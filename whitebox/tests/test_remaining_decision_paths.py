"""Targeted tests for remaining uncovered decision paths."""

from moneypoly.moneypoly.moneypoly.game import Game
from moneypoly.moneypoly.moneypoly.player import Player
from moneypoly.moneypoly.moneypoly.property import Property, PropertyGroup
from moneypoly.moneypoly.moneypoly import ui


def test_move_and_resolve_non_action_tile_still_runs_bankruptcy_check(monkeypatch):
    game = Game(["Alice", "Bob"])
    player = game.players[0]

    monkeypatch.setattr(player, "move", lambda _steps: None)
    player.position = 8
    monkeypatch.setattr(game.board, "get_tile_type", lambda _pos: "plain")

    called = {"bankruptcy": 0}
    monkeypatch.setattr(game, "_check_bankruptcy", lambda _p: called.__setitem__("bankruptcy", called["bankruptcy"] + 1))

    game._move_and_resolve(player, 2)
    assert called["bankruptcy"] == 1


def test_tile_handlers_direct_paths_cover_jail_income_luxury_and_free_parking(capsys):
    game = Game(["Alice", "Bob"])
    player = game.players[0]
    start_bank = game.bank.get_balance()

    game._handle_go_to_jail_tile(player)
    assert player.in_jail is True

    before_tax = player.balance
    game._handle_income_tax_tile(player)
    assert player.balance < before_tax

    before_luxury = player.balance
    game._handle_luxury_tax_tile(player)
    assert player.balance < before_luxury
    assert game.bank.get_balance() > start_bank

    game._handle_free_parking_tile(player)
    out = capsys.readouterr().out
    assert "Free Parking" in out


def test_mortgage_property_rejects_already_mortgaged_property():
    game = Game(["Alice", "Bob"])
    player = game.players[0]
    prop = game.board.get_property_at(1)
    assert prop is not None

    assert game.buy_property(player, prop) is True
    assert game.mortgage_property(player, prop) is True
    assert game.mortgage_property(player, prop) is False


def test_mortgage_property_rejects_when_bank_cannot_pay():
    game = Game(["Alice", "Bob"])
    player = game.players[0]
    prop = game.board.get_property_at(1)
    assert prop is not None

    assert game.buy_property(player, prop) is True
    game.bank._funds = 0
    assert game.mortgage_property(player, prop) is False
    assert prop.is_mortgaged is False


def test_unmortgage_property_not_owner_and_not_mortgaged_branches():
    game = Game(["Alice", "Bob"])
    owner, other = game.players
    prop = game.board.get_property_at(1)
    assert prop is not None

    assert game.buy_property(owner, prop) is True
    assert game.unmortgage_property(other, prop) is False
    assert game.unmortgage_property(owner, prop) is False


def test_handle_jail_turn_decline_card_then_pay_fine_branch(monkeypatch):
    game = Game(["Alice", "Bob"])
    player = game.players[0]
    player.in_jail = True
    player.get_out_of_jail_cards = 1

    answers = iter([False, True])
    monkeypatch.setattr("moneypoly.moneypoly.moneypoly.ui.confirm", lambda _q: next(answers))
    monkeypatch.setattr(game.dice, "roll", lambda: 4)
    monkeypatch.setattr(game.dice, "describe", lambda: "2 + 2 = 4")
    monkeypatch.setattr(game, "_move_and_resolve", lambda *_a, **_k: None)

    game._handle_jail_turn(player)
    assert player.in_jail is False
    assert player.jail_turns == 0


def test_card_move_to_property_tile_with_missing_property_no_handler_call(monkeypatch):
    game = Game(["Alice", "Bob"])
    player = game.players[0]

    monkeypatch.setattr(game.board, "get_tile_type", lambda _pos: "property")
    monkeypatch.setattr(game.board, "get_property_at", lambda _pos: None)

    called = {"property_handler": 0}
    monkeypatch.setattr(game, "_handle_property_tile", lambda *_a, **_k: called.__setitem__("property_handler", called["property_handler"] + 1))

    game._card_move_to(player, 3)
    assert called["property_handler"] == 0


def test_run_handles_no_players_left_branch(monkeypatch, capsys):
    game = Game(["Alice", "Bob"])
    game.players = []

    monkeypatch.setattr("moneypoly.moneypoly.moneypoly.ui.print_banner", lambda *_a, **_k: None)
    monkeypatch.setattr("moneypoly.moneypoly.moneypoly.ui.print_standings", lambda *_a, **_k: None)

    game.run()
    out = capsys.readouterr().out
    assert "no players remaining" in out


