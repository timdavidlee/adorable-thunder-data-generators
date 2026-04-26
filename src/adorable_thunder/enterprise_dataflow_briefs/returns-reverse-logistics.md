# Returns / Reverse Logistics (RMA)

**Flow:** Return Request → Authorization → Return Shipment → Receipt & Inspection → Disposition → Credit/Refund

RMA covers the reverse supply chain — products moving from customer back to supplier for replacement, credit, repair, or disposal.

## Records

| Record | Key Fields |
|---|---|
| **Return Authorization** | rma_id, original_order_id, request_date, return_reason, sku, qty, status, expiry_date |
| **Return Shipment** | shipment_id, rma_id, carrier, tracking_number, ship_date, origin (customer address) |
| **Return Receipt** | receipt_id, rma_id, received_date, sku, qty_received, condition_code |
| **Inspection** | inspection_id, receipt_id, inspector, inspection_date, condition_code, notes |
| **Disposition** | disposition_id, inspection_id, disposition_type, credit_amount, restocking_fee, replacement_order_id |

## Reference Values

**Return Reasons:** `DEFECTIVE`, `WRONG_ITEM_SHIPPED`, `WRONG_ITEM_ORDERED`, `DAMAGED_IN_TRANSIT`, `EXCESS_QUANTITY`, `QUALITY_ISSUE`, `END_OF_LIFE`, `VENDOR_RECALL`

**Condition Codes:** `LIKE_NEW`, `GOOD`, `FAIR`, `DAMAGED`, `SCRAP`

**Disposition Types:** `RESTOCK`, `REFURBISH`, `VENDOR_RETURN`, `SCRAP`, `DONATE`

## Business Rules

- **Return qty**: qty_received ≤ original_order_qty
- **Credit amount**: credit ≤ original invoice line amount; restocking fee (10–20%) may apply
- **Inspection gates disposition**: no disposition record without a completed inspection
- **Return window**: RMA authorization expires 30–90 days after original delivery
- **Condition → disposition mapping**: `LIKE_NEW`/`GOOD` → `RESTOCK`; `FAIR` → `REFURBISH`; `DAMAGED`/`SCRAP` → `VENDOR_RETURN` or `SCRAP`

## Realism Benchmarks

- **Return rate**: B2B 2–5% of shipped lines; electronics/tech 5–10%; industrial goods <2%
- **Reason distribution**: DEFECTIVE ~30%, WRONG_ITEM ~20%, EXCESS ~20%, DAMAGED_IN_TRANSIT ~15%, other ~15%
- **Credit turnaround**: 7–30 days from receipt to credit issuance
- **Disposition split**: ~50% restock, ~20% vendor return, ~15% refurbish, ~15% scrap
- **Date chain**: rma_request_date ≤ shipment_date ≤ receipt_date ≤ inspection_date ≤ disposition_date

## Field Generators

`identifiers`, `dates`, `amounts`, `carrier`, `address`, `product_code`, `unit_of_measure`
