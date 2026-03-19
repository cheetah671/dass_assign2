"""White-box tests for player.py."""

import pytest

from moneypoly.moneypoly.moneypoly.config import GO_SALARY
from moneypoly.moneypoly.moneypoly.player import Player


@pytest.mark.parametrize("amount", [0, 1, 75, 999])
def test_add_money_increases_balance(amount):
    p = Player("P")
    before = p.balance
    p.add_money(amount)
    assert p.balance == before + amount


@pytest.mark.parametrize("amount", [0, 1, 75, 999])
def test_deduct_money_decreases_balance(amount):
    p = Player("P")
    before = p.balance
    p.deduct_money(amount)
    assert p.balance == before - amount


@pytest.mark.parametrize("amount", [-1, -100])
def test_add_money_negative_raises(amount):
    p = Player("P")
    with pytest.raises(ValueError):
        p.add_money(amount)


@pytest.mark.parametrize("amount", [-1, -100])
def test_deduct_money_negative_raises(amount):
    p = Player("P")
    with pytest.raises(ValueError):
        p.deduct_money(amount)


@pytest.mark.parametrize("balance,expected", [(0, True), (-1, True), (1, False)])
def test_is_bankrupt(balance, expected):
    p = Player("P", balance=balance)
    assert p.is_bankrupt() is expected


def test_move_wraps_board_and_passes_go_collects_salary():
    p = Player("P")
    p.position = 39
    before = p.balance
    p.move(2)
    assert p.position == 1
    assert p.balance == before + GO_SALARY


def test_move_landing_on_go_collects_salary():
    p = Player("P")
    p.position = 39
    before = p.balance
    p.move(1)
    assert p.position == 0
    assert p.balance == before + GO_SALARY


def test_go_to_jail_sets_flags():
    p = Player("P")
    p.go_to_jail()
    assert p.in_jail is True
    assert p.jail_turns == 0


def test_property_add_remove_count():
    p = Player("P")
    marker = object()
    p.add_property(marker)
    p.add_property(marker)
    assert p.count_properties() == 1
    p.remove_property(marker)
    assert p.count_properties() == 0


def test_status_line_contains_core_fields():
    p = Player("P")
    status = p.status_line()
    assert "P:" in status
    assert "pos=" in status
    assert "props=" in status
