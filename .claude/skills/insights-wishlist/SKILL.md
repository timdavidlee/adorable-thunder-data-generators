---
name: insights-wishlist
description: >
  Iteratively explores generated data in the Postgres database via MCP run_sql/list_tables
  and proposes new fields that would unlock better analytics, visualization, or behavioral
  understanding, then implements the Top 5 back into the generator scripts and re-injects
  to verify. The inverse of scrutinize: instead of flagging unrealistic data, it dreams up
  what's missing — and wires it in. Use when the user says "insights wishlist", "wishlist",
  "what fields are missing", "what should we add for analytics", or invokes
  /insights-wishlist. Accepts an optional flow argument (e.g. "order-to-cash"); defaults
  to "order-to-cash".
---

# Insights Wishlist

Counterpart to `scrutinize`. Scrutinize asks "is what's here realistic?" — this skill
asks "what's missing that would make this dataset more analytically valuable?" — and
then implements the highest-leverage proposals back into the generator code.

## Persona

You are a senior analytics engineer at a mid-to-large enterprise. You know what BI
dashboards, cohort analyses, attribution models, and ML features typically need. You spot
when a table records the *event* but not the *attribution*, the *outcome* but not the
*driver*, the *current state* but not the *transition*.

## What to look for

For each table, ask:

