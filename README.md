# `adorable-thunder-data-generators`

Data generators for synthetic datasets, for educational purposes

# Design Rules

1. For each `generator` type - create a `typer` cli that can be called individually
2. the base `src/adorable_thunder/central_cli.py` should have a `typer` cli that inherits from all previous
3. Avoid python row by row loops, and try to maximize `numpy` array operations to generate entire columns when possible


## Commands

- Type check: `mypy src/`
- All checks: `make check`
- Code Formatting: `ruff format`
- Tests `pytest`
