# `adorable-thunder-data-generators`

Synthetic data generators for enterprise business process flows, for educational purposes. Produces realistic, relationally consistent datasets (quotes → orders → invoices → payments, etc.) and seeds them into a local Postgres database via Docker Compose.

---

## Quick Start

**Prerequisites:** [uv](https://docs.astral.sh/uv/), [Docker](https://www.docker.com/)

1. Copy the environment file and fill in credentials:
   ```bash
   cp .env.example .env
   ```

2. Spin up Postgres and seed it with sample data:
   ```bash
   docker compose up --build
   ```
   This starts a Postgres instance and runs seeders for `order_to_cash` and `procure_to_pay` (1,000 records each).

3. Connect to the database:
   ```
   host: localhost  port: 5432
   db/user/password: as set in your .env
   ```

**Running generators directly (without Docker):**
```bash
uv sync
uv run python -m adorable_thunder.make.database.inject_into_pg --flow order_to_cash --n-samples 500
uv run python -m adorable_thunder.make.database.inject_into_pg --flow procure_to_pay --n-samples 500
```

**Running tests:**
```bash
uv run pytest
```

---

## Repository Layout

```
adorable-thunder-data-generators/
│
├── compose.yml                     # Docker Compose: Postgres + seeder services
├── Dockerfile.seeder               # Image used by seeder services
├── pyproject.toml                  # Project metadata and dependencies (uv / hatch)
├── BRIEFS.md                       # Registry of every flow brief and whether it has a generator
│
├── src/adorable_thunder/
│   │
│   ├── central_cli.py              # Top-level CLI entrypoint
│   │
│   ├── make/                       # Data generation layer
│   │   ├── cli.py                  # CLI commands for generation
│   │   ├── common/                 # Shared math utilities
│   │   ├── field_generators/       # Atomic field generators (address, dates, currency, …)
│   │   ├── record_generators/      # Flow-level record generators (one subdir per flow)
│   │   │   ├── acquire_to_retire/      # Asset master → depreciation runs → disposals
│   │   │   ├── campaign_to_conversion/ # Campaigns → impressions → engagements → leads → conversions
│   │   │   ├── forecast_to_stock/      # Forecasts → inventory → stock params → replenishment
│   │   │   ├── install_to_retention/   # Installs → accounts → activation events → IAPs → cohorts
│   │   │   ├── lead_to_opportunity/    # Leads → contacts → opportunities → quotes → contracts
│   │   │   ├── order_to_cash/          # Quotes → orders → shipments → invoices → receipts → cash apps
│   │   │   ├── procure_to_pay/         # Requests → POs → invoices → payments
│   │   │   └── quote_to_cash/          # Subscriptions → contracts → recurring invoices → renewals
│   │   │   #   each flow dir contains: stage *.py files, flow.py, __init__.py, briefs/TODO.md
│   │   └── database/               # Postgres injection logic
│   │
│   ├── scrutinize/                 # AI-assisted brief review agent
│   │   ├── agent/                  # LangGraph agent definition and schemas
│   │   ├── tools/                  # Agent tools (dataset profile, flow brief lookup)
│   │   └── specific_briefs/        # Per-flow scrutiny notes (one .md per flow)
│   │
│   └── enterprise_dataflow_briefs/ # Source-of-truth design briefs for each flow
│       └── *.md                    # order-to-cash, procure-to-pay, forecast-to-stock, …
│
├── docs/generated/                 # AI-written iteration logs (one per skill invocation)
│   └── iter/<flow>/                # YYYY-MM-DD-HHMMSS--<skill>.md
│
└── tests/
    └── adorable_thunder/make/
        └── field_generators/       # Unit tests for every field generator
```

### Key concepts

| Term | What it is |
|---|---|
| **field generator** | Produces a single column value (e.g. a random address, currency code, or fiscal period) |
| **record generator** | Assembles field generators into a full document (e.g. a sales order row) with referential consistency across tables |
| **flow** | An end-to-end business process (e.g. `order_to_cash`) composed of several related record generators |
| **enterprise dataflow brief** | Markdown spec describing the tables, fields, and realistic data patterns for a flow |
| **scrutinize agent** | LangGraph agent that reviews briefs for design completeness using the Claude API |