def test_interactive_menu_routes_each_choice_once(monkeypatch):
    game = Game(["Alice", "Bob"])
    player = game.players[0]

    choices = iter([1, 2, 3, 4, 5, 6, 250, 0])
    monkeypatch.setattr("moneypoly.moneypoly.moneypoly.ui.safe_int_input", lambda *_a, **_k: next(choices))

    called = {"standings": 0, "board": 0, "mortgage": 0, "unmortgage": 0, "trade": 0, "loan": 0}
    monkeypatch.setattr("moneypoly.moneypoly.moneypoly.ui.print_standings", lambda *_a, **_k: called.__setitem__("standings", called["standings"] + 1))
    monkeypatch.setattr("moneypoly.moneypoly.moneypoly.ui.print_board_ownership", lambda *_a, **_k: called.__setitem__("board", called["board"] + 1))
    monkeypatch.setattr(game, "_menu_mortgage", lambda _p: called.__setitem__("mortgage", called["mortgage"] + 1))
    monkeypatch.setattr(game, "_menu_unmortgage", lambda _p: called.__setitem__("unmortgage", called["unmortgage"] + 1))
    monkeypatch.setattr(game, "_menu_trade", lambda _p: called.__setitem__("trade", called["trade"] + 1))
    monkeypatch.setattr(game.bank, "give_loan", lambda *_a, **_k: called.__setitem__("loan", called["loan"] + 1))

    game.interactive_menu(player)

    assert called == {
        "standings": 1,
        "board": 1,
        "mortgage": 1,
        "unmortgage": 1,
        "trade": 1,
        "loan": 1,
    }


def test_menu_mortgage_valid_selection_calls_mortgage_property(monkeypatch):
    game = Game(["Alice", "Bob"])
    player = game.players[0]
    prop = game.board.get_property_at(1)
    assert prop is not None

    assert game.buy_property(player, prop) is True
    monkeypatch.setattr("moneypoly.moneypoly.moneypoly.ui.safe_int_input", lambda *_a, **_k: 1)

    called = {"mortgage": 0}
    monkeypatch.setattr(game, "mortgage_property", lambda _p, _prop: called.__setitem__("mortgage", called["mortgage"] + 1))

    game._menu_mortgage(player)
    assert called["mortgage"] == 1


def test_menu_unmortgage_valid_selection_calls_unmortgage_property(monkeypatch):
    game = Game(["Alice", "Bob"])
    player = game.players[0]
    prop = game.board.get_property_at(1)
    assert prop is not None

    assert game.buy_property(player, prop) is True
    assert game.mortgage_property(player, prop) is True
    monkeypatch.setattr("moneypoly.moneypoly.moneypoly.ui.safe_int_input", lambda *_a, **_k: 1)

    called = {"unmortgage": 0}
    monkeypatch.setattr(game, "unmortgage_property", lambda _p, _prop: called.__setitem__("unmortgage", called["unmortgage"] + 1))

    game._menu_unmortgage(player)
    assert called["unmortgage"] == 1


def test_menu_trade_valid_path_calls_trade(monkeypatch):
    game = Game(["Alice", "Bob"])
    seller, _buyer = game.players
    prop = game.board.get_property_at(1)
    assert prop is not None

    assert game.buy_property(seller, prop) is True
    inputs = iter([1, 1, 175])
    monkeypatch.setattr("moneypoly.moneypoly.moneypoly.ui.safe_int_input", lambda *_a, **_k: next(inputs))

    called = {"trade": 0, "cash": None}

    def fake_trade(_seller, _partner, _prop, cash):
        called["trade"] += 1
        called["cash"] = cash
        return True

    monkeypatch.setattr(game, "trade", fake_trade)

    game._menu_trade(seller)
    assert called["trade"] == 1
    assert called["cash"] == 175


def test_check_bankruptcy_player_not_in_active_list_keeps_index_valid():
    game = Game(["Alice", "Bob"])
    ghost = Player("Ghost", balance=0)
    game.current_index = 1

    game._check_bankruptcy(ghost)

    assert game.current_index == 1


def test_run_skips_loop_when_turn_limit_already_reached(monkeypatch, capsys):
    game = Game(["Alice", "Bob"])
    game.turn_number = 1000

    called = {"play_turn": 0, "standings": 0}
    monkeypatch.setattr(game, "play_turn", lambda: called.__setitem__("play_turn", called["play_turn"] + 1))
    monkeypatch.setattr("moneypoly.moneypoly.moneypoly.ui.print_standings", lambda *_a, **_k: called.__setitem__("standings", called["standings"] + 1))
    monkeypatch.setattr("moneypoly.moneypoly.moneypoly.ui.print_banner", lambda *_a, **_k: None)

    game.run()

    assert called["play_turn"] == 0
    assert called["standings"] == 0
    assert "wins with a net worth" in capsys.readouterr().out


