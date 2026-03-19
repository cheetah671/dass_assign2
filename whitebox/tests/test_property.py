"""White-box tests for property.py."""

import pytest

from moneypoly.moneypoly.moneypoly.player import Player
from moneypoly.moneypoly.moneypoly.property import Property, PropertyGroup


def test_mortgage_value_is_half_price():
    prop = Property("A", 1, 180, 14)
    assert prop.mortgage_value == 90


def test_mortgage_sets_flag_and_returns_value():
    prop = Property("A", 1, 120, 8)
    assert prop.mortgage() == 60
    assert prop.is_mortgaged is True


def test_mortgage_twice_returns_zero_second_time():
    prop = Property("A", 1, 120, 8)
    prop.mortgage()
    assert prop.mortgage() == 0


def test_unmortgage_cost_and_flag():
    prop = Property("A", 1, 120, 8)
    prop.mortgage()
    cost = prop.unmortgage()
    assert cost == 66
    assert prop.is_mortgaged is False


def test_unmortgage_when_not_mortgaged_returns_zero():
    prop = Property("A", 1, 120, 8)
    assert prop.unmortgage() == 0


def test_is_available_only_when_unowned_and_not_mortgaged():
    prop = Property("A", 1, 120, 8)
    assert prop.is_available() is True
    prop.is_mortgaged = True
    assert prop.is_available() is False
    prop.is_mortgaged = False
    prop.owner = Player("O")
    assert prop.is_available() is False


def test_group_add_property_links_back():
    group = PropertyGroup("Red", "red")
    prop = Property("A", 1, 120, 8)
    group.add_property(prop)
    assert prop.group is group
    assert group.size() == 1


def test_group_all_owned_by_requires_every_property_owned_by_player():
    group = PropertyGroup("Red", "red")
    p1 = Player("P1")
    p2 = Player("P2")
    a = Property("A", 1, 120, 8)
    b = Property("B", 3, 120, 8)
    group.add_property(a)
    group.add_property(b)

    a.owner = p1
    b.owner = p2
    assert group.all_owned_by(p1) is False

    b.owner = p1
    assert group.all_owned_by(p1) is True


def test_group_all_owned_by_none_player_false():
    group = PropertyGroup("Red", "red")
    assert group.all_owned_by(None) is False


def test_get_owner_counts_reports_counts_by_owner():
    group = PropertyGroup("Red", "red")
    p1 = Player("P1")
    p2 = Player("P2")
    props = [Property(str(i), i, 100, 8) for i in range(3)]
    for prop in props:
        group.add_property(prop)
    props[0].owner = p1
    props[1].owner = p1
    props[2].owner = p2

    counts = group.get_owner_counts()
    assert counts[p1] == 2
    assert counts[p2] == 1


def test_get_rent_doubles_only_on_full_group_ownership():
    group = PropertyGroup("Blue", "blue")
    p1 = Player("P1")
    p2 = Player("P2")
    a = Property("A", 1, 100, 10)
    b = Property("B", 2, 100, 10)
    group.add_property(a)
    group.add_property(b)

    a.owner = p1
    b.owner = p2
    assert a.get_rent() == 10

    b.owner = p1
    assert a.get_rent() == 20


def test_get_rent_zero_when_mortgaged():
    prop = Property("A", 1, 100, 10)
    prop.is_mortgaged = True
    assert prop.get_rent() == 0


@pytest.mark.parametrize("price", [60, 100, 200, 400])
def test_mortgage_value_parametrized(price):
    prop = Property("A", 1, price, 10)
    assert prop.mortgage_value == price // 2
