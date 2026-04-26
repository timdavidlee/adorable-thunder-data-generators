# Warehouse Management (WM) — Scrutiny Brief

**Receiving accuracy**: ~97–99% of receipt lines should have `received_qty = expected_qty`. If every single line is exact, the generator may not be modeling shortages/overages.

**Cycle count variance** (high severity): `(system_qty − counted_qty) / system_qty > 1%` should be rare (<1–2% of counts). Systematic large variances indicate a generation bug; zero variance everywhere is too perfect.

**Location fill rate**: storage locations should be 70–85% utilized overall. Locations at 100% capacity or <10% utilization at scale are unrealistic.

**FIFO/FEFO compliance**: pick orders should source from the oldest receipt (by `receipt_date`) for the same SKU/location. If picks consistently source from newer receipts when older stock is available, that's a realism issue.

**Outbound confirmation**: `shipment.status = shipped` should only appear when all associated pick lines have `status = picked`. Shipped orders with open pick lines are a bug.

**Location naming**: location IDs should follow the `WH{n}-{ZONE}-{AISLE}{RACK}-L{LEVEL}-B{BIN}` convention. Random strings or inconsistent formats indicate a generator gap.

**Zone-SKU appropriateness**: temperature-sensitive or perishable SKUs should appear only in the `COLD` zone; hazardous materials only in `HAZMAT`. Generic SKUs stored in `COLD` or `HAZMAT` locations indicate a generator zone-assignment bug.

**Capacity constraint**: `qty` stored at a location should not exceed the location's `capacity`. Locations consistently at 110%+ utilization are physically impossible.

**Inbound receipt date vs. expected date**: `actual_date` should be within ±3 days of `expected_date` for domestic shipments and ±7 days for international. Systematic gaps of weeks indicate the generator is not coupling the two fields realistically.
