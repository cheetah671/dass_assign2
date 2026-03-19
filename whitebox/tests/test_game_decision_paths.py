"""Additional unit tests for uncovered game decision paths."""

from moneypoly.moneypoly.moneypoly.game import Game


def test_handle_property_tile_unowned_buy_branch(monkeypatch):
    game = Game(["Alice", "Bob"])
    player = game.players[0]
    prop = game.board.get_property_at(1)
    assert prop is not None
    prop.owner = None

    called = {"buy": 0}
    monkeypatch.setattr("builtins.input", lambda _q: "b")
    monkeypatch.setattr(game, "buy_property", lambda _p, _prop: called.__setitem__("buy", called["buy"] + 1))

    game._handle_property_tile(player, prop)
    assert called["buy"] == 1


def test_handle_property_tile_unowned_auction_branch(monkeypatch):
    game = Game(["Alice", "Bob"])
    player = game.players[0]
    prop = game.board.get_property_at(1)
    assert prop is not None
    prop.owner = None

    called = {"auction": 0}
    monkeypatch.setattr("builtins.input", lambda _q: "a")
    monkeypatch.setattr(game, "auction_property", lambda _prop: called.__setitem__("auction", called["auction"] + 1))

    game._handle_property_tile(player, prop)
    assert called["auction"] == 1


def test_handle_property_tile_unowned_skip_branch(monkeypatch):
    game = Game(["Alice", "Bob"])
    player = game.players[0]
    prop = game.board.get_property_at(1)
    assert prop is not None
    prop.owner = None

    called = {"buy": 0, "auction": 0}
    monkeypatch.setattr("builtins.input", lambda _q: "s")
    monkeypatch.setattr(game, "buy_property", lambda *_a, **_k: called.__setitem__("buy", called["buy"] + 1))
    monkeypatch.setattr(game, "auction_property", lambda *_a, **_k: called.__setitem__("auction", called["auction"] + 1))

    game._handle_property_tile(player, prop)
    assert called["buy"] == 0
    assert called["auction"] == 0


def test_handle_property_tile_owned_by_self_no_rent(monkeypatch):
    game = Game(["Alice", "Bob"])
    player = game.players[0]
    prop = game.board.get_property_at(1)
    assert prop is not None
    prop.owner = player

    called = {"rent": 0}
    monkeypatch.setattr(game, "pay_rent", lambda *_a, **_k: called.__setitem__("rent", called["rent"] + 1))

    game._handle_property_tile(player, prop)
    assert called["rent"] == 0


def test_handle_property_tile_owned_by_other_calls_pay_rent(monkeypatch):
    game = Game(["Alice", "Bob"])
    player = game.players[0]
    owner = game.players[1]
    prop = game.board.get_property_at(1)
    assert prop is not None
    prop.owner = owner

    called = {"rent": 0}
    monkeypatch.setattr(game, "pay_rent", lambda *_a, **_k: called.__setitem__("rent", called["rent"] + 1))

    game._handle_property_tile(player, prop)
    assert called["rent"] == 1


def test_move_and_resolve_property_tile_with_missing_property_does_not_call_handler(monkeypatch):
    game = Game(["Alice", "Bob"])
    player = game.players[0]

    monkeypatch.setattr(player, "move", lambda _steps: None)
    player.position = 12
    monkeypatch.setattr(game.board, "get_tile_type", lambda _pos: "property")
    monkeypatch.setattr(game.board, "get_property_at", lambda _pos: None)

    called = {"property_handler": 0, "bankruptcy": 0}
    monkeypatch.setattr(game, "_handle_property_tile", lambda *_a, **_k: called.__setitem__("property_handler", called["property_handler"] + 1))
    monkeypatch.setattr(game, "_check_bankruptcy", lambda _p: called.__setitem__("bankruptcy", called["bankruptcy"] + 1))

    game._move_and_resolve(player, 3)
    assert called["property_handler"] == 0
    assert called["bankruptcy"] == 1


