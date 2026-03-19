"""White-box tests for game.py decision paths."""

from types import SimpleNamespace

import pytest

from moneypoly.moneypoly.moneypoly.config import GO_SALARY
from moneypoly.moneypoly.moneypoly.game import Game
from moneypoly.moneypoly.moneypoly.player import Player


def test_current_player_returns_indexed_player(game_two_players):
    assert game_two_players.current_player().name == "Alice"


def test_advance_turn_rotates_and_increments_counter(game_two_players):
    game_two_players.advance_turn()
    assert game_two_players.current_player().name == "Bob"
    assert game_two_players.turn_number == 1


def test_play_turn_jail_path_advances_turn(monkeypatch, game_two_players):
    player = game_two_players.current_player()
    player.in_jail = True
    called = {"jail": False}

    def fake_handle(p):
        called["jail"] = True
        assert p is player

    monkeypatch.setattr(game_two_players, "_handle_jail_turn", fake_handle)
    game_two_players.play_turn()

    assert called["jail"] is True
    assert game_two_players.current_player().name == "Bob"


def test_play_turn_three_doubles_sends_player_to_jail(monkeypatch, game_two_players):
    player = game_two_players.current_player()
    game_two_players.dice.doubles_streak = 2

    def fake_roll():
        # Mirror Dice.roll side effect: doubles streak increments before game checks jail rule.
        game_two_players.dice.doubles_streak += 1
        return 7

    monkeypatch.setattr(game_two_players.dice, "roll", fake_roll)
    monkeypatch.setattr(game_two_players.dice, "describe", lambda: "3 + 4 = 7")
    monkeypatch.setattr(game_two_players.dice, "is_doubles", lambda: True)

    game_two_players.play_turn()

    assert player.in_jail is True


def test_play_turn_doubles_grants_extra_turn(monkeypatch, game_two_players):
    start_name = game_two_players.current_player().name
    monkeypatch.setattr(game_two_players.dice, "roll", lambda: 6)
    monkeypatch.setattr(game_two_players.dice, "describe", lambda: "3 + 3 = 6")
    game_two_players.dice.doubles_streak = 0
    monkeypatch.setattr(game_two_players.dice, "is_doubles", lambda: True)
    monkeypatch.setattr(game_two_players, "_move_and_resolve", lambda _p, _s: None)

    game_two_players.play_turn()
    assert game_two_players.current_player().name == start_name


def test_play_turn_non_doubles_advances_turn(monkeypatch, game_two_players):
    monkeypatch.setattr(game_two_players.dice, "roll", lambda: 5)
    monkeypatch.setattr(game_two_players.dice, "describe", lambda: "2 + 3 = 5")
    monkeypatch.setattr(game_two_players.dice, "is_doubles", lambda: False)
    game_two_players.dice.doubles_streak = 0
    monkeypatch.setattr(game_two_players, "_move_and_resolve", lambda _p, _s: None)

    game_two_players.play_turn()
    assert game_two_players.current_player().name == "Bob"


@pytest.mark.parametrize(
    "tile_name,expected",
    [
        ("go_to_jail", "jail"),
        ("income_tax", "income"),
        ("luxury_tax", "luxury"),
        ("free_parking", "parking"),
        ("chance", "chance"),
        ("community_chest", "chest"),
    ],
)
def test_move_and_resolve_dispatches_tile_handlers(monkeypatch, game_two_players, tile_name, expected):
    player = game_two_players.current_player()
    marks = {"jail": 0, "income": 0, "luxury": 0, "parking": 0, "chance": 0, "chest": 0}

    monkeypatch.setattr(player, "move", lambda _steps: None)
    player.position = 10

    monkeypatch.setattr(game_two_players.board, "get_tile_type", lambda _p: tile_name)
    monkeypatch.setattr(game_two_players, "_handle_go_to_jail_tile", lambda _p: marks.__setitem__("jail", marks["jail"] + 1))
    monkeypatch.setattr(game_two_players, "_handle_income_tax_tile", lambda _p: marks.__setitem__("income", marks["income"] + 1))
    monkeypatch.setattr(game_two_players, "_handle_luxury_tax_tile", lambda _p: marks.__setitem__("luxury", marks["luxury"] + 1))
    monkeypatch.setattr(game_two_players, "_handle_free_parking_tile", lambda _p: marks.__setitem__("parking", marks["parking"] + 1))
    monkeypatch.setattr(game_two_players, "_draw_and_apply", lambda _p, d: marks.__setitem__("chance" if d == "chance" else "chest", 1))
    monkeypatch.setattr(game_two_players, "_check_bankruptcy", lambda _p: None)

    game_two_players._move_and_resolve(player, 4)
    assert marks[expected] >= 1


