# Order-to-Cash (O2C) — Scrutiny Brief

**Date chain** (high severity): `order_date ≤ ship_date ≤ invoice_date ≤ due_date`; `receipt_date ≥ invoice_date`. Receipts before invoices or shipments after invoices are hard bugs.

**Amount integrity**: `invoice_amount = order_amount × (1 − discount_rate) × (1 + tax_rate)`. Verify the math holds across a sample; rounding errors >$1 are a flag.

**Tax rates**: B2B enterprise often has 0% tax (exempt); any record with >25% tax is suspicious unless the country justifies it. Mixing taxed and tax-exempt records on the same customer without differentiation is a flag.

**Partial payments**: multiple `cash_receipt` records can and should close a single invoice. If every invoice is closed by exactly one receipt, the generator is probably not modeling partial payment behavior.

**Days to pay**: on-time payers should be within 28–32 days of Net 30 due date. ~15% of invoices should be past due. A dataset where 100% of invoices are paid exactly on the due date is unrealistic.

**Invoice aging**: expect ~60% under 30 days, ~20% 30–60, ~10% 60–90, ~10% >90 days old in an open AR snapshot.

**Cash application math**: `open_balance = invoice_amount − sum(applied_amounts)` across all cash application records for that invoice. Mismatches indicate a derivation bug.

**Discount rate distribution**: discount rates should vary across orders — not all 0% (no one ever discounts) and not all the same rate. Large-volume orders should skew toward higher discounts (15–30%); most orders 0–10%.

**Customer concentration**: no single customer should account for >25% of total order revenue. Uniform customer distribution across orders is also unrealistic — some customers should order more frequently or at higher values.

**Incoterms on international orders**: shipments where `origin country ≠ destination country` should carry an incoterms code. Domestic shipments typically do not. Missing incoterms on cross-border records is a gap.
