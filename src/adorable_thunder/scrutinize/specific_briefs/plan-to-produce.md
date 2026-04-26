# Plan-to-Produce (P2P / MtS) — Scrutiny Brief

**BOM balance** (high severity): for each production order, `component_consumed = qty_ordered × bom_qty_per` for every BOM line. Under- or over-consumption that isn't explained by scrap is a generator bug.

**Date chain** (high severity): `production start_date < end_date`; `receipt_date ≥ end_date`. Goods received before production ends, or start after end, are hard bugs.

**Yield / scrap**: `qty_produced ≤ qty_ordered`; scrap rate should be 1–5% for mature processes. Zero scrap across all orders is unrealistic; >20% scrap is a red flag.

**Batch sizes**: `qty_ordered` should cluster around standard pack multiples (50, 100, 500, 1,000). Random fractional quantities like 73 or 241 suggest the generator isn't modeling standard batch logic.

**Work center utilization**: actual_hours / planned_capacity per work center should be 70–85%. Consistently >95% indicates a constraint that would stop production in reality; <50% is also suspicious.

**Status transitions**: only `completed` and `cancelled` orders should have a `receipt_date`. Open `in_progress` orders with receipts are a bug.

**Goods receipt qty vs. qty_produced**: `qty_received` in the goods receipt should equal `qty_produced`, not `qty_ordered`. Receiving more than was produced is physically impossible and indicates the generator is using the wrong source field.

**Planned vs. actual hours**: `actual_hours / planned_hours` per work order should be 95–110% for a stable process. Ratios below 50% or above 200% indicate the generator is not coupling the two fields realistically.

**BOM effective date validity**: BOM lines used to compute component consumption should have `effective_date ≤ production_order.start_date`. Using an expired or future BOM version for a production order is a generator logic gap.
