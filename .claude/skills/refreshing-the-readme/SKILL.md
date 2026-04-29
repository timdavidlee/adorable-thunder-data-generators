---
name: refreshing-the-readme
description: >
  Refreshes the project README and BRIEFS.md registry: verifies every shell command in the
  README still works, adds entries for new enterprise dataflows that have a generator but
  are missing from the repo-layout section, and reconciles BRIEFS.md against the filesystem
  (briefs dir + record_generators dir). Use when the user says "refresh the readme",
  "update the readme", "check the readme", "readme is stale", "refresh briefs.md",
  or invokes /refreshing-the-readme.
---

# Refreshing the README

Three jobs:

1. **Verify** every command in [README.md](../../../README.md) still runs.
2. **Sync** the repo-layout flow list in the README with what's actually under `src/adorable_thunder/make/record_generators/`.
3. **Reconcile** [BRIEFS.md](../../../BRIEFS.md) against the filesystem.

Touch only the README and BRIEFS.md. Don't restructure prose, don't reword unrelated sections.

## Checklist

### 1. Verify the commands

Walk every fenced command block in the README in order and run a non-destructive equivalent. If a command fails or its output disagrees with what the README claims, fix the README — don't fix the project to match.

| README command | How to verify |
|---|---|
| `cp .env.example .env` | Confirm `.env.example` exists at the repo root with `ls .env.example`. Don't actually overwrite the user's `.env`. |
| `docker compose up --build` | Run `docker compose config -q` to validate `compose.yml` parses and references existing Dockerfiles. Don't actually `up` the stack. |
| `uv sync` | Run `uv sync` — it's idempotent. |
| `uv run python -m adorable_thunder.make.database.inject_into_pg --flow <flow> --n-samples 500` | Run with `--help` instead: `uv run python -m adorable_thunder.make.database.inject_into_pg --help`. Confirm both `order_to_cash` and `procure_to_pay` appear as valid `--flow` choices. |
| `uv run pytest` | Run `uv run pytest --collect-only -q` to confirm the suite is discoverable. Don't run the full suite unless the user asks. |

For each mismatch, note it and edit the README to match reality.

### 2. Sync the flow list

The README's "Repository Layout" section under `record_generators/` lists each flow with a one-line description. Compare against the filesystem:

```bash
ls src/adorable_thunder/make/record_generators/
```

- Any directory present on disk but missing from the README → add a row, alphabetically placed, matching the existing `<name>/  # <one-line description>` formatting and column alignment.
- Any directory in the README but missing on disk → flag to the user before removing (it may be in-progress on a branch).

For the one-line description of a new flow, read its `__init__.py` or top-level docstring in `src/adorable_thunder/make/record_generators/<flow>/` and summarize the stage chain (e.g. `Quotes → orders → shipments → invoices → receipts → cash apps`). Match the tense and style of neighboring rows.

[BRIEFS.md](../../../BRIEFS.md) is reconciled in step 3 — by the time you finish that step, the README layout and BRIEFS.md should agree (every README layout row corresponds to a `has dataset` row in BRIEFS.md).

### 3. Reconcile BRIEFS.md

[BRIEFS.md](../../../BRIEFS.md) has one row per brief, sorted alphabetically, with columns: **Brief**, **Status** (`brief only` or `has dataset`), **Last Updated**.

Source of truth for each column:

| Column | Source |
|---|---|
| Brief | `ls src/adorable_thunder/enterprise_dataflow_briefs/*.md` |
| Status = `has dataset` | A directory exists at `src/adorable_thunder/make/record_generators/<flow_snake_case>/` AND the flow is registered in `src/adorable_thunder/make/database/inject_into_pg.py` (`ALL_FLOW_GENERATORS`) |
| Status = `brief only` | Brief file exists but no generator directory (or directory exists but isn't wired into `ALL_FLOW_GENERATORS`) |
| Last Updated | `git log -1 --format=%cs -- <path>` against the brief and (if it exists) the generator dir — take the more recent of the two. Use `YYYY-MM-DD`. |

Reconciliation steps:

1. Build the canonical list of briefs from the filesystem.
2. For each brief, determine its current status and last-updated date.
3. Compare against the existing rows in BRIEFS.md:
   - **Missing row** → insert in alphabetical position.
   - **Status changed** (`brief only` → `has dataset` or vice versa) → update.
   - **Last Updated stale** (older than what `git log` reports) → update.
   - **Row in BRIEFS.md but no brief file on disk** → flag to the user before removing; it may be uncommitted on a branch.
4. Keep the `kebab-case` filename convention in the link text (e.g. `[order-to-cash](...)`), and preserve the existing table formatting and column alignment.

The brief→generator name mapping is `kebab-case` ↔ `snake_case` (e.g. `order-to-cash` ↔ `order_to_cash`).

### 4. Report

End with a short summary:
- Commands verified / commands that needed README fixes
- Flows added to the README layout (and their descriptions)
- BRIEFS.md changes (rows added, statuses flipped, dates updated)
- Any drift flagged for the user (orphan rows, missing dirs, unwired generators, etc.)
