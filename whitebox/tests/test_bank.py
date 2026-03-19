"""White-box tests for bank.py."""

import pytest

from moneypoly.moneypoly.moneypoly.bank import Bank
from moneypoly.moneypoly.moneypoly.player import Player


@pytest.mark.parametrize("amount", [1, 25, 500, 9999])
def test_collect_positive_increases_balance_and_total(amount):
    bank = Bank()
    before = bank.get_balance()
    bank.collect(amount)
    assert bank.get_balance() == before + amount


@pytest.mark.parametrize("amount", [-1, -5, -200])
def test_collect_negative_amounts_are_ignored(amount):
    bank = Bank()
    before = bank.get_balance()
    bank.collect(amount)
    assert bank.get_balance() == before


@pytest.mark.parametrize("amount", [0, -1, -999])
def test_pay_out_non_positive_returns_zero(amount):
    bank = Bank()
    before = bank.get_balance()
    assert bank.pay_out(amount) == 0
    assert bank.get_balance() == before


def test_pay_out_insufficient_funds_raises_value_error():
    bank = Bank()
    with pytest.raises(ValueError):
        bank.pay_out(bank.get_balance() + 1)


@pytest.mark.parametrize("amount", [1, 10, 1500])
def test_pay_out_reduces_bank_funds(amount):
    bank = Bank()
    before = bank.get_balance()
    paid = bank.pay_out(amount)
    assert paid == amount
    assert bank.get_balance() == before - amount


@pytest.mark.parametrize("amount", [0, -10])
def test_give_loan_non_positive_does_not_change_player_or_loan_count(amount):
    bank = Bank()
    player = Player("P")
    before = player.balance
    bank.give_loan(player, amount)
    assert player.balance == before
    assert bank.loan_count() == 0


@pytest.mark.parametrize("amount", [1, 100, 350])
def test_give_loan_positive_updates_player_and_records_loan(amount):
    bank = Bank()
    player = Player("P")
    before = player.balance
    bank.give_loan(player, amount)
    assert player.balance == before + amount
    assert bank.loan_count() == 1
    assert bank.total_loans_issued() == amount


def test_summary_prints_bank_details(capsys):
    bank = Bank()
    bank.collect(100)
    bank.summary()
    out = capsys.readouterr().out
    assert "Bank reserves" in out
    assert "Total collected" in out
    assert "Loans issued" in out


def test_repr_contains_class_name():
    bank = Bank()
    assert "Bank(" in repr(bank)
