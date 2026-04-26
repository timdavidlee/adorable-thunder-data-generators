# Forecast-to-Stock (F2S) — Scrutiny Brief

**Available qty math** (high severity): `available_qty = on_hand_qty + on_order_qty − committed_qty`. Mismatches indicate a generator field derivation bug.

**Replenishment trigger**: replenishment orders should only appear when `available_qty ≤ reorder_point` as of `trigger_date`. Orders placed when stock is well above the reorder point are a logic bug.

**Order quantity sizing**: `order_qty` should satisfy `order_qty ≥ (reorder_point − on_hand_qty + safety_stock_qty)`, rounded up to `economic_order_qty`. Undersized orders that won't cover the gap are a bug.

**Lead time compliance**: `expected_receipt_date ≈ trigger_date + lead_time_days` (business days). Domestic suppliers 2–14 days; international 14–90 days. Receipts expected faster than plausible lead times are a flag.

**Stockout detection**: SKU-days with `on_hand_qty = 0` and no `on_order_qty` should be <2% of total. Excessive stockouts suggest the replenishment logic is too slow or thresholds are too low.

**Overstock flag**: `on_hand_qty > 90-day average demand` indicates excess inventory. A dataset with zero overstock is unrealistic; >20% of SKUs in overstock suggests demand is too low relative to order quantities.

**Non-negative inventory**: `on_hand_qty` should never be negative. Negative on-hand is physically impossible and indicates the generator is not enforcing a floor when decrementing stock.

**On-order consistency**: `on_order_qty` in the inventory position record should match the sum of open (non-received) replenishment order quantities for that SKU × location. Discrepancies indicate the two record types are being generated independently without cross-referencing.

**Forecast model distribution**: forecast records should include a realistic mix of `statistical`, `manual`, and `consensus` models. A dataset where every forecast uses one model indicates the generator is not varying the source type.
