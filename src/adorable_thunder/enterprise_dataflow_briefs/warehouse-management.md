# Warehouse Management (WM)

**Flow:** Inbound Shipment → Receiving → Putaway → Storage → Pick → Pack → Outbound Shipment → Cycle Count

WM covers physical inventory movements within a warehouse or distribution center.

## Records

| Record | Key Fields |
|---|---|
| **Inbound Shipment** | shipment_id, carrier, tracking_number, expected_date, actual_date, origin, status |
| **Receipt Line** | receipt_id, shipment_id, sku, expected_qty, received_qty, uom, condition, put_to_location |
| **Storage Location** | location_id, warehouse, zone, aisle, rack, level, bin, sku, qty, capacity |
| **Pick List** | picklist_id, order_id, lines (sku, qty, from_location), assigned_to, status |
| **Outbound Shipment** | shipment_id, order_id, carrier, tracking_number, ship_date, destination, weight_kg, status |
| **Cycle Count** | count_id, location_id, sku, system_qty, counted_qty, variance_qty, count_date |

## Location Naming Convention

`WH{n}-{ZONE}-{AISLE}{RACK}-L{LEVEL}-B{BIN}` — e.g., `WH1-BULK-A01-L2-B04`

Common zones: `BULK`, `PICK`, `STAGING`, `COLD`, `HAZMAT`, `RETURNS`, `QUARANTINE`

## Business Rules

- **Receiving discrepancy**: received_qty ≠ expected_qty flags a shortage/overage requiring resolution before putaway
- **FIFO/FEFO**: pick from oldest receipt (FIFO) or earliest expiry (FEFO for perishables)
- **Outbound confirmation**: shipment status → `shipped` only after all pick lines are confirmed picked and packed
- **Cycle count variance**: (system_qty − counted_qty) / system_qty > 1% triggers investigation and adjustment

## Realism Benchmarks

- **Receiving accuracy**: 97–99% of lines received exactly as expected
- **Pick accuracy**: 99.5–99.9% in well-run operations; errors cause returns or customer complaints
- **Cycle count frequency**: A items (high value/velocity) monthly; B items quarterly; C items annually
- **Annual shrinkage**: 0.1–0.5% of inventory value in a well-run DC; >1% indicates a control problem
- **Location fill rate**: storage locations typically 70–85% utilized; >95% creates putaway bottlenecks

## Field Generators

`identifiers`, `carrier`, `dates`, `product_code`, `unit_of_measure`, `address` (origin/destination), `country`
