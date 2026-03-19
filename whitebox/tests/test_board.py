"""White-box tests for board.py."""

import pytest

from moneypoly.moneypoly.moneypoly.board import Board, SPECIAL_TILES
from moneypoly.moneypoly.moneypoly.player import Player


@pytest.mark.parametrize("position", sorted(SPECIAL_TILES.keys()))
def test_special_tiles_return_expected_types(position):
    board = Board()
    assert board.get_tile_type(position) == SPECIAL_TILES[position]


@pytest.mark.parametrize("position", [1, 3, 6, 8, 9, 11, 39])
def test_property_positions_report_property_tile(position):
    board = Board()
    assert board.get_tile_type(position) == "property"


@pytest.mark.parametrize("position", [12, 28])
def test_blank_positions_report_blank(position):
    board = Board()
    assert board.get_tile_type(position) == "blank"


@pytest.mark.parametrize("position", [1, 3, 6, 39])
def test_get_property_at_known_positions(position):
    board = Board()
    prop = board.get_property_at(position)
    assert prop is not None
    assert prop.position == position


def test_get_property_at_unknown_position_returns_none():
    board = Board()
    assert board.get_property_at(12) is None


def test_is_purchasable_only_for_unowned_non_mortgaged_property():
    board = Board()
    prop = board.get_property_at(1)
    assert prop is not None

    assert board.is_purchasable(1) is True
    prop.owner = Player("Owner")
    assert board.is_purchasable(1) is False

    prop.owner = None
    prop.is_mortgaged = True
    assert board.is_purchasable(1) is False


def test_is_purchasable_false_for_non_property():
    board = Board()
    assert board.is_purchasable(0) is False


@pytest.mark.parametrize("position", [0, 2, 7, 10, 20, 22, 30, 38])
def test_is_special_tile_true_for_special_positions(position):
    board = Board()
    assert board.is_special_tile(position) is True


@pytest.mark.parametrize("position", [1, 6, 12, 28, 39])
def test_is_special_tile_false_for_non_special_positions(position):
    board = Board()
    assert board.is_special_tile(position) is False


def test_properties_owned_by_filters_by_owner():
    board = Board()
    p1 = Player("P1")
    p2 = Player("P2")
    board.properties[0].owner = p1
    board.properties[1].owner = p1
    board.properties[2].owner = p2

    owned = board.properties_owned_by(p1)
    assert len(owned) == 2
    assert all(prop.owner == p1 for prop in owned)


def test_unowned_properties_filters_correctly():
    board = Board()
    board.properties[0].owner = Player("P")
    unowned = board.unowned_properties()
    assert len(unowned) == len(board.properties) - 1


def test_repr_shows_total_and_owned_counts():
    board = Board()
    board.properties[0].owner = Player("P")
    text = repr(board)
    assert "Board(" in text
    assert "22 properties" in text
    assert "1 owned" in text
