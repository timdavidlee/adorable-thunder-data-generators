# Procure-to-Pay (P2P)

**Flow:** Purchase Request → Purchase Order → Goods/Services Receipt → Invoice → Payment

The P2P cycle covers everything from an internal purchase need through supplier payment. It is the primary flow currently implemented in `make/record_generators/`.

## Records

| Record | Key Fields |
|---|---|
| **Request** | request_id, document_number, request_date, requester_email, owner_email, supplier_name, amount_usd, currency_code, cost_center, status |
| **Purchase Order** | po_id, request_id, po_number, po_date, supplier_name, line_items, total_amount, payment_terms, status |
| **Invoice** | invoice_id, po_id, invoice_number, invoice_date, due_date, amount_invoiced, tax_amount, status |
| **Payment** | payment_id, invoice_id, payment_date, amount_paid, currency_code, payment_method, status |

## Status Transitions

| Record | States (ordered most → least common) |
|---|---|
| Request | `approved` → `initiated` → `pending` → `rejected` |
| Purchase Order | `approved` → `pending` → `draft` → `rejected` → `cancelled` |
| Invoice | `paid` → `received` → `pending` → `on_hold` → `cancelled` → `in_dispute` |
| Payment | `paid` → `scheduled` → `on_hold` → `cancelled` |

## Business Rules

- **Date chain**: request_date ≤ po_date ≤ invoice_date ≤ due_date ≤ payment_date
- **Amount integrity**: invoice_amount ≈ po_amount (±tolerance for FX, minor adjustments)
- **Three-way match**: payment released when PO, goods receipt, and invoice are matched and approved
- **Approval tiers**: requests above threshold require multi-level approval (thresholds typically $5k, $25k, $100k)

## Realism Benchmarks

- **Request amounts**: $1,000–$100,000 (lognormal); enterprise POs can reach $500k+
- **Status distribution**: approved ~55%, initiated/pending ~30%, rejected ~10%, cancelled ~5%
- **Cycle times**: request → PO 1–10 days; PO → invoice 14–90 days; invoice → payment Net 30–60
- **Multi-currency**: ~30% of enterprise POs are in a non-USD currency
- **Cost center population**: >95% of requests should have a cost center assigned

## Field Generators

`amounts`, `dates`, `identifiers`, `company`, `users`, `cost_center`, `currency`, `payment_terms`
