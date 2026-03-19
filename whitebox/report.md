# 1.2 Code Quality Analysis (pylint)

## Objective
Run `pylint` on the MoneyPoly codebase, fix warnings iteratively, and keep one commit per iteration.

## Baseline Run
- Date: 2026-03-19
- Official baseline command used for this report:

```bash
/home/arnav-agnihotri/miniconda3/envs/autograder/bin/python -m pylint moneypoly/moneypoly/moneypoly
```

- Official baseline score: `8.17/10`

## Note On Score Difference
- Running pylint on only `moneypoly/moneypoly/moneypoly` gives `8.17/10`.
- Running pylint on `moneypoly/moneypoly/moneypoly` plus `moneypoly/moneypoly/main.py` gives `9.08/10`.
- For consistency in section 1.2, this report uses `8.17/10` as the baseline and compares all iterations against the same command.

## Baseline Issues Found
- Missing module/function/class docstrings in multiple files.
- `unused-import` in `bank.py`, `dice.py`, `player.py`, `game.py`.
- `unused-variable` in `player.py` (`old_position`).
- `bare-except` in `ui.py`.
- `line-too-long` in many lines of `cards.py`.
- `singleton-comparison` in `board.py` (`== True`).
- `missing-final-newline` in `player.py` and `game.py`.
- `superfluous-parens` around `not (...)` in `game.py`.
- `f-string-without-interpolation` in `game.py`.
- Design warnings such as `too-many-branches`, `too-many-instance-attributes`, and constructor argument-count warnings.

## Iteration Log
Use one commit after each lint-fix pass with message format:
`Iteration #: <What You Changed>`

- Iteration 1: Pending
	- Planned focus: safe style/import fixes that do not change game behavior.
	- Planned commit message: `Iteration 1: Remove unused imports and fix simple pylint style warnings`

