---
name: reset-schema
description: >
  Drops a Postgres schema CASCADE, recreates it, and re-grants access to postgres (superuser)
  and ai_readonly_user. Use when the user says "reset schema", "drop and recreate schema",
  "clear schema", or invokes /reset-schema. Accepts a schema name as a required argument
  (e.g. "order_to_cash", "procure_to_pay", "lead_to_opportunity", "campaign_to_conversion").
---

# Reset Schema

Drop a schema CASCADE, recreate it empty, and restore user grants.

## Steps

### 1. Ensure postgres is healthy

```bash
docker compose up -d postgres
docker compose exec postgres pg_isready -U postgres -d adorable_thunder
```

If not healthy after ~30s, stop and report the error.

### 2. Run the reset

Always pass the superuser credentials — the readonly user cannot perform DDL:

```bash
PG_USER=postgres PG_PASSWORD=postgres PG_DBNAME=adorable_thunder \
  uv run python -m adorable_thunder.make.database.reset_schema <schema>
```

Replace `<schema>` with the schema name the user specified. Valid values:

- `order_to_cash`
- `procure_to_pay`
- `lead_to_opportunity`
- `campaign_to_conversion`

### 3. Confirm completion

Report which schema was reset and that `ai_readonly_user` grants are in place.
If the user intends to load data next, suggest:

```bash
PG_USER=postgres PG_PASSWORD=postgres PG_DBNAME=adorable_thunder \
  uv run python -m adorable_thunder.make.database.inject_into_pg \
  --flow <schema> --n-samples 10_000
```
