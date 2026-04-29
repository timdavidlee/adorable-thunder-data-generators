# insights-wishlist — forecast-to-stock — 2026-04-28

## What ran

`/insights-wishlist forecast-to-stock` against the existing `forecast_to_stock` schema (10k stock_parameters, 40k forecasts, 30k inventory_positions, 9.1k replenishment_orders).

## What changed

### Wishlist

The flow is mechanically sound (replenishment trigger logic, EOQ rounding, lead-time math) but analytically threadbare: every dollar/cost dimension is missing, every after-the-fact outcome is missing, and every product/supplier dimension is missing.

**stock_parameters**

- `unit_cost_usd` (NUMERIC, **high**, analytics) — unlocks inventory valuation and $-weighted ABC; cost dimension is entirely absent.
- `product_category` (TEXT, **high**, analytics) — every SKU is `PROD-NNNNN` with no category; blocks category-mix analysis.
- `abc_class` (TEXT, **high**, analytics) — Pareto segmentation is the single most-used inventory cut; absent.
- `supplier_id` + `supplier_name` (UUID + TEXT, **high**, cross-table) — `supplier_type` exists but no supplier identity; can't compute supplier OTD or spend.
- `demand_variability_cv` (NUMERIC, medium, analytics) — flags volatile vs stable SKUs.
- `service_level_target` (NUMERIC, medium, analytics) — driver behind safety stock sizing.
- `currency_code` (VARCHAR(3), low, analytics) — local-currency cost reporting.
- `last_review_date` (DATE, low, behavioral) — flags stale parameter tunings.

**forecasts**

- `actual_qty` (INTEGER, **high**, analytics) — without an actual, no MAPE/bias; the most-requested DP analysis.
- `forecast_horizon_days` (INTEGER, medium, analytics) — short vs long horizon segmentation.
- `forecast_version` (INTEGER, medium, behavioral) — forecast-revision tracking.
- `created_by_email` (TEXT, low, analytics) — accountability for `manual` and `consensus` forecasts.

**inventory_positions**

- `inventory_value_usd` (NUMERIC, **high**, analytics — paired with `unit_cost_usd`) — drives working-capital metrics.
- `stockout_flag` (BOOLEAN, medium, analytics) — cheap derived field; simplifies stockout-rate dashboards.
- `days_of_supply` (NUMERIC, medium, analytics) — universal supply-chain KPI.
- `oldest_receipt_date` (DATE, medium, behavioral) — FIFO aging / obsolescence.

**replenishment_orders**

- `actual_receipt_date` (DATE nullable, **high**, behavioral) — supplier OTD% and lead-time variance.
- `total_cost_usd` (NUMERIC, medium, analytics) — replenishment $$ tie-out.
- `urgency` (TEXT enum, medium, behavioral) — separates planned vs stockout-driven orders.
- `transport_mode` (TEXT enum, medium, analytics) — correlates lead-time with freight cost.

### Top 5

1. `stock_parameters.unit_cost_usd` + `inventory_positions.inventory_value_usd` (paired, high) — adds $ dimension everywhere.
2. `stock_parameters.product_category` + `stock_parameters.abc_class` (paired, high) — most-used segmentation cuts.
3. `replenishment_orders.actual_receipt_date` (high) — supplier OTD analytics.
4. `stock_parameters.supplier_id` + `stock_parameters.supplier_name` (paired, high) — supplier-level analytics.
5. `forecasts.actual_qty` (high) — MAPE / bias / model comparison.

### Implemented

All five Top 5 slots wired into the generators:

- [src/adorable_thunder/make/record_generators/forecast_to_stock/stock_parameters.py](../../../../src/adorable_thunder/make/record_generators/forecast_to_stock/stock_parameters.py) — added `product_category`, `abc_class`, `unit_cost_usd`, `supplier_id`, `supplier_name` columns and DDL. ABC follows ~20/30/50 weights with cost scaled by class (A high cost, C low). Suppliers drawn from a fixed ~150-name pool partitioned by `supplier_type`.
- [src/adorable_thunder/make/record_generators/forecast_to_stock/inventory_positions.py](../../../../src/adorable_thunder/make/record_generators/forecast_to_stock/inventory_positions.py) — added `inventory_value_usd` derived as `on_hand_qty × unit_cost_usd`; threaded the cost from `stock_parameters` through `flow.py`.
- [src/adorable_thunder/make/record_generators/forecast_to_stock/replenishment_orders.py](../../../../src/adorable_thunder/make/record_generators/forecast_to_stock/replenishment_orders.py) — added `actual_receipt_date` populated only for `received` status (NULL otherwise) with realistic ±lead-time-fraction noise around `expected_receipt_date`.
- [src/adorable_thunder/make/record_generators/forecast_to_stock/forecasts.py](../../../../src/adorable_thunder/make/record_generators/forecast_to_stock/forecasts.py) — added `actual_qty` populated with `avg_daily_demand × ~30 × independent noise` so MAPE values come out in the realistic 10–30% range; threaded `avg_daily_demand` argument from the flow.

## Verification

- `uv run ruff check src/adorable_thunder/make/record_generators/forecast_to_stock/` — clean.
- `uv run pyright src/adorable_thunder/make/record_generators/forecast_to_stock/` — clean.
- `PG_USER=postgres ... uv run python -m adorable_thunder.make.database.inject_into_pg --flow forecast_to_stock --n-samples 1000 --drop` — re-injected without errors; row counts match prior run shape (4 stages, expected scale).
- Spot-checked: ABC distribution ≈ 20/30/50, supplier_type↔supplier_name partition holds, `actual_receipt_date` only present for `status='received'`, `inventory_value_usd = on_hand_qty × unit_cost_usd` in random row sample.

## Follow-ups

Out-of-scope items (would need new tables, not new fields) that surfaced during profiling:

- A `goods_receipts` event table (one row per `received` order with putaway location + receipt qty).
- A `demand_history` daily-grain table — would let `actual_qty` on forecasts be derived rather than synthetically populated.
- A `supplier_master` dimension — once `supplier_id` lives on multiple SKUs, breaking it out into its own table is the natural next move.
