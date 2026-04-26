# Forecast-to-Stock (F2S)

**Flow:** Demand Sensing → Statistical Forecast → Inventory Position → Replenishment Signal → PO or Production Order → Goods Receipt

F2S governs inventory replenishment — continuously comparing demand forecasts against available stock and triggering orders to prevent stockouts or overstock.

## Records

| Record | Key Fields |
|---|---|
| **Inventory Position** | record_id, sku, location, on_hand_qty, on_order_qty, available_qty, as_of_date |
| **Forecast** | forecast_id, sku, period, forecast_qty, uom, model (`statistical`/`manual`/`consensus`) |
| **Stock Parameters** | sku, location, safety_stock_qty, reorder_point, economic_order_qty, lead_time_days |
| **Replenishment Order** | order_id, sku, location, trigger_date, order_qty, expected_receipt_date, status |

## Business Rules

- **Replenishment trigger**: fires when available_qty ≤ reorder_point
- **Order quantity**: order_qty ≥ (reorder_point − on_hand_qty + safety_stock_qty); rounded up to economic_order_qty
- **Available qty**: available_qty = on_hand_qty + on_order_qty − committed_qty
- **Expected receipt**: expected_receipt_date = trigger_date + lead_time_days (business days)
- **Safety stock**: sized to cover demand uncertainty during lead time; typically 1–2 weeks of average demand

## Realism Benchmarks

- **Lead times**: domestic suppliers 2–14 days; international 14–90 days; contract manufacturers 30–120 days
- **Safety stock coverage**: 1–4 weeks of average demand; volatile SKUs carry higher buffers
- **Fill rate target**: 95–98% line fill rate is healthy for enterprise
- **Stockout rate**: <2% SKU-days in stockout is a healthy target
- **Overstock flag**: on_hand > 90-day demand is excess inventory; common causes: demand collapse, forecast error

## Field Generators

`product_code`, `amounts`, `dates`, `identifiers`, `unit_of_measure`, `country` (location)
