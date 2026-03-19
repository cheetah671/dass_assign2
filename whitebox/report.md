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

### Iteration 0: Add pylint baseline report and issue log
- Command:

```bash
/home/arnav-agnihotri/miniconda3/envs/autograder/bin/python -m pylint moneypoly/moneypoly/moneypoly
```

- Score: `8.17/10`
- Issues found:
	- Missing module/function/class docstrings.
	- `unused-import`, `unused-variable`, `bare-except`, `line-too-long`, `singleton-comparison`.
	- `missing-final-newline`, `superfluous-parens`, `f-string-without-interpolation`.
	- `import-error` and design warnings (`too-many-branches`, `too-many-instance-attributes`, etc.).
- Changes made:
	- Created baseline analysis section and recorded all issue categories.

### Iteration 1: Remove unused imports and fix simple pylint style warnings
- Command:

```bash
/home/arnav-agnihotri/miniconda3/envs/autograder/bin/python -m pylint moneypoly/moneypoly/moneypoly
```

- Score: `9.04/10`
- Issues found in this iteration:
	- `missing-module-docstring` and `missing-function-docstring` in several files.
	- `unused-import` and `unused-variable` warnings.
	- `bare-except`, `singleton-comparison`, and `line-too-long` warnings.
	- `missing-final-newline`, `superfluous-parens`, `f-string-without-interpolation`, `no-else-break`, `no-else-return`.
- Changes made:
	- Added module/function/class docstrings in `main.py`, `ui.py`, `dice.py`, `config.py`, `bank.py`, `board.py`, `property.py`, `player.py`, and `game.py`.
	- Removed unused imports and unused local variable (`old_position`).
	- Replaced bare `except` with `except ValueError` in `ui.py`.
	- Replaced `prop.is_mortgaged == True` with truthy check.
	- Reformatted card definitions in `cards.py` to fix long-line warnings.
	- Fixed minor style warnings in `game.py` and added missing final newlines.
- Remaining issues after Iteration 1:
	- `import-error` for package imports during lint execution.
	- Design warnings such as `too-many-instance-attributes`, `too-many-arguments`, and `too-many-branches`.

### Iteration 2: Resolve package import errors and stabilize module imports
- Command:

```bash
/home/arnav-agnihotri/miniconda3/envs/autograder/bin/python -m pylint moneypoly/moneypoly/moneypoly
```

- Score: `9.91/10`
- Issues found in this iteration:
	- `import-error` in `board.py`, `bank.py`, `player.py`, and `game.py` due to package resolution during lint.
	- Remaining design warnings: `too-many-instance-attributes`, `too-many-arguments`, `too-many-positional-arguments`, `too-many-branches`.
- Changes made:
	- Converted internal imports from absolute package paths to relative imports in `board.py`, `bank.py`, `player.py`, and `game.py`.
	- Added package initializer `moneypoly/moneypoly/moneypoly/__init__.py`.
	- Re-ran pylint with the same command used in baseline for fair comparison.
- Remaining issues after Iteration 2:
	- `too-many-instance-attributes` in `property.py`, `player.py`, and `game.py`.
	- `too-many-arguments` and `too-many-positional-arguments` in `Property.__init__`.
	- `too-many-branches` in `Game._move_and_resolve`.

