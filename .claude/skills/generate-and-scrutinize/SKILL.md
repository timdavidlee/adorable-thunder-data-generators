---
name: generate-and-scrutinize
description: >
  Runs one full generate→scrutinize→fix iteration cycle for an enterprise dataflow: ensures
  postgres is healthy, drops and regenerates the schema with fresh data, scrutinizes the
  result, and edits the generator scripts to fix the top findings. Use when the user says
  "generate and scrutinize", "run the cycle", "iterate on the generators", or invokes
  /generate-and-scrutinize. Accepts an optional flow argument (order_to_cash, procure_to_pay);
  defaults to order_to_cash.
---

# Generate and Scrutinize

One iterative cycle: ensure DB → generate → scrutinize → fix generators.

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

`--drop` tears down the existing schema and recreates it:

```bash
uv run python -m adorable_thunder.make.database.inject_into_pg \
  --flow <flow> --n-samples 10_000 --drop
```

Valid flow values: `order_to_cash`, `procure_to_pay`  
Default: `order_to_cash`

### 3. Scrutinize

```bash
uv run python -m adorable_thunder.scrutinize <flow>
```

Capture the JSON output. Summarise:
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
