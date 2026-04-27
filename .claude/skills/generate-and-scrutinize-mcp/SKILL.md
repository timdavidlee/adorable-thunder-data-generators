---
name: generate-and-scrutinize-mcp
description: >
  Same cycle as generate-and-scrutinize but scrutinizes the database directly via MCP
  postgres tools (list_tables, run_sql) instead of the adorable_thunder scrutinize agent.
  Use when the user says "generate and scrutinize mcp", "mcp cycle", or invokes
  /generate-and-scrutinize-mcp. Accepts an optional flow argument (order_to_cash,
  procure_to_pay); defaults to order_to_cash.
---

# Generate and Scrutinize (MCP)

One iterative cycle: ensure DB → generate → scrutinize via MCP → fix generators.

## Scrutinizer persona

You are a data quality critic for enterprise procurement and finance datasets.

Your job is to evaluate whether generated records in a PostgreSQL database look realistic
for a mid-to-large enterprise (500–10,000 employees) — one with diverse suppliers,
multi-currency spend, layered approval hierarchies, and dedicated procurement/finance teams.

### What to flag

- Amount distributions that are too uniform or violate expected tiers
- Status distributions that are too clean (e.g. 90% approved)
- Date chain violations (e.g. payment before invoice)
- Cross-field inconsistencies (currency vs. supplier region, requester = approver)
- Sparse required fields (cost_center, currency_code, etc.) at >5% null
- Identifier formats that don't follow realistic conventions
- Supplier/product pairings from mismatched industries
- Arithmetic errors (e.g. gain/loss = proceeds − book_value)

### Output structure

Each finding must be specific and actionable:

- `field`: the column or field being flagged (use "multi-field" for cross-field issues)
- `issue`: what is wrong and why it's unrealistic
- `suggestion`: a concrete change the generator should make
- `severity`: low / medium / high

If no issues are found, explicitly confirm: "No issues found — data looks realistic for a
mid-to-large enterprise `<flow>` dataset."

## Steps

### 1. Ensure postgres is healthy

```bash
docker compose up -d postgres
```

Then wait for healthy:

```bash
docker compose exec postgres pg_isready -U $POSTGRES_USER -d $POSTGRES_DB
```

If the service fails to become healthy after ~30s, stop and report the error.

### 2. Generate fresh data

```bash
uv run python -m adorable_thunder.make.database.inject_into_pg \
  --flow <flow> --n-samples 10_000 --drop
```

Valid flow values: `order_to_cash`, `procure_to_pay`  
Default: `order_to_cash`

### 3. Scrutinize via MCP tools

Use the `list_tables` and `run_sql` MCP tools directly — do NOT run
`adorable_thunder.scrutinize`. You are the scrutinizer.

#### 3a. Load the scrutiny brief

Read the flow-specific scrutiny brief so you know which checks matter most and what
the realism benchmarks are before running any SQL:

```
src/adorable_thunder/scrutinize/specific_briefs/<flow>.md
```

Flow name format here uses kebab-case: `order-to-cash`, `procure-to-pay`.

Ingest the brief fully. The high-severity items listed there are the most likely
to catch generator bugs — prioritise them when forming SQL queries.

#### 3b. Load table LLM annotations

Run the annotation tool to get per-column descriptions, expected data types, and
representative example values for every table in the flow. This tells you what each
field means and what values to expect before querying the live database.

```bash
uv run python -c "
import asyncio
from adorable_thunder.scrutinize.tools.table_schema import get_table_llm_annotations
print(asyncio.run(get_table_llm_annotations.ainvoke({'flow': '<flow>'})))
"
```

Flow name format here uses kebab-case: `order-to-cash`, `procure-to-pay`.

Read the output in full before writing any SQL — column names and value formats
are described there, not in the live schema.

#### 3c. Discover schema

Call `list_tables` to get all tables, then for each table run:

```sql
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_schema = 'public' AND table_name = '<table>'
ORDER BY ordinal_position;
```

#### 3d. Run quality checks

For each table, run the checks below. Adapt column names to what you discovered.

Please use the guidelines outline in the scrutinize briefs:

`src/adorable_thunder/scrutinize/specific_briefs/<flow>.md`

#### 3e. Form findings

After running the checks, produce findings in this structure for each issue:

- **severity**: high / medium / low
- **table**: which table
- **field**: which column (if applicable)
- **issue**: what is wrong
- **suggestion**: what the generator should do differently

Severity guidance:
- **high**: orphaned FKs, duplicate PKs, >5% nulls on required fields, impossible date ranges, amounts ≤ 0
- **medium**: unrealistic distributions (e.g. 99% of orders in one status), suspiciously narrow numeric ranges
- **low**: minor skews, cosmetic label issues

Report a summary:
- Total findings by severity (high / medium / low)
- Top high-severity issues (issue + suggestion)
- Overall verdict

### 4. Edit generator scripts

Generator files live in:

```
src/adorable_thunder/make/record_generators/<flow>/
```

For each high-severity finding:
1. Identify which generator file owns the flagged field or table
2. Read the file
3. Make the minimal targeted fix
4. Do not touch unrelated generators

After edits, confirm what changed and what the fix addresses.
