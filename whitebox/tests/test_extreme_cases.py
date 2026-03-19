"""Extreme edge-case tests to expose any remaining hidden defects."""

import pytest

from moneypoly.moneypoly.moneypoly.game import Game


def test_extreme_loan_above_bank_funds_raises_value_error():
    game = Game(["Alice", "Bob"])
    player = game.players[0]
    with pytest.raises(ValueError):
        game.bank.give_loan(player, game.bank.get_balance() + 1)


def test_extreme_mortgage_reduces_bank_funds_by_payout():
    game = Game(["Alice", "Bob"])
    player = game.players[0]
    prop = game.board.get_property_at(1)
    assert prop is not None

    assert game.buy_property(player, prop) is True
    bank_before = game.bank.get_balance()
    payout = prop.mortgage_value

    assert game.mortgage_property(player, prop) is True
    assert game.bank.get_balance() == bank_before - payout


def test_extreme_unmortgage_increases_bank_funds_by_cost():
    game = Game(["Alice", "Bob"])
    player = game.players[0]
    prop = game.board.get_property_at(1)
    assert prop is not None

    assert game.buy_property(player, prop) is True
    assert game.mortgage_property(player, prop) is True

    bank_before = game.bank.get_balance()
    cost = int(prop.mortgage_value * 1.1)

    assert game.unmortgage_property(player, prop) is True
    assert game.bank.get_balance() == bank_before + cost


def test_extreme_trade_negative_cash_rejected_without_state_change():
    game = Game(["Alice", "Bob"])
    seller, buyer = game.players
    prop = game.board.get_property_at(1)
    assert prop is not None

    assert game.buy_property(seller, prop) is True
    seller_before = seller.balance
    buyer_before = buyer.balance

    result = game.trade(seller, buyer, prop, -50)

    assert result is False
    assert prop.owner is seller
    assert seller.balance == seller_before
    assert buyer.balance == buyer_before


def test_extreme_trade_zero_cash_transfers_only_property():
    game = Game(["Alice", "Bob"])
    seller, buyer = game.players
    prop = game.board.get_property_at(1)
    assert prop is not None

    assert game.buy_property(seller, prop) is True
    seller_before = seller.balance
    buyer_before = buyer.balance

    assert game.trade(seller, buyer, prop, 0) is True
    assert prop.owner is buyer
    assert seller.balance == seller_before
    assert buyer.balance == buyer_before


def test_extreme_bankruptcy_on_last_index_resets_current_index_to_zero():
    game = Game(["Alice", "Bob", "Cara"])
    game.current_index = 2
    eliminated = game.players[2]
    eliminated.balance = 0

    game._check_bankruptcy(eliminated)

    assert game.current_index == 0
    assert eliminated not in game.players


def test_extreme_card_collect_raises_when_bank_cannot_pay():
    game = Game(["Alice", "Bob"])
    player = game.players[0]
    game.bank._funds = 10  # force low reserve for this edge path

    with pytest.raises(ValueError):
        game._card_collect(player, 100)


def test_extreme_move_and_resolve_rent_can_bankrupt_player():
    game = Game(["Alice", "Bob"])
    tenant, owner = game.players
    prop = game.board.get_property_at(39)
    assert prop is not None

    prop.owner = owner
    tenant.balance = prop.get_rent() - 1

    game._move_and_resolve(tenant, 39)

    assert tenant not in game.players


def test_extreme_auction_equal_bid_does_not_overtake_current_high(monkeypatch):
    game = Game(["Alice", "Bob"])
    prop = game.board.get_property_at(3)
    assert prop is not None

    # First bid 100 wins high; second equal bid 100 should be rejected.
    bids = iter([100, 100])
    monkeypatch.setattr("moneypoly.moneypoly.moneypoly.ui.safe_int_input", lambda *_a, **_k: next(bids))

    game.auction_property(prop)
    assert prop.owner is game.players[0]


def test_extreme_menu_loan_negative_amount_not_issued(monkeypatch):
    game = Game(["Alice", "Bob"])
    player = game.players[0]
    choices = iter([6, -500, 0])
    called = {"n": 0}

    monkeypatch.setattr("moneypoly.moneypoly.moneypoly.ui.safe_int_input", lambda *_a, **_k: next(choices))
    monkeypatch.setattr(game.bank, "give_loan", lambda *_a, **_k: called.__setitem__("n", called["n"] + 1))

    game.interactive_menu(player)
    assert called["n"] == 0


def test_extreme_card_move_to_owned_property_charges_and_credits_rent():
    game = Game(["Alice", "Bob"])
    tenant, owner = game.players
    prop = game.board.get_property_at(1)
    assert prop is not None

    prop.owner = owner
    tenant.position = 39
    tenant_before = tenant.balance
    owner_before = owner.balance

    game._card_move_to(tenant, 1)

    rent = prop.get_rent()
    assert tenant.balance == tenant_before + 200 - rent
    assert owner.balance == owner_before + rent


def test_extreme_collect_from_others_exact_balance_transfers_all():
    game = Game(["Alice", "Bob", "Cara"])
    collector = game.players[0]
    donor = game.players[1]
    third = game.players[2]
    donor.balance = 25
    third.balance = 0
    before = collector.balance

    game._card_collect_from_others(collector, 25)

    assert donor.balance == 0
    assert collector.balance == before + 25
