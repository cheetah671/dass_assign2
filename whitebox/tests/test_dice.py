"""White-box tests for dice.py."""

from moneypoly.moneypoly.moneypoly.dice import Dice


def test_reset_clears_faces_and_streak():
    dice = Dice()
    dice.die1 = 3
    dice.die2 = 5
    dice.doubles_streak = 2
    dice.reset()
    assert dice.die1 == 0
    assert dice.die2 == 0
    assert dice.doubles_streak == 0


def test_roll_values_are_in_six_sided_range():
    dice = Dice()
    for _ in range(200):
        dice.roll()
        assert 1 <= dice.die1 <= 6
        assert 1 <= dice.die2 <= 6


def test_roll_updates_total(monkeypatch):
    values = iter([2, 6])
    monkeypatch.setattr("moneypoly.moneypoly.moneypoly.dice.random.randint", lambda _a, _b: next(values))
    dice = Dice()
    assert dice.roll() == 8


def test_doubles_streak_increments_on_doubles(monkeypatch):
    values = iter([3, 3, 4, 4])
    monkeypatch.setattr("moneypoly.moneypoly.moneypoly.dice.random.randint", lambda _a, _b: next(values))
    dice = Dice()
    dice.roll()
    dice.roll()
    assert dice.doubles_streak == 2


def test_doubles_streak_resets_on_non_double(monkeypatch):
    values = iter([2, 2, 1, 3])
    monkeypatch.setattr("moneypoly.moneypoly.moneypoly.dice.random.randint", lambda _a, _b: next(values))
    dice = Dice()
    dice.roll()
    assert dice.doubles_streak == 1
    dice.roll()
    assert dice.doubles_streak == 0


def test_describe_shows_doubles_tag(monkeypatch):
    values = iter([5, 5])
    monkeypatch.setattr("moneypoly.moneypoly.moneypoly.dice.random.randint", lambda _a, _b: next(values))
    dice = Dice()
    dice.roll()
    assert "(DOUBLES)" in dice.describe()


def test_repr_contains_fields():
    dice = Dice()
    text = repr(dice)
    assert "Dice(" in text
    assert "die1" in text
    assert "die2" in text
