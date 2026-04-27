# Database

PostgreSQL running in Docker via `compose.yml`. Connection defaults are in `.env` at the project root.

## Credentials

| Role | User | Password | Use for |
|---|---|---|---|
| Superuser | `postgres` | `postgres` | Schema creation, `inject_into_pg`, any DDL |
| Read-only | `ai_readonly_user` | `not-a-password123!@#` | MCP tools (`run_sql`, `list_tables`), scrutinize agent |

The read-only user is created by `init/01_readonly_user.sh` on first container start. It has `SELECT` on all tables but cannot create schemas or write data.

## Environment variables

```
POSTGRES_DB=adorable_thunder
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
AI_READONLY_PASSWORD=not-a-password123!@#
```

The app uses `PG_HOST`, `PG_USER`, `PG_PASSWORD`, `PG_DBNAME` at runtime (defaulting to the read-only user). Pass the superuser explicitly when needed:

```bash
PG_USER=postgres PG_PASSWORD=postgres PG_DBNAME=adorable_thunder uv run python -m adorable_thunder.make.database.inject_into_pg ...
```

## Schema layout

Each flow gets its own Postgres schema:

- `procure_to_pay` — requests, purchase_orders, invoices, payments
- `order_to_cash` — quotes, sales_orders, shipments, invoices, cash_receipts, cash_applications

After a schema drop/recreate (`--drop`), the read-only user loses its grants. Re-grant with:

```bash
docker compose exec postgres psql -U postgres -d adorable_thunder \
  -c "GRANT USAGE ON SCHEMA <schema> TO ai_readonly_user; GRANT SELECT ON ALL TABLES IN SCHEMA <schema> TO ai_readonly_user;"
```
