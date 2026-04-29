# Insights Wishlist TODO — forecast_to_stock

Living TODO of field/data additions proposed by `/insights-wishlist`. Full runs are archived under `docs/generated/iter/forecast-to-stock/`. Prune entries here as they are implemented or become irrelevant.

## 2026-04-28 run

### Top 5
1. ~~**stock_parameters.unit_cost_usd + inventory_positions.inventory_value_usd** (high) — adds $ dimension to inventory; unlocks working capital, $-weighted ABC, $-overstock.~~
2. ~~**stock_parameters.product_category + stock_parameters.abc_class** (high) — most-used inventory segmentation cuts; foundational for any dashboard.~~
3. ~~**replenishment_orders.actual_receipt_date** (high) — supplier OTD%, lead-time variance, expediting analysis.~~
4. ~~**stock_parameters.supplier_id + stock_parameters.supplier_name** (high) — supplier-level analytics flow through every replenishment via SKU join.~~
5. ~~**forecasts.actual_qty** (high) — MAPE / forecast bias / model comparison.~~

### All proposals
- ~~**stock_parameters.unit_cost_usd** (analytics, high) — inventory valuation, $-weighted ABC; cost dimension currently absent.~~
- ~~**stock_parameters.product_category** (analytics, high) — every SKU is `PROD-NNNNN` with no category dimension.~~
- ~~**stock_parameters.abc_class** (analytics, high) — Pareto segmentation; A/B/C ~20/30/50 by value.~~
- ~~**stock_parameters.supplier_id + supplier_name** (cross-table, high) — `supplier_type` exists but no supplier identity.~~
- **stock_parameters.demand_variability_cv** (analytics, medium) — CV tags volatile vs stable SKUs.
- **stock_parameters.service_level_target** (analytics, medium) — 95/98/99% target driving safety stock sizing.
- **stock_parameters.currency_code** (analytics, low) — local-currency cost reporting.
- **stock_parameters.last_review_date** (behavioral, low) — flags stale parameter tunings.
- ~~**forecasts.actual_qty** (analytics, high) — enables MAPE, bias, model accuracy comparison.~~
- **forecasts.forecast_horizon_days** (analytics, medium) — short (≤30d) vs long (90d+) horizon segmentation.
- **forecasts.forecast_version** (behavioral, medium) — forecast-revision tracking across versions.
- **forecasts.created_by_email** (analytics, low) — accountability for manual/consensus forecasts.
- ~~**inventory_positions.inventory_value_usd** (analytics, high) — `on_hand_qty × unit_cost`; working-capital KPI.~~
- **inventory_positions.stockout_flag** (analytics, medium) — derived but cheap; simplifies stockout dashboards.
- **inventory_positions.days_of_supply** (analytics, medium) — `on_hand / avg_daily_demand`; universal supply-chain KPI.
- **inventory_positions.oldest_receipt_date** (behavioral, medium) — FIFO aging / obsolescence reporting.
- ~~**replenishment_orders.actual_receipt_date** (behavioral, high) — supplier OTD KPI; only populated for `received`.~~
- **replenishment_orders.total_cost_usd** (analytics, medium) — `order_qty × unit_cost`; ties replenishment to spend.
- **replenishment_orders.urgency** (behavioral, medium) — routine/expedite/emergency; emergency rate signals plan quality.
- **replenishment_orders.transport_mode** (analytics, medium) — road/ocean/air/rail; correlates lead-time with freight cost.

Out of scope (would need new tables): goods_receipts event table, daily-grain demand_history, supplier_master dimension.
