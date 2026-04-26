# Procure-to-Pay (P2P) — Scrutiny Brief

*Primary implemented flow. Most scrutiny effort should be invested here.*

**Date chain** (high severity): `request_date ≤ po_date ≤ invoice_date ≤ due_date ≤ payment_date`. Any inversion is a hard bug.

**Three-way match**: payments with status `paid` should only appear when the corresponding PO and invoice are also approved/matched. Paid invoices with draft or rejected POs are a flag.

**Amount integrity**: `invoice_amount ≈ po_amount` (±5–10% tolerance for FX/adjustments). Large gaps without a clear FX explanation indicate a generator bug.

**Status distribution**: approved ~55%, initiated/pending ~30%, rejected ~10%, cancelled ~5%. If >70% are `approved`, the distribution is too clean.

**Approval tiers**: requests above $5k should not all have the same single approver. Requests above $25k/$100k imply multi-level approval — flag if the same `owner_email` approves everything regardless of amount.

**Multi-currency**: ~30% of POs should be non-USD. A dataset where >90% is USD is unrealistic for a mid-large enterprise.

**Cost center population**: >95% of requests must have a non-null `cost_center`. Missing cost centers at scale indicate a generation gap.

**Cycle times**: request→PO should be 1–10 days; PO→invoice 14–90 days; invoice→payment roughly Net 30–60. Payments arriving the same day as invoices, or POs created before requests, are bugs.

**Supplier concentration**: no single supplier should account for >20% of total PO spend. A dataset where one or two suppliers dominate reflects a generator defaulting to a short list.

**Duplicate invoices**: the same `invoice_number` should not appear more than once per supplier. Duplicates are a realistic data quality issue to model, but systematic duplicates (>1%) indicate a generator bug.

**Requester ≠ approver**: the same `email` should not appear as both `requester_email` and `owner_email` (approver) on the same request record. Self-approval is a controls violation that should not appear in well-governed enterprise data.

**Payment method variety**: payment records should include a mix of methods (ACH, wire, check, card). A dataset where every payment uses the same method is unrealistic for a mid-large enterprise paying diverse suppliers.

**PO line item count**: POs should have a realistic distribution of line items (1–15). If every PO has exactly one line, the generator is likely not modeling multi-line purchasing behavior.
