"""Shared pytest fixtures for MoneyPoly white-box tests."""

import pytest

from moneypoly.moneypoly.moneypoly.game import Game


@pytest.fixture
def game_two_players():
    """Create a deterministic 2-player game fixture."""
    return Game(["Alice", "Bob"])


@pytest.fixture
def sample_property(game_two_players):
    """Return a purchasable board property from the game fixture."""
    return game_two_players.board.properties[0]
