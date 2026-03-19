"""Additional integration tests for decision-path combinations."""

from moneypoly.moneypoly.moneypoly.config import GO_SALARY, JAIL_FINE
from moneypoly.moneypoly.moneypoly.game import Game


def test_integration_play_turn_jail_branch_advances_turn(monkeypatch):
    game = Game(["Alice", "Bob"])
    game.players[0].in_jail = True

    called = {"jail": 0}
    monkeypatch.setattr(game, "_handle_jail_turn", lambda _p: called.__setitem__("jail", called["jail"] + 1))

    game.play_turn()

    assert called["jail"] == 1
    assert game.current_player().name == "Bob"


def test_integration_play_turn_three_doubles_sends_to_jail(monkeypatch):
    game = Game(["Alice", "Bob"])
    player = game.players[0]
    game.dice.doubles_streak = 2

    def fake_roll():
        game.dice.doubles_streak += 1
        return 7

    monkeypatch.setattr(game.dice, "roll", fake_roll)
    monkeypatch.setattr(game.dice, "describe", lambda: "3 + 4 = 7")
    monkeypatch.setattr(game.dice, "is_doubles", lambda: True)

    game.play_turn()

    assert player.in_jail is True
    assert game.current_player().name == "Bob"


def test_integration_auction_rejects_low_increment_bid(monkeypatch):
    game = Game(["Alice", "Bob"])
    prop = game.board.get_property_at(3)
    assert prop is not None

    # First bid sets high=50, second bid 51 should be rejected (< min increment of 10).
    bids = iter([50, 51])
    monkeypatch.setattr("moneypoly.moneypoly.moneypoly.ui.safe_int_input", lambda *_a, **_k: next(bids))

    game.auction_property(prop)

    assert prop.owner is game.players[0]


def test_integration_auction_rejects_bid_above_balance(monkeypatch):
    game = Game(["Alice", "Bob"])
    prop = game.board.get_property_at(3)
    assert prop is not None

    game.players[0].balance = 40
    bids = iter([100, 0])
    monkeypatch.setattr("moneypoly.moneypoly.moneypoly.ui.safe_int_input", lambda *_a, **_k: next(bids))

    game.auction_property(prop)

    assert prop.owner is None


def test_integration_card_jail_action_sets_player_jail_state():
    game = Game(["Alice", "Bob"])
    player = game.players[0]
    card = {"description": "Go to jail", "action": "jail", "value": 0}

    game._apply_card(player, card)
    assert player.in_jail is True


def test_integration_card_jail_free_action_increments_card_count():
    game = Game(["Alice", "Bob"])
    player = game.players[0]
    before = player.get_out_of_jail_cards
    card = {"description": "Free", "action": "jail_free", "value": 0}

    game._apply_card(player, card)

    assert player.get_out_of_jail_cards == before + 1


def test_integration_card_collect_from_all_skips_collector_and_low_balance_players():
    game = Game(["Alice", "Bob", "Cara"])
    collector = game.players[0]
    donor_1 = game.players[1]
    donor_2 = game.players[2]
    donor_1.balance = 20
    donor_2.balance = 5

    before_collector = collector.balance
    game._card_collect_from_others(collector, 10)

    assert collector.balance == before_collector + 10
    assert donor_1.balance == 10
    assert donor_2.balance == 5


def test_integration_card_move_to_property_skip_branch(monkeypatch):
    game = Game(["Alice", "Bob"])
    player = game.players[0]
    player.position = 39

    monkeypatch.setattr("builtins.input", lambda _q: "s")
    game._card_move_to(player, 1)

    assert player.position == 1


def test_integration_jail_mandatory_release_after_three_turns(monkeypatch):
    game = Game(["Alice", "Bob"])
    player = game.players[0]
    player.go_to_jail()
    player.jail_turns = 2

    monkeypatch.setattr("moneypoly.moneypoly.moneypoly.ui.confirm", lambda _q: False)
    monkeypatch.setattr(game.dice, "roll", lambda: 4)
    monkeypatch.setattr(game.dice, "describe", lambda: "2 + 2 = 4")
    monkeypatch.setattr(game, "_move_and_resolve", lambda *_a, **_k: None)

    before = player.balance
    game._handle_jail_turn(player)

    assert player.in_jail is False
    assert player.balance == before - JAIL_FINE


def test_integration_run_loop_calls_play_turn_until_limit(monkeypatch):
    game = Game(["Alice", "Bob"])

    monkeypatch.setattr("moneypoly.moneypoly.moneypoly.ui.print_banner", lambda *_a, **_k: None)
    monkeypatch.setattr("moneypoly.moneypoly.moneypoly.ui.print_standings", lambda *_a, **_k: None)

    call_count = {"n": 0}

    def fake_play_turn():
        call_count["n"] += 1
        # Advance manually and end quickly.
        game.turn_number += 1
        if call_count["n"] >= 2:
            game.players = [game.players[0]]

    monkeypatch.setattr(game, "play_turn", fake_play_turn)

    game.run()
    assert call_count["n"] == 2


def test_integration_card_move_to_go_tile_collects_salary_without_prompt():
    game = Game(["Alice", "Bob"])
    player = game.players[0]
    player.position = 39
    before = player.balance

    # Move to Go (position 0), which should not enter property-choice prompt.
    game._card_move_to(player, 0)

    assert player.position == 0
    assert player.balance == before + GO_SALARY
