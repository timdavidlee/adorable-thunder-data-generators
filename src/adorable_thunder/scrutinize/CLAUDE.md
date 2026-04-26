# scrutinize

LLM-powered agent that receives generated datasets from `make/` and evaluates how realistic they look as real-world procurement/finance data. Returns structured feedback and suggestions for improving the generators.

## Key assumptions

- **Business size**: mid-to-large enterprise (500–10,000 employees). This means diverse supplier bases, multi-currency spend, layered approval hierarchies, and dedicated procurement/finance teams — not a small business where one person buys everything.
- **Product/supplier variety**: a realistic dataset should span multiple industries and spend categories (IT, logistics, materials, professional services, etc.). A dataset where 90% of suppliers are from one industry is a red flag.
- **Schema completeness**: fields like `country`, `cost_center`, `currency_code`, `requester_email`, and `owner_email` should be populated for the majority of records — sparse optional fields are realistic for edge cases only, not the norm at this business scale.

## What this module does

The scrutinizer is a **read-only critic** — it does not generate or modify data. It:

1. Queries generated records directly from a PostgreSQL database
2. Evaluates realism across several dimensions (see below)
3. Returns structured findings: what looks off, why, and what the generator should do differently

## Upstream context

Generated data comes from `make/generators/purchase_order_flow/`. The primary flow is:
- **Requests** → Purchase Orders → Invoices → Payments
- Each record has amounts (USD + local currency), dates, statuses, supplier names, user emails, and identifiers
- Reference data (company names, user emails, cost centers, ledger accounts) lives in `make/reference_data/` — all fictional, no real entities

## What "realistic" means here

Realism = statistical and semantic plausibility for a mid-sized enterprise procurement workflow. Flag things like:

- **Amount distributions**: are amounts implausibly uniform? Real PO amounts cluster around common spend tiers (e.g. $500, $5k, $50k thresholds for approval workflows)
- **Status ratios**: e.g. if 80% of requests are "approved" that may be too clean; real data has noise, holds, rejections
- **Date logic**: completed_date before request_date, payments before invoices, unrealistic cycle times
- **Cross-field consistency**: currency codes that don't match supplier regions, local amounts that don't convert correctly at plausible FX rates
- **User patterns**: same email appearing as requester and approver on the same record; emails not matching the supplier's company domain pool
- **Identifier format**: document numbers that don't follow realistic sequential or prefix conventions
- **Supplier/product coherence**: supplier names paired with products from a different industry
- **Missing Fields**: 

## Output

Return findings as structured objects (Pydantic models), not free-form prose. Each finding should have:
- `field` — the column or field being flagged
- `issue` — what's wrong
- `suggestion` — what the generator should change (specific and actionable)
- `severity` — `low` / `medium` / `high`

## Flow briefs

Business rules, realism benchmarks, and expected schemas for every supported flow — the ground truth this agent evaluates against:

@../enterprise_dataflow_briefs/CLAUDE.md

## Agent design guidance

- Use the Claude API (`anthropic` SDK) with tool use for structured output
- Query a representative sample (50–200 rows) from PostgreSQL using `TABLESAMPLE` or `ORDER BY RANDOM() LIMIT` — the agent infers distribution from the sample, not the full table
- Prompt should include domain context (this is procurement data for a mid-sized enterprise) so the model doesn't hallucinate irrelevant standards
- One agent call per table/dataset type (requests, POs, invoices, payments) — don't mix schemas in one call
- Keep the system prompt short; let the structured output schema do the heavy lifting