- **Analytics gaps** — aggregations or cohort cuts blocked by a missing field
  (e.g. no `acquisition_channel` on customers → can't do channel-attributed retention).
- **Visualization gaps** — fields that would unlock a useful chart or map but aren't there
  (e.g. no `geographic_region` → no geo heatmaps).
- **Behavioral gaps** — entity actions or transitions that go unrecorded
  (e.g. status column has current state but no `status_changed_at` → no time-in-state).
- **Cross-table connections** — fields that would let you join two tables in a meaningful
  new way (e.g. `campaign_id` on orders ties marketing spend to revenue).

## Steps

### 1. Load context

Read the flow's briefs so suggestions stay grounded in the flow's purpose:

- `src/adorable_thunder/enterprise_dataflow_briefs/<flow>.md` — what this flow is for
- `src/adorable_thunder/scrutinize/specific_briefs/<flow>.md` — realism benchmarks

Flow names are kebab-case here: `order-to-cash`, `procure-to-pay`, etc.

### 2. Discover the schema

The Postgres schema name uses underscores (e.g. `order_to_cash`). Call `list_tables`,
then for each table:

```sql
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_schema = '<flow_schema>' AND table_name = '<table>'
ORDER BY ordinal_position;
```

### 3. Profile iteratively

Don't try to be exhaustive. Follow what's interesting:

- Sample 5–10 rows per table with `run_sql` to see what's actually populated.
- Look at value distributions on enum-like / categorical columns.
- Note which foreign keys exist and what *doesn't* tie together.

After each query, ask: "given what I just saw, what would I *want* to see that isn't here?"
Run a follow-up query if you need to validate the gap (e.g. confirm a field really is
missing, or that an existing column doesn't already cover it).

### 4. Propose fields

For each suggestion:

- **table** — which table the new field would join
- **proposed_field** — snake_case name
- **data_type** — postgres type
- **category** — analytics / visualization / behavioral / cross-table
- **rationale** — 1–2 sentences on what this unlocks
- **example_use_case** — a specific dashboard, cohort, or model that becomes possible
- **priority** — high / medium / low (high = unlocks a fundamental analytical question
  that current schema cannot answer at all)

### 5. Report

Group suggestions by table. End with a **Top 5 wishlist** ranked across all tables —
the fields with highest analytical leverage relative to generation cost. Paired
proposals (e.g. `purchase_order_id + vendor_name`) count as one slot.

The Top 5 is what the implementation step (step 8) will actually wire up; everything
beyond it stays in the TODO for a later run.

### 6. Write iteration log

After reporting to the user, persist the wishlist as an iteration log.

Path: `docs/generated/iter/<flow>/<timestamp>--insights-wishlist.md`

- `<flow>` is the kebab-case flow name (already kebab-case in this skill's argument)
- `<timestamp>` is `date +%Y-%m-%d-%H%M%S` at completion

Create the `<flow>/` subdirectory if it does not exist. Follow the contents template in [docs/generated/CLAUDE.md](../../docs/generated/CLAUDE.md). For this skill, the **What changed** section has two parts:

1. **Wishlist** — the proposals grouped by table, plus the Top 5.
2. **Implemented** — the subset of the Top 5 that step 8 actually wired into the generators (file paths + which fields were added). If a Top 5 item was skipped, note why.

Under **Verification**, list the post-implementation checks: `ruff` / `pyright` clean, re-inject succeeded, row counts produced.

### 7. Append to the living TODO

Also append this run's wishlist to the flow's living TODO so the user has a single working list to draw from across runs.

Path: `src/adorable_thunder/make/record_generators/<flow_underscore>/briefs/TODO.md`

- `<flow_underscore>` is the schema-style name (e.g. `order_to_cash`, `procure_to_pay`). Convert from the kebab-case flow argument by replacing `-` with `_`.
- The file already exists with a header — **append**, do not overwrite.
- Append a dated section like:

  ```markdown

  ## <YYYY-MM-DD> run

  ### Top 5
  1. **<table>.<proposed_field>** (<priority>) — <one-line rationale>
  ...

  ### All proposals
  - **<table>.<proposed_field>** (<category>, <priority>) — <rationale>
  ...
  ```

- Don't try to dedupe against earlier runs — the user prunes manually as items are rejected or become irrelevant.
- The full iteration log written in step 6 remains the immutable audit trail; this TODO is the working list and may be truncated over time.

### 8. Implement the Top 5

For each item in the Top 5, edit the generator package at
`src/adorable_thunder/make/record_generators/<flow_underscore>/`:

- Add the new column to the relevant stage's `create_pg_sql_table_schema` (`PgColumn` list).
- Update the stage's `generate_<stage>(...)` function to populate the column.
- Reuse existing field generators in `field_generators/` whenever a fitting one exists
  (`generate_country_codes`, `generate_user_emails`, etc.); only inline a new value pool
  if no generator fits.
- Honor the realism constraints in the scrutiny brief — if a Top 5 item conflicts with
  a scrutiny rule, skip it and note the skip in the iteration log under **Implemented**.
- Skip "out of scope" items that would require new tables.

Paired proposals (e.g. `purchase_order_id + vendor_name`) are implemented together as
one Top 5 slot.

### 9. Verify

Same gates as `add-flow`. Fix issues before continuing — the goal is a clean inject.

```bash
uv run ruff check src/adorable_thunder/make/record_generators/<flow_underscore>/
uv run pyright src/adorable_thunder/make/record_generators/<flow_underscore>/
```

Then re-inject so the schema picks up the new columns:

```bash
PG_USER=postgres PG_PASSWORD=postgres PG_DBNAME=adorable_thunder \
  uv run python -m adorable_thunder.make.database.inject_into_pg \
  --flow <flow_underscore> --n-samples 1000 --drop
```

### 10. Mark implemented items in the TODO

For every Top 5 item that step 8 actually wired in, **strike through** the matching
bullet in the run's `### Top 5` block in `briefs/TODO.md` by wrapping it in `~~ ~~`:

```markdown
1. ~~**assets.gl_account** (high) — depreciation expense GL account.~~
```

Do the same for any matching bullet in the run's `### All proposals` block. Leave
non-implemented items untouched — they remain the working backlog. Don't strike items
from earlier runs.

## Constraints

- Don't propose fields that already exist — you read the schema in step 2, use it.
- Don't propose fields that would violate realism principles in the scrutiny brief.
- Prefer fields that are *cheap to generate* and *high analytical value*. A typed enum
  like `device_type` beats a free-text `notes` column.
- Don't propose new tables — this skill is about field additions to existing tables.
  If you spot a gap that genuinely needs a new table, mention it once at the end as an
  "out of scope" note.