def test_move_and_resolve_property_path_calls_property_handler(monkeypatch, game_two_players):
    player = game_two_players.current_player()
    prop = game_two_players.board.properties[0]

    monkeypatch.setattr(player, "move", lambda _steps: None)
    player.position = prop.position
    monkeypatch.setattr(game_two_players.board, "get_tile_type", lambda _p: "property")
    monkeypatch.setattr(game_two_players.board, "get_property_at", lambda _p: prop)

    called = {"ok": False}

    def fake_handler(_player, _prop):
        called["ok"] = True

    monkeypatch.setattr(game_two_players, "_handle_property_tile", fake_handler)
    monkeypatch.setattr(game_two_players, "_check_bankruptcy", lambda _p: None)

    game_two_players._move_and_resolve(player, 2)
    assert called["ok"] is True


def test_buy_property_succeeds_when_balance_equals_price(game_two_players):
    player = game_two_players.current_player()
    prop = game_two_players.board.properties[0]
    player.balance = prop.price

    assert game_two_players.buy_property(player, prop) is True
    assert prop.owner is player


def test_buy_property_fails_when_balance_less_than_price(game_two_players):
    player = game_two_players.current_player()
    prop = game_two_players.board.properties[0]
    player.balance = prop.price - 1

    assert game_two_players.buy_property(player, prop) is False
    assert prop.owner is None


def test_pay_rent_noop_when_mortgaged(game_two_players):
    tenant = game_two_players.players[0]
    owner = game_two_players.players[1]
    prop = game_two_players.board.properties[0]
    prop.owner = owner
    prop.is_mortgaged = True
    before = tenant.balance

    game_two_players.pay_rent(tenant, prop)
    assert tenant.balance == before


def test_pay_rent_noop_when_unowned(game_two_players):
    tenant = game_two_players.players[0]
    prop = game_two_players.board.properties[0]
    before = tenant.balance

    game_two_players.pay_rent(tenant, prop)
    assert tenant.balance == before


def test_mortgage_property_owner_only(game_two_players):
    p1, p2 = game_two_players.players
    prop = game_two_players.board.properties[0]
    prop.owner = p2

    assert game_two_players.mortgage_property(p1, prop) is False


def test_unmortgage_property_checks_balance(game_two_players):
    p1 = game_two_players.players[0]
    prop = game_two_players.board.properties[0]
    prop.owner = p1
    prop.mortgage()
    p1.balance = 0

    assert game_two_players.unmortgage_property(p1, prop) is False


def test_trade_successful_path(game_two_players):
    seller, buyer = game_two_players.players
    prop = game_two_players.board.properties[0]
    prop.owner = seller
    seller.add_property(prop)

    ok = game_two_players.trade(seller, buyer, prop, 100)
    assert ok is True
    assert prop.owner is buyer


def test_trade_fails_if_seller_not_owner(game_two_players):
    seller, buyer = game_two_players.players
    prop = game_two_players.board.properties[0]
    prop.owner = buyer

    assert game_two_players.trade(seller, buyer, prop, 10) is False


def test_auction_no_bids_keeps_property_unowned(monkeypatch, game_two_players):
    prop = game_two_players.board.properties[0]
    monkeypatch.setattr("moneypoly.moneypoly.moneypoly.ui.safe_int_input", lambda *_a, **_k: 0)

    game_two_players.auction_property(prop)
    assert prop.owner is None


def test_auction_valid_bid_assigns_owner(monkeypatch, game_two_players):
    prop = game_two_players.board.properties[0]
    bids = iter([50, 0])
    monkeypatch.setattr("moneypoly.moneypoly.moneypoly.ui.safe_int_input", lambda *_a, **_k: next(bids))

    game_two_players.auction_property(prop)
    assert prop.owner is game_two_players.players[0]


def test_check_bankruptcy_removes_bankrupt_player(game_two_players):
    player = game_two_players.players[0]
    player.balance = 0
    game_two_players._check_bankruptcy(player)
    assert player not in game_two_players.players


def test_find_winner_returns_highest_net_worth_player(game_two_players):
    game_two_players.players[0].balance = 10
    game_two_players.players[1].balance = 20
    winner = game_two_players.find_winner()
    assert winner is game_two_players.players[1]


