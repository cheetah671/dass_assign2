"""Integration-phase tests across MoneyPoly modules."""

import pytest

from moneypoly.moneypoly.moneypoly.config import GO_SALARY, JAIL_FINE
from moneypoly.moneypoly.moneypoly.game import Game


def test_integration_bank_loan_updates_player_and_bank_balance():
    game = Game(["Alice", "Bob"])
    player = game.players[0]
    bank_before = game.bank.get_balance()
    player_before = player.balance

    game.bank.give_loan(player, 200)

    assert player.balance == player_before + 200
    assert game.bank.get_balance() == bank_before - 200


def test_integration_purchase_then_rent_transfers_to_owner():
    game = Game(["Alice", "Bob"])
    owner, tenant = game.players
    prop = game.board.get_property_at(1)
    assert prop is not None

    assert game.buy_property(owner, prop) is True
    owner_before = owner.balance
    tenant_before = tenant.balance

    game.pay_rent(tenant, prop)

    assert tenant.balance == tenant_before - prop.get_rent()
    assert owner.balance == owner_before + prop.get_rent()


def test_integration_trade_transfers_cash_and_property():
    game = Game(["Alice", "Bob"])
    seller, buyer = game.players
    prop = game.board.get_property_at(1)
    assert prop is not None

    assert game.buy_property(seller, prop) is True
    cash = 90
    seller_before = seller.balance
    buyer_before = buyer.balance

    assert game.trade(seller, buyer, prop, cash) is True
    assert prop.owner is buyer
    assert seller.balance == seller_before + cash
    assert buyer.balance == buyer_before - cash


def test_integration_bankruptcy_releases_owned_properties():
    game = Game(["Alice", "Bob"])
    player = game.players[0]
    prop = game.board.get_property_at(1)
    assert prop is not None

    assert game.buy_property(player, prop) is True
    prop.mortgage()
    player.balance = 0

    game._check_bankruptcy(player)

    assert player not in game.players
    assert prop.owner is None
    assert prop.is_mortgaged is False


def test_integration_jail_card_releases_and_moves(monkeypatch):
    game = Game(["Alice", "Bob"])
    player = game.players[0]
    player.go_to_jail()
    player.get_out_of_jail_cards = 1

    monkeypatch.setattr("moneypoly.moneypoly.moneypoly.ui.confirm", lambda _q: True)
    monkeypatch.setattr(game.dice, "roll", lambda: 4)
    monkeypatch.setattr(game.dice, "describe", lambda: "2 + 2 = 4")
    monkeypatch.setattr(game, "_move_and_resolve", lambda p, _r: setattr(p, "position", 14))

    game._handle_jail_turn(player)

    assert player.in_jail is False
    assert player.get_out_of_jail_cards == 0
    assert player.position == 14


def test_integration_jail_mandatory_release_collects_fine(monkeypatch):
    game = Game(["Alice", "Bob"])
    player = game.players[0]
    player.go_to_jail()
    player.jail_turns = 2
    bank_before = game.bank.get_balance()
    player_before = player.balance

    monkeypatch.setattr("moneypoly.moneypoly.moneypoly.ui.confirm", lambda _q: False)
    monkeypatch.setattr(game.dice, "roll", lambda: 3)
    monkeypatch.setattr(game.dice, "describe", lambda: "1 + 2 = 3")
    monkeypatch.setattr(game, "_move_and_resolve", lambda *_a, **_k: None)

    game._handle_jail_turn(player)

    assert player.in_jail is False
    assert player.balance == player_before - JAIL_FINE
    assert game.bank.get_balance() == bank_before + JAIL_FINE


def test_integration_collect_from_all_transfers_from_each_eligible_player():
    game = Game(["Alice", "Bob", "Cara"])
    collector = game.players[0]
    donor_1 = game.players[1]
    donor_2 = game.players[2]
    donor_1.balance = 30
    donor_2.balance = 5

    before = collector.balance
    game._card_collect_from_others(collector, 10)

    assert donor_1.balance == 20
    assert donor_2.balance == 5
    assert collector.balance == before + 10


def test_integration_card_move_to_property_and_buy(monkeypatch):
    game = Game(["Alice", "Bob"])
    player = game.players[0]
    prop = game.board.get_property_at(1)
    assert prop is not None

    player.position = 39
    balance_before = player.balance
    monkeypatch.setattr("builtins.input", lambda _q: "b")

    game._card_move_to(player, 1)

    assert player.position == 1
    assert prop.owner is player
    assert player.balance == balance_before + GO_SALARY - prop.price


def test_integration_auction_winner_updates_owner_and_bank(monkeypatch):
    game = Game(["Alice", "Bob"])
    prop = game.board.get_property_at(3)
    assert prop is not None

    bank_before = game.bank.get_balance()
    bids = iter([70, 0])
    monkeypatch.setattr("moneypoly.moneypoly.moneypoly.ui.safe_int_input", lambda *_a, **_k: next(bids))

    game.auction_property(prop)

    assert prop.owner is game.players[0]
    assert game.bank.get_balance() == bank_before + 70


def test_integration_turn_progression_non_double_advances(monkeypatch):
    game = Game(["Alice", "Bob"])

    monkeypatch.setattr(game.dice, "roll", lambda: 5)
    monkeypatch.setattr(game.dice, "describe", lambda: "2 + 3 = 5")
    monkeypatch.setattr(game.dice, "is_doubles", lambda: False)
    monkeypatch.setattr(game, "_move_and_resolve", lambda *_a, **_k: None)

    game.play_turn()

    assert game.current_player().name == "Bob"
    assert game.turn_number == 1


def test_integration_turn_progression_double_keeps_same_player(monkeypatch):
    game = Game(["Alice", "Bob"])

    monkeypatch.setattr(game.dice, "roll", lambda: 8)
    monkeypatch.setattr(game.dice, "describe", lambda: "4 + 4 = 8")
    monkeypatch.setattr(game.dice, "is_doubles", lambda: True)
    monkeypatch.setattr(game, "_move_and_resolve", lambda *_a, **_k: None)

    game.play_turn()

    assert game.current_player().name == "Alice"
    assert game.turn_number == 0


def test_integration_card_collect_uses_bank_payout_path(monkeypatch):
    game = Game(["Alice", "Bob"])
    player = game.players[0]
    before = player.balance

    monkeypatch.setattr(game.bank, "pay_out", lambda amt: amt)
    game._card_collect(player, 75)

    assert player.balance == before + 75
