# Insights Wishlist — procure-to-pay

## What ran

`/insights-wishlist procure-to-pay` against the live `procure_to_pay` schema (10k requests, 9k POs, 8.2k invoices, 7.7k payments).

## What changed

Read-only skill, no code changes. The wishlist itself follows.

### requests

- `spend_category` (text/enum, **high**) — analytics. No way to slice spend by category (IT, Professional Services, Materials, Logistics, Marketing, Facilities, Travel). Blocks the most basic procurement KPI.
- `approval_tier` (smallint, **high**) — analytics. Scrutiny brief defines $5k/$25k/$100k tiers but the data does not surface which tier a request hit; blocks tier-driven cycle-time and controls audits.
- `request_type` (text/enum, medium) — analytics. `one_time / recurring / blanket / p_card` — different procurement playbooks.
- `priority` (text/enum, medium) — behavioral. Urgency-driven cycle-time analytics.
- `business_unit` (text, medium) — analytics. Roll-up above cost-center for exec dashboards.
- `submitted_via` (text/enum, low) — channel adoption / process mining.
- `country` (text, low) — visualization. Geo heatmaps for requesters.

### purchase_orders

- `supplier_country` (text, **high**) — visualization. Unlocks geo spend, supplier diversification, FX exposure analysis.
- `supplier_category` (text/enum, **high**) — analytics. No category dimension on the supplier today.
- `supplier_id` (uuid, **high**) — cross-table. `supplier_name` repeats as free text across requests and POs; an id is the foundation for any supplier dim.
- `expected_delivery_date` (date, **high**) — behavioral. Enables OTD %, lead-time variance, open-PO aging.
- `gl_account` (text, **high**) — cross-table. Hook for joining P2P to R2R/B2R.
- `procurement_method` (text/enum, medium) — `RFQ / RFP / single_source / contract_call_off / p_card / marketplace`.
- `buyer_email` (text, medium) — buyer load and buyer-supplier relationships (distinct from request owner).
- `incoterms` (text, low) — for cross-border POs (~30% of dataset).
- `contract_id` (uuid, low) — separates contract-call-off spend from one-off.

### invoices

- `currency_code` (varchar, **high**) — analytics. PO has it, invoice doesn't. AP cannot do FX analytics or per-currency aging without this. Likely a generation oversight.
- `goods_receipt_date` (date, **high**) — behavioral. Three-way match requires PO + invoice + goods receipt; today the receipt event is only implicit.
- `match_status` (text/enum, **high**) — analytics. `matched / price_variance / qty_variance / blocked / unmatched`. Operationalizes the AP exception workflow.
- `discrepancy_amount` (numeric, medium) — analytics. Quantifies match-exception impact.
- `early_payment_discount_eligible` (boolean, medium) — analytics. Pairs with `payment_terms` like `2/10 Net 30`.
- `tax_jurisdiction` (text, medium) — compliance / tax-by-region.
- `posted_to_gl_date` (date, low) — close-cycle metrics.

### payments

- `payment_run_id` (uuid, **high**) — behavioral. AP batches payments into runs; no run id today.
- `fx_rate` (numeric, medium) — analytics. Pairs with missing invoice currency for full FX-loss analysis.
- `transaction_fee` (numeric, medium) — analytics. True cost of payment method.
- `early_payment_discount_taken` (numeric, medium) — analytics. Companion to invoice's eligible flag.
- `bank_account` (text, medium) — behavioral. Treasury concentration / bank-fee analytics.
- `is_partial_payment` (boolean, low) — partial-payment classification.

### Top 5 wishlist (highest leverage)

1. **purchase_orders.supplier_country + supplier_category** — pair unlocks geo spend and category spend dashboards. Cheap to generate (typed enum + 2-letter country).
2. **invoices.currency_code** — closes a generation oversight; without it no AP FX analytics.
3. **invoices.goods_receipt_date + invoices.match_status** — operationalizes the three-way-match control already named in the scrutiny brief.
4. **purchase_orders.gl_account + requests.spend_category** — join hooks that connect P2P to R2R/B2R.
5. **payments.payment_run_id** — AP runs are the natural batching unit; enables run-cadence and treasury-timing analytics.

### Out of scope (would need new tables)

- **Supplier dimension** — `supplier_name` is duplicated as text; a true supplier dim would carry country, category, terms, performance, certifications.
- **Goods receipt** table — three-way match presumes a separate receipt event.
- **Invoice line items** — invoices store an aggregate amount, no line detail.

## Verification

Read-only skill, no code changes. The wishlist was derived from `information_schema.columns`, distribution queries, and 5-row samples per table on the live `procure_to_pay` schema.

## Follow-ups

None. Wishlist appended to `src/adorable_thunder/make/record_generators/procure_to_pay/briefs/TODO.md` as the working list.