def test_move_and_resolve_railroad_with_property_calls_property_handler(monkeypatch):
    game = Game(["Alice", "Bob"])
    player = game.players[0]
    rr_prop = game.board.get_property_at(6)
    assert rr_prop is not None

    monkeypatch.setattr(player, "move", lambda _steps: None)
    player.position = 5
    monkeypatch.setattr(game.board, "get_tile_type", lambda _pos: "railroad")
    monkeypatch.setattr(game.board, "get_property_at", lambda _pos: rr_prop)

    called = {"property_handler": 0}
    monkeypatch.setattr(game, "_handle_property_tile", lambda *_a, **_k: called.__setitem__("property_handler", called["property_handler"] + 1))
    monkeypatch.setattr(game, "_check_bankruptcy", lambda _p: None)

    game._move_and_resolve(player, 4)
    assert called["property_handler"] == 1


def test_draw_and_apply_uses_selected_deck(monkeypatch):
    game = Game(["Alice", "Bob"])
    player = game.players[0]

    class FakeDeck:
        def __init__(self):
            self.calls = 0

        def draw(self):
            self.calls += 1
            return {"description": "Pay", "action": "pay", "value": 10}

    fake = FakeDeck()
    game.decks["chance"] = fake
    called = {"apply": 0}
    monkeypatch.setattr(game, "_apply_card", lambda _p, _c: called.__setitem__("apply", called["apply"] + 1))

    game._draw_and_apply(player, "chance")
    assert fake.calls == 1
    assert called["apply"] == 1


def test_apply_card_birthday_alias_calls_collect_from_others(monkeypatch):
    game = Game(["Alice", "Bob"])
    player = game.players[0]
    card = {"description": "Birthday", "action": "birthday", "value": 10}

    called = {"collect": 0}
    monkeypatch.setattr(game, "_card_collect_from_others", lambda _p, _v: called.__setitem__("collect", called["collect"] + 1))

    game._apply_card(player, card)
    assert called["collect"] == 1


def test_handle_jail_turn_decline_all_increments_jail_turn(monkeypatch):
    game = Game(["Alice", "Bob"])
    player = game.players[0]
    player.in_jail = True
    player.jail_turns = 0

    monkeypatch.setattr("moneypoly.moneypoly.moneypoly.ui.confirm", lambda _q: False)

    game._handle_jail_turn(player)
    assert player.in_jail is True
    assert player.jail_turns == 1


def test_handle_jail_turn_pays_fine_path_resets_jail(monkeypatch):
    game = Game(["Alice", "Bob"])
    player = game.players[0]
    player.in_jail = True
    player.jail_turns = 1

    monkeypatch.setattr("moneypoly.moneypoly.moneypoly.ui.confirm", lambda _q: True)
    monkeypatch.setattr(game.dice, "roll", lambda: 5)
    monkeypatch.setattr(game.dice, "describe", lambda: "2 + 3 = 5")
    monkeypatch.setattr(game, "_move_and_resolve", lambda *_a, **_k: None)

    game._handle_jail_turn(player)
    assert player.in_jail is False
    assert player.jail_turns == 0


def test_interactive_menu_invalid_choice_then_roll_exits(monkeypatch):
    game = Game(["Alice", "Bob"])
    player = game.players[0]
    choices = iter([99, 0])

    monkeypatch.setattr("moneypoly.moneypoly.moneypoly.ui.safe_int_input", lambda *_a, **_k: next(choices))

    game.interactive_menu(player)


def test_menu_trade_no_other_players_returns_without_error():
    game = Game(["Alice"])
    player = game.players[0]
    game._menu_trade(player)


def test_menu_trade_current_player_has_no_properties_returns(monkeypatch):
    game = Game(["Alice", "Bob"])
    player = game.players[0]
    monkeypatch.setattr("moneypoly.moneypoly.moneypoly.ui.safe_int_input", lambda *_a, **_k: 1)

    game._menu_trade(player)
    assert player.properties == []