def test_menu_mortgage_no_mortgageable_properties_returns():
    game = Game(["Alice", "Bob"])
    player = game.players[0]

    game._menu_mortgage(player)
    assert player.properties == []


def test_menu_mortgage_invalid_selection_does_not_call_mortgage(monkeypatch):
    game = Game(["Alice", "Bob"])
    player = game.players[0]
    prop = game.board.get_property_at(1)
    assert prop is not None
    assert game.buy_property(player, prop) is True

    monkeypatch.setattr("moneypoly.moneypoly.moneypoly.ui.safe_int_input", lambda *_a, **_k: 0)
    called = {"mortgage": 0}
    monkeypatch.setattr(game, "mortgage_property", lambda *_a, **_k: called.__setitem__("mortgage", called["mortgage"] + 1))

    game._menu_mortgage(player)
    assert called["mortgage"] == 0


def test_menu_unmortgage_no_mortgaged_properties_returns():
    game = Game(["Alice", "Bob"])
    player = game.players[0]

    game._menu_unmortgage(player)
    assert player.properties == []


def test_menu_unmortgage_invalid_selection_does_not_call_unmortgage(monkeypatch):
    game = Game(["Alice", "Bob"])
    player = game.players[0]
    prop = game.board.get_property_at(1)
    assert prop is not None
    assert game.buy_property(player, prop) is True
    assert game.mortgage_property(player, prop) is True

    monkeypatch.setattr("moneypoly.moneypoly.moneypoly.ui.safe_int_input", lambda *_a, **_k: 0)
    called = {"unmortgage": 0}
    monkeypatch.setattr(game, "unmortgage_property", lambda *_a, **_k: called.__setitem__("unmortgage", called["unmortgage"] + 1))

    game._menu_unmortgage(player)
    assert called["unmortgage"] == 0


def test_menu_trade_invalid_property_selection_returns_without_trade(monkeypatch):
    game = Game(["Alice", "Bob"])
    seller, _buyer = game.players
    prop = game.board.get_property_at(1)
    assert prop is not None
    assert game.buy_property(seller, prop) is True

    # valid partner selection, invalid property selection
    choices = iter([1, 999])
    monkeypatch.setattr("moneypoly.moneypoly.moneypoly.ui.safe_int_input", lambda *_a, **_k: next(choices))
    called = {"trade": 0}
    monkeypatch.setattr(game, "trade", lambda *_a, **_k: called.__setitem__("trade", called["trade"] + 1))

    game._menu_trade(seller)
    assert called["trade"] == 0


def test_player_remove_property_noop_when_absent_and_repr_covered():
    player = Player("Alice")
    player.remove_property("missing")
    assert player.count_properties() == 0
    assert "Player('Alice'" in repr(player)


def test_property_repr_group_duplicate_add_and_owner_counts_branches():
    prop1 = Property("Test One", 1, 100, 10)
    prop2 = Property("Test Two", 2, 120, 12)
    group = PropertyGroup("Test Group", "blue")

    group.add_property(prop1)
    group.add_property(prop1)
    group.add_property(prop2)

    owner = Player("Owner")
    prop1.owner = owner

    owner_counts = group.get_owner_counts()
    assert owner_counts[owner] == 1
    assert "owner='unowned'" in repr(prop2)
    assert "owner='Owner'" in repr(prop1)
    assert "PropertyGroup('Test Group'" in repr(group)


def test_ui_helpers_cover_print_and_input_branches(monkeypatch, capsys):
    player = Player("Alice", balance=1500)
    prop = Property("Boardwalk", 39, 400, 50)

    ui.print_banner("Demo")

    ui.print_player_card(player)

    player.in_jail = True
    player.jail_turns = 2
    player.get_out_of_jail_cards = 1
    player.add_property(prop)
    prop.owner = player
    prop.is_mortgaged = True
    ui.print_player_card(player)

    other = Player("Bob", balance=1000)
    ui.print_standings([player, other])

    class FakeBoard:
        properties = [prop]

    ui.print_board_ownership(FakeBoard())

    assert ui.format_currency(1234567) == "$1,234,567"

    answers = iter(["42", "oops", "y", "N"])
    monkeypatch.setattr("builtins.input", lambda _p: next(answers))
    assert ui.safe_int_input("n?", default=0) == 42
    assert ui.safe_int_input("n?", default=7) == 7
    assert ui.confirm("ok?") is True
    assert ui.confirm("ok?") is False

    out = capsys.readouterr().out
    assert "Player" in out
    assert "Property Register" in out
