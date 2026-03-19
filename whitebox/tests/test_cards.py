"""White-box tests for cards.py."""

import pytest

from moneypoly.moneypoly.moneypoly.cards import (
    CHANCE_CARDS,
    COMMUNITY_CHEST_CARDS,
    CardDeck,
)


@pytest.mark.parametrize("card", CHANCE_CARDS + COMMUNITY_CHEST_CARDS)
def test_all_cards_have_required_shape(card):
    assert set(card.keys()) == {"description", "action", "value"}
    assert isinstance(card["description"], str)
    assert isinstance(card["action"], str)
    assert isinstance(card["value"], int)


def test_draw_cycles_through_cards_in_order():
    cards = [{"description": "a", "action": "collect", "value": 1}, {"description": "b", "action": "pay", "value": 2}]
    deck = CardDeck(cards)
    assert deck.draw()["description"] == "a"
    assert deck.draw()["description"] == "b"
    assert deck.draw()["description"] == "a"


def test_peek_does_not_advance_index():
    cards = [{"description": "a", "action": "collect", "value": 1}]
    deck = CardDeck(cards)
    assert deck.peek()["description"] == "a"
    assert deck.peek()["description"] == "a"
    assert deck.index == 0


def test_reshuffle_resets_index(monkeypatch):
    cards = [{"description": "a", "action": "collect", "value": 1}, {"description": "b", "action": "pay", "value": 2}]
    deck = CardDeck(cards)
    deck.draw()

    called = {"ok": False}

    def fake_shuffle(values):
        called["ok"] = True
        values.reverse()

    monkeypatch.setattr("moneypoly.moneypoly.moneypoly.cards.random.shuffle", fake_shuffle)
    deck.reshuffle()

    assert called["ok"] is True
    assert deck.index == 0


@pytest.mark.parametrize(
    "draw_count,remaining",
    [
        (0, 3),
        (1, 2),
        (2, 1),
        (3, 3),
        (4, 2),
    ],
)
def test_cards_remaining_cycles_correctly(draw_count, remaining):
    cards = [
        {"description": "a", "action": "collect", "value": 1},
        {"description": "b", "action": "collect", "value": 1},
        {"description": "c", "action": "collect", "value": 1},
    ]
    deck = CardDeck(cards)
    for _ in range(draw_count):
        deck.draw()
    assert deck.cards_remaining() == remaining


def test_empty_deck_draw_returns_none():
    deck = CardDeck([])
    assert deck.draw() is None


def test_empty_deck_peek_returns_none():
    deck = CardDeck([])
    assert deck.peek() is None


def test_empty_deck_cards_remaining_is_zero():
    deck = CardDeck([])
    assert deck.cards_remaining() == 0


def test_len_and_repr_work_for_non_empty_deck():
    deck = CardDeck(CHANCE_CARDS)
    assert len(deck) == len(CHANCE_CARDS)
    assert "CardDeck(" in repr(deck)
