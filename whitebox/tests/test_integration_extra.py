"""Additional integration tests to expand whitebox coverage."""

from moneypoly.moneypoly.moneypoly.config import GO_SALARY, INCOME_TAX_AMOUNT, LUXURY_TAX_AMOUNT
from moneypoly.moneypoly.moneypoly.game import Game


def test_integration_move_and_resolve_income_tax_reduces_player_and_increases_bank():
    game = Game(["Alice", "Bob"])
    player = game.players[0]
    bank_before = game.bank.get_balance()
    player_before = player.balance

    game._handle_income_tax_tile(player)

    assert player.balance == player_before - INCOME_TAX_AMOUNT
    assert game.bank.get_balance() == bank_before + INCOME_TAX_AMOUNT


def test_integration_move_and_resolve_luxury_tax_reduces_player_and_increases_bank():
    game = Game(["Alice", "Bob"])
    player = game.players[0]
    bank_before = game.bank.get_balance()
    player_before = player.balance

    game._handle_luxury_tax_tile(player)

    assert player.balance == player_before - LUXURY_TAX_AMOUNT
    assert game.bank.get_balance() == bank_before + LUXURY_TAX_AMOUNT


def test_integration_card_move_to_same_or_forward_does_not_collect_go_salary():
    game = Game(["Alice", "Bob"])
    player = game.players[0]
    player.position = 5
    before = player.balance

    game._card_move_to(player, 10)

    assert player.balance == before
    assert player.position == 10


def test_integration_card_move_to_wrap_collects_go_salary(monkeypatch):
    game = Game(["Alice", "Bob"])
    player = game.players[0]
    player.position = 39
    before = player.balance

    # Moving to position 1 lands on an unowned property and triggers input.
    # Choose skip so we only verify the Go salary side effect.
    monkeypatch.setattr("builtins.input", lambda _prompt: "s")

    game._card_move_to(player, 1)

    assert player.balance == before + GO_SALARY


def test_integration_find_winner_none_when_players_empty():
    game = Game(["Alice", "Bob"])
    game.players = []
    assert game.find_winner() is None


def test_integration_check_bankruptcy_non_bankrupt_player_stays_in_game():
    game = Game(["Alice", "Bob"])
    player = game.players[0]
    player.balance = 10

    game._check_bankruptcy(player)

    assert player in game.players


def test_integration_buy_property_collects_price_into_bank():
    game = Game(["Alice", "Bob"])
    buyer = game.players[0]
    prop = game.board.get_property_at(1)
    assert prop is not None
    bank_before = game.bank.get_balance()

    ok = game.buy_property(buyer, prop)

    assert ok is True
    assert game.bank.get_balance() == bank_before + prop.price


def test_integration_buy_property_assigns_owner_and_player_property_list():
    game = Game(["Alice", "Bob"])
    buyer = game.players[0]
    prop = game.board.get_property_at(3)
    assert prop is not None

    assert game.buy_property(buyer, prop) is True
    assert prop.owner is buyer
    assert prop in buyer.properties


def test_integration_mortgage_then_unmortgage_restores_state():
    game = Game(["Alice", "Bob"])
    player = game.players[0]
    prop = game.board.get_property_at(1)
    assert prop is not None

    assert game.buy_property(player, prop) is True
    assert game.mortgage_property(player, prop) is True
    assert prop.is_mortgaged is True
    assert game.unmortgage_property(player, prop) is True
    assert prop.is_mortgaged is False


def test_integration_pay_rent_noop_if_owner_none():
    game = Game(["Alice", "Bob"])
    tenant = game.players[0]
    prop = game.board.get_property_at(1)
    assert prop is not None
    prop.owner = None
    before = tenant.balance

    game.pay_rent(tenant, prop)

    assert tenant.balance == before


def test_integration_pay_rent_noop_if_property_mortgaged():
    game = Game(["Alice", "Bob"])
    tenant, owner = game.players
    prop = game.board.get_property_at(1)
    assert prop is not None
    assert game.buy_property(owner, prop) is True
    prop.is_mortgaged = True
    before = tenant.balance

    game.pay_rent(tenant, prop)

    assert tenant.balance == before


def test_integration_trade_fails_if_buyer_cannot_afford():
    game = Game(["Alice", "Bob"])
    seller, buyer = game.players
    prop = game.board.get_property_at(1)
    assert prop is not None
    assert game.buy_property(seller, prop) is True
    buyer.balance = 0

    assert game.trade(seller, buyer, prop, 50) is False
    assert prop.owner is seller


def test_integration_trade_fails_if_seller_not_owner():
    game = Game(["Alice", "Bob"])
    seller, buyer = game.players
    prop = game.board.get_property_at(1)
    assert prop is not None

    assert game.trade(seller, buyer, prop, 50) is False


def test_integration_draw_and_apply_none_card_is_noop(monkeypatch):
    game = Game(["Alice", "Bob"])
    player = game.players[0]

    class EmptyDeck:
        def draw(self):
            return None

    game.decks["chance"] = EmptyDeck()
    before = player.balance
    game._draw_and_apply(player, "chance")

    assert player.balance == before


def test_integration_board_purchasable_becomes_false_after_buy():
    game = Game(["Alice", "Bob"])
    buyer = game.players[0]
    prop = game.board.get_property_at(1)
    assert prop is not None

    assert game.board.is_purchasable(prop.position) is True
    assert game.buy_property(buyer, prop) is True
    assert game.board.is_purchasable(prop.position) is False
