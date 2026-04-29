---
name: add-flow
description: >
  Adds a new enterprise data flow to the adorable-thunder project: creates the enterprise
  brief, scrutiny brief, record generator package, and registers the flow in inject_into_pg.
  Use when the user says "add a new flow", "add flow", "new data flow", "implement a flow",
  or invokes /add-flow. Accepts a flow name as an argument (e.g. "record-to-report").
---

# Add Flow

Creates all files for a new enterprise data flow and wires it into the pipeline.

## Naming conventions

| Form | Example | Used for |
|---|---|---|
| kebab-case | `record-to-report` | Brief filenames, flow argument to CLI |
| snake_case | `record_to_report` | Python package dir, `FLOW_NAME` const |
| ABBR | `R2R` | Import aliases in `inject_into_pg.py` |

## Checklist

Work through these in order. Verify each before moving to the next.

### 1. Read existing briefs for the flow

Before writing anything, read the enterprise brief for context:

```
src/adorable_thunder/enterprise_dataflow_briefs/<flow-name>.md
```

If no brief exists yet, write one first — see [REFERENCE.md](REFERENCE.md#enterprise-brief-format).

### 2. Write the scrutiny brief

```
src/adorable_thunder/scrutinize/specific_briefs/<flow-name>.md
```

List 8–12 high-priority checks. Each line: **field/invariant** (severity): description.
See [REFERENCE.md](REFERENCE.md#scrutiny-brief-format) for format and examples.

### 3. Create the generator package

```
src/adorable_thunder/make/record_generators/<flow_name>/
  __init__.py
  flow.py
  <stage1>.py
  <stage2>.py
  ...
  briefs/
    TODO.md
```

`briefs/TODO.md` is the living wishlist that `/insights-wishlist` appends to. Seed it with a header like:

```markdown
# Insights Wishlist TODO — <flow_name>

Living TODO of field/data additions proposed by `/insights-wishlist`. Full runs are archived under `docs/generated/iter/<flow-name>/`. Prune entries here as they are implemented or become irrelevant.
```

For each stage file, implement:
- `<STAGE>_TABLE_NAME: str`
- `create_pg_sql_table_schema(pg_schema: str) -> CreatePgTableSql`
- `generate_<stage>(n_samples, ...) -> pd.DataFrame`

Then wire stages together in `flow.py` and export from `__init__.py`.

See [REFERENCE.md](REFERENCE.md#generator-patterns) for import patterns, PgColumn conventions,
date-chain enforcement, and FK linkage.

### 4. Register in inject_into_pg.py

File: `src/adorable_thunder/make/database/inject_into_pg.py`

Add imports following the existing pattern, then add to `ALL_FLOW_GENERATORS`:

```python
from adorable_thunder.make.record_generators.<flow_name> import (
    FLOW_SCHEMAS as <ABBR>_FLOW_SCHEMAS,
)
from adorable_thunder.make.record_generators.<flow_name> import (
    GeneratorConfig as <ABBR>GeneratorConfig,
)

ALL_FLOW_GENERATORS = [
    ...existing...,
    (<ABBR>GeneratorConfig, <ABBR>_FLOW_SCHEMAS),
]
```

### 5. Verify

```bash
PG_USER=postgres PG_PASSWORD=postgres PG_DBNAME=adorable_thunder \
  uv run python -m adorable_thunder.make.database.inject_into_pg \
  --flow <flow_name> --n-samples 1_000 --drop
```

```bash
uv run ruff check src/ && uv run pyright
```

Fix any errors before reporting done.

### 6. Update BRIEFS.md registry

File: `BRIEFS.md` at the repo root.

Find the row for `<flow-name>` in the table and update both **Status** and **Last Updated**:

```
| [<flow-name>](src/adorable_thunder/enterprise_dataflow_briefs/<flow-name>.md) | has dataset | <YYYY-MM-DD> |
```

Use today's date. Rows are sorted alphabetically by brief name — keep that ordering.

If no row exists yet (e.g. a brand-new brief that wasn't in the registry), insert one in
the correct alphabetical position.

### 7. Write iteration log

After all wiring is done and verification has passed, record what was built.

Path: `docs/generated/iter/<flow-name>/<timestamp>--add-flow.md`

- `<flow-name>` is the kebab-case flow name (e.g. `record-to-report`)
- `<timestamp>` is `date +%Y-%m-%d-%H%M%S` at completion

Create the `<flow-name>/` subdirectory if it does not exist. Follow the contents template in [docs/generated/CLAUDE.md](../../docs/generated/CLAUDE.md) — a few paragraphs covering what ran, what changed (enterprise brief, scrutiny brief, generator package, `inject_into_pg.py` wiring, `BRIEFS.md` row), verification (inject succeeded, ruff/pyright clean), and follow-ups.