def test_find_winner_none_when_no_players(game_two_players):
    game_two_players.players.clear()
    assert game_two_players.find_winner() is None


def test_apply_card_collect_increases_balance(game_two_players):
    player = game_two_players.players[0]
    before = player.balance
    card = {"description": "Collect", "action": "collect", "value": 50}
    game_two_players._apply_card(player, card)
    assert player.balance == before + 50


def test_apply_card_pay_decreases_balance(game_two_players):
    player = game_two_players.players[0]
    before = player.balance
    card = {"description": "Pay", "action": "pay", "value": 25}
    game_two_players._apply_card(player, card)
    assert player.balance == before - 25


def test_apply_card_jail_sets_jail_state(game_two_players):
    player = game_two_players.players[0]
    card = {"description": "Jail", "action": "jail", "value": 0}
    game_two_players._apply_card(player, card)
    assert player.in_jail is True


def test_apply_card_jail_free_increments_counter(game_two_players):
    player = game_two_players.players[0]
    card = {"description": "Free", "action": "jail_free", "value": 0}
    game_two_players._apply_card(player, card)
    assert player.get_out_of_jail_cards == 1


def test_apply_card_move_to_passes_go_collects_salary(monkeypatch, game_two_players):
    player = game_two_players.players[0]
    player.position = 39
    before = player.balance
    card = {"description": "Go", "action": "move_to", "value": 2}

    monkeypatch.setattr(game_two_players.board, "get_tile_type", lambda _p: "blank")
    game_two_players._apply_card(player, card)
    assert player.balance == before + GO_SALARY


def test_apply_card_collect_from_all_transfers_only_from_players_with_enough_balance(game_two_players):
    collector = game_two_players.players[0]
    other = game_two_players.players[1]
    other.balance = 5
    before = collector.balance
    card = {"description": "Collect", "action": "collect_from_all", "value": 10}
    game_two_players._apply_card(collector, card)
    assert collector.balance == before


def test_apply_card_unknown_action_is_noop(game_two_players):
    player = game_two_players.players[0]
    before = player.balance
    card = {"description": "Unknown", "action": "noop", "value": 999}
    game_two_players._apply_card(player, card)
    assert player.balance == before


def test_handle_jail_turn_uses_card_path(monkeypatch, game_two_players):
    player = game_two_players.players[0]
    player.in_jail = True
    player.get_out_of_jail_cards = 1

    monkeypatch.setattr("moneypoly.moneypoly.moneypoly.ui.confirm", lambda _p: True)
    monkeypatch.setattr(game_two_players.dice, "roll", lambda: 4)
    monkeypatch.setattr(game_two_players.dice, "describe", lambda: "2 + 2 = 4")
    monkeypatch.setattr(game_two_players, "_move_and_resolve", lambda _p, _r: None)

    game_two_players._handle_jail_turn(player)
    assert player.in_jail is False


def test_handle_jail_turn_mandatory_release_after_third_turn(monkeypatch, game_two_players):
    player = game_two_players.players[0]
    player.in_jail = True
    player.jail_turns = 2

    monkeypatch.setattr("moneypoly.moneypoly.moneypoly.ui.confirm", lambda _p: False)
    monkeypatch.setattr(game_two_players.dice, "roll", lambda: 3)
    monkeypatch.setattr(game_two_players.dice, "describe", lambda: "1 + 2 = 3")
    monkeypatch.setattr(game_two_players, "_move_and_resolve", lambda _p, _r: None)

    game_two_players._handle_jail_turn(player)
    assert player.in_jail is False


def test_menu_trade_returns_when_invalid_partner(monkeypatch, game_two_players):
    player = game_two_players.players[0]
    monkeypatch.setattr("moneypoly.moneypoly.moneypoly.ui.safe_int_input", lambda *_a, **_k: 999)
    game_two_players._menu_trade(player)


def test_interactive_menu_breaks_on_zero(monkeypatch, game_two_players):
    player = game_two_players.players[0]
    monkeypatch.setattr("moneypoly.moneypoly.moneypoly.ui.safe_int_input", lambda *_a, **_k: 0)
    game_two_players.interactive_menu(player)


def test_run_terminates_when_one_player_left(monkeypatch, game_two_players):
    game_two_players.players = [game_two_players.players[0]]
    monkeypatch.setattr("moneypoly.moneypoly.moneypoly.ui.print_banner", lambda *_a, **_k: None)
    monkeypatch.setattr("moneypoly.moneypoly.moneypoly.ui.print_standings", lambda *_a, **_k: None)
    game_two_players.run()
