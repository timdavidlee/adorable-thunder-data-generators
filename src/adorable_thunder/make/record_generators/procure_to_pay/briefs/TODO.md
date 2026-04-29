# Insights Wishlist TODO — procure_to_pay

Living TODO of field/data additions proposed by `/insights-wishlist`. Full runs are archived under `docs/generated/iter/procure-to-pay/`. Prune entries here as they are implemented or become irrelevant.

## 2026-04-28 run

_Top 5 implemented in the 18:46 run on 2026-04-28 — see `docs/generated/iter/procure-to-pay/2026-04-28-184640--insights-wishlist.md`. Strikethrough = wired into the generators._

### Top 5
1. ~~**purchase_orders.supplier_country + supplier_category** (high) — pair unlocks geo spend and category spend dashboards (cheap: typed enum + 2-letter country).~~
2. ~~**invoices.currency_code** (high) — PO has it, invoice doesn't; closes an oversight that blocks AP FX analytics.~~
3. ~~**invoices.goods_receipt_date + invoices.match_status** (high) — operationalizes three-way-match exception workflow already named in the scrutiny brief.~~
4. ~~**purchase_orders.gl_account + requests.spend_category** (high) — join hooks connecting P2P to R2R/B2R.~~
5. ~~**payments.payment_run_id** (high) — AP runs are the natural batching unit; enables run-cadence and treasury-timing analytics.~~

### All proposals

**requests**
- ~~**requests.spend_category** (analytics, high) — slice spend by category (IT, Pro Services, Materials, Logistics, Marketing, Facilities, Travel).~~
- **requests.approval_tier** (analytics, high) — surface the $5k/$25k/$100k tier the request hit; supports tier-driven cycle-time and controls audits.
- **requests.request_type** (analytics, medium) — `one_time / recurring / blanket / p_card`.
- **requests.priority** (behavioral, medium) — `low/normal/high/urgent` for urgency-driven cycle-time analytics.
- **requests.business_unit** (analytics, medium) — exec-level rollup above cost center.
- **requests.submitted_via** (analytics, low) — `web_portal / email / integration / mobile`.
- **requests.country** (visualization, low) — geo heatmap of requesters.

**purchase_orders**
- ~~**purchase_orders.supplier_country** (visualization, high) — geo spend, FX exposure.~~
- ~~**purchase_orders.supplier_category** (analytics, high) — supplier industry/category dimension.~~
- **purchase_orders.supplier_id** (cross-table, high) — stable id; foundation for any supplier dim.
- **purchase_orders.expected_delivery_date** (behavioral, high) — OTD %, lead-time variance, open-PO aging.
- ~~**purchase_orders.gl_account** (cross-table, high) — join hook to R2R/B2R.~~
- **purchase_orders.procurement_method** (analytics, medium) — `RFQ / RFP / single_source / contract_call_off / p_card / marketplace`.
- **purchase_orders.buyer_email** (behavioral, medium) — buyer load (distinct from request owner).
- **purchase_orders.incoterms** (analytics, low) — for cross-border POs.
- **purchase_orders.contract_id** (cross-table, low) — separates contract-call-off from one-off spend.

**invoices**
- ~~**invoices.currency_code** (analytics, high) — missing while PO has it; blocks AP FX analytics.~~
- ~~**invoices.goods_receipt_date** (behavioral, high) — third leg of three-way match.~~
- ~~**invoices.match_status** (analytics, high) — `matched / price_variance / qty_variance / blocked / unmatched`.~~
- **invoices.discrepancy_amount** (analytics, medium) — quantifies match-exception impact.
- **invoices.early_payment_discount_eligible** (analytics, medium) — pairs with `2/10 Net 30`-style terms.
- **invoices.tax_jurisdiction** (analytics, medium) — compliance / regional tax.
- **invoices.posted_to_gl_date** (behavioral, low) — close-cycle metrics.

**payments**
- ~~**payments.payment_run_id** (behavioral, high) — AP batches payments into runs; no run id today.~~
- **payments.fx_rate** (analytics, medium) — pairs with missing invoice currency for full FX-loss view.
- **payments.transaction_fee** (analytics, medium) — true cost of payment method.
- **payments.early_payment_discount_taken** (analytics, medium) — measures discount capture.
- **payments.bank_account** (behavioral, medium) — treasury concentration / bank-fee analytics.
- **payments.is_partial_payment** (analytics, low) — partial-payment classification.

### Out of scope (would need new tables)
- **Supplier dimension** — `supplier_name` is duplicated as text; a true supplier dim would carry country, category, terms, performance, certifications.
- **Goods receipt** table — three-way match presumes a separate receipt event.
- **Invoice line items** — invoices store an aggregate amount only.
