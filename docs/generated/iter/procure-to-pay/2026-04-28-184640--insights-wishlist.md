# Insights Wishlist — procure-to-pay

## What ran

`/insights-wishlist procure-to-pay` against the `procure_to_pay` schema (1k requests, 893 POs, 471 invoices, 452 payments). Schema unchanged since the prior run — Top 5 were carried forward and implemented this time.

## What changed

### Wishlist

This run's proposals were the same Top 5 surfaced on 2026-04-28 earlier today; see [2026-04-28-181647--insights-wishlist.md](2026-04-28-181647--insights-wishlist.md) for the full per-table breakdown and out-of-scope notes. Top 5 below.

#### Top 5

1. **purchase_orders.supplier_country + supplier_category** — geo + category spend dashboards.
2. **invoices.currency_code** — closes a generation oversight (PO has it, invoice didn't).
3. **invoices.goods_receipt_date + invoices.match_status** — operationalizes three-way match.
4. **purchase_orders.gl_account + requests.spend_category** — join hooks to R2R / B2R.
5. **payments.payment_run_id** — AP run batching.

### Implemented

All five Top 5 wired in. No items skipped.

- [src/adorable_thunder/make/record_generators/procure_to_pay/requests.py](../../../../src/adorable_thunder/make/record_generators/procure_to_pay/requests.py) — added `spend_category` (8-value typed enum, weighted IT 25% / PROFESSIONAL_SERVICES 20% / MATERIALS 20% / LOGISTICS 10% / MARKETING 10% / FACILITIES 8% / TRAVEL 5% / OTHER 2%). Exported `SPEND_CATEGORIES` so downstream stages reuse the pool.
- [src/adorable_thunder/make/record_generators/procure_to_pay/purchase_orders.py](../../../../src/adorable_thunder/make/record_generators/procure_to_pay/purchase_orders.py) — added `supplier_country` (via `generate_country_codes`, GDP-weighted), `supplier_category` (inherited from the originating request's `spend_category` via new `spend_categories` parameter), and `gl_account` (via `generate_ledger_accounts(account_type="opex")`).
- [src/adorable_thunder/make/record_generators/procure_to_pay/invoices.py](../../../../src/adorable_thunder/make/record_generators/procure_to_pay/invoices.py) — added `currency_code` (inherited from PO via new `po_currency_codes` parameter), `goods_receipt_date` (uniformly sampled between `po_date` and `invoice_date` so the three-way-match date chain holds row-by-row), and `match_status` (5-value enum, weighted matched 85% / price_variance 5% / qty_variance 4% / blocked 4% / unmatched 2%).
- [src/adorable_thunder/make/record_generators/procure_to_pay/payments.py](../../../../src/adorable_thunder/make/record_generators/procure_to_pay/payments.py) — added `payment_run_id` (one shared UUID per ISO calendar week of `payment_date`).
- [src/adorable_thunder/make/record_generators/procure_to_pay/flow.py](../../../../src/adorable_thunder/make/record_generators/procure_to_pay/flow.py) — passes `spend_categories` from requests → POs and `currency_codes` from POs → invoices.

## Verification

- `ruff check` on `procure_to_pay/` — 25 errors, all pre-existing E501 line-length issues on lines this run did not modify (verified via `git stash` baseline). Per surgical-changes rule, leaving them.
- `pyright` on `procure_to_pay/` — clean (0 errors).
- Re-inject `--flow procure_to_pay --n-samples 1000 --drop` succeeded; loaded 1000 requests / 893 POs / 471 invoices / 452 payments.
- Distribution / invariant checks via SQL:
  - `requests.spend_category` mix lands within ±3% of design weights.
  - `purchase_orders.supplier_category` mirrors the upstream `requests.spend_category` distribution (active requests only).
  - `purchase_orders.supplier_country` GDP-weighted with US ~29%, CN ~17%, JP ~5%, DE ~4%.
  - `invoices.match_status` mix: matched 86%, price_variance 4%, qty_variance 4%, unmatched 3%, blocked 2%.
  - Zero rows where `invoices.goods_receipt_date < po_date` or `> invoice_date` (date-chain holds).
  - Zero rows where `invoices.currency_code <> purchase_orders.currency_code` (propagation correct).
  - 452 payments grouped into 110 distinct `payment_run_id` values (~4 payments per weekly run).

## Follow-ups

- The remaining medium / low priority items from the prior wishlist run remain in the working TODO for a future iteration.
