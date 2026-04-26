# Plan-to-Produce (P2P) / Make-to-Stock

**Flow:** Demand Planning → MRP Run → Production Order → BOM Explosion → Work Order → Goods Receipt → Inventory Update

Plan-to-Produce translates demand signals into production schedules, consuming raw materials and producing finished goods. Distinct from Procure-to-Pay ("P2P" is an overloaded abbreviation — this is the manufacturing variant).

## Records

| Record | Key Fields |
|---|---|
| **Demand Plan** | plan_id, sku, period, planned_qty, uom, source (`forecast`/`order`/`safety_stock`) |
| **Production Order** | order_id, sku, qty_ordered, qty_produced, start_date, end_date, status, work_center |
| **BOM Line** | bom_id, parent_sku, component_sku, qty_per, uom, effective_date |
| **Work Order** | work_order_id, production_order_id, operation, work_center, planned_hours, actual_hours, status |
| **Goods Receipt** | receipt_id, production_order_id, sku, qty_received, receipt_date, batch_id |

## Business Rules

- **BOM balance**: for each production run, component_consumed = qty_ordered × bom_qty_per for every BOM line
- **Date chain**: production start_date < end_date; receipt_date ≥ end_date
- **Status transitions**: `planned` → `released` → `in_progress` → `completed` / `cancelled`
- **Yield**: qty_produced ≤ qty_ordered; scrap = qty_ordered − qty_produced
- **MRP logic**: planned production ≥ demand − current_stock + safety_stock

## Realism Benchmarks

- **Batch sizes**: cluster around standard pack multiples (50, 100, 500, 1,000)
- **Cycle times**: discrete manufacturing 1–5 days; process manufacturing 1–30 days
- **Scrap / yield loss**: 1–5% for mature processes; higher for new product introduction
- **Work center utilization**: 70–85% is healthy; >90% indicates a capacity constraint
- **Planned vs. actual hours**: actual typically 95–110% of planned; large deviations flag inefficiency

## Field Generators

`product_code`, `amounts`, `dates`, `identifiers`, `unit_of_measure`, `fiscal_period`, `cost_center`
