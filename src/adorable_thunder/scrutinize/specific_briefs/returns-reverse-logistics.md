# Returns / Reverse Logistics (RMA) — Scrutiny Brief

**Date chain** (high severity): `rma_request_date ≤ shipment_date ≤ receipt_date ≤ inspection_date ≤ disposition_date`. Any inversion is a hard bug.

**Inspection gates disposition** (high severity): no `disposition` record should exist without a completed `inspection`. Dispositions without inspections indicate a generator sequencing error.

**Credit amount ceiling**: `credit_amount ≤ original_invoice_line_amount`. Credits exceeding the original amount are a hard error.

**Return window**: `shipment_date` should be within 30–90 days of the original order delivery. Returns arriving years later are unrealistic.

**Condition → disposition mapping**: `LIKE_NEW`/`GOOD` → `RESTOCK`; `FAIR` → `REFURBISH`; `DAMAGED`/`SCRAP` → `VENDOR_RETURN` or `SCRAP`. Mismatches (e.g. SCRAP condition → RESTOCK) indicate a generator wiring error.

**Return rate**: returned qty / shipped qty should be 2–5% for B2B. Rates above 20% or exactly 0% are both suspicious.

**Reason distribution**: `DEFECTIVE ~30%`, `WRONG_ITEM ~20%`, `EXCESS ~20%`, `DAMAGED_IN_TRANSIT ~15%`, other ~15%. A dataset where 80% of returns are a single reason is too skewed.

**RMA expiry compliance**: `shipment_date` must be before the RMA `expiry_date`. A return shipment sent after the RMA has expired would be rejected in reality; such records are a generator logic bug.

**Qty consistency chain**: `qty` in the disposition ≤ `qty_received` in the receipt ≤ `qty` on the RMA authorization. Each downstream record should not exceed the upstream authorized quantity.

**Restocking fee logic**: `LIKE_NEW` condition restocked items typically carry 0% restocking fee; `FAIR` condition items 10–20%; dispositions for `SCRAP` condition should have `credit_amount = 0` or reflect only salvage value. A `SCRAP` item generating a full credit is a bug.
