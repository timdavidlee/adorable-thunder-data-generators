# Order-to-Cash (O2C)

**Flow:** Quote → Sales Order → Fulfillment/Shipment → Invoice → Cash Receipt → Cash Application

O2C covers everything from a customer placing an order to cash being posted in the GL. It is the revenue-generating counterpart to Procure-to-Pay.

## Records

| Record | Key Fields |
|---|---|
| **Quote** | quote_id, customer_name, line_items (sku, qty, unit_price), discount_rate, expiry_date |
| **Sales Order** | order_id, order_date, customer, ship_to_address, payment_terms, line_items, total_amount, status |
| **Shipment** | shipment_id, order_id, ship_date, carrier, tracking_number, incoterms, origin, destination |
| **Invoice** | invoice_id, order_id, invoice_date, due_date, line_items, tax_amount, total_amount, status |
| **Cash Receipt** | receipt_id, invoice_id, received_date, amount_received, currency, exchange_rate |
| **Cash Application** | application_id, receipt_id, invoice_id, applied_amount, open_balance |

## Business Rules

- **Date chain**: order_date ≤ ship_date ≤ invoice_date ≤ due_date; receipt_date ≥ invoice_date
- **Amount integrity**: invoice_amount = order_amount × (1 − discount_rate) × (1 + tax_rate)
- **Partial payments**: applied_amount ≤ invoice_amount; multiple receipts can close one invoice
- **Cash application**: sum(applied_amounts) = invoice_amount when fully settled

## Realism Benchmarks

- **Order amounts**: $500–$500k for B2B enterprise; lognormal peak ~$10k
- **Discount rates**: 0–30%; most orders 0–10%; large-volume deals 15–30%
- **Tax rates**: 0% (B2B exempt in many jurisdictions); 5–25% depending on country
- **Payment terms**: Net 30 (~35%), Net 45 (~20%), Net 60 (~15%)
- **Days to pay**: on-time payers 28–32 days on Net 30; late payers 45–90; ~15% past due
- **Invoice aging mix**: <30 days (~60%), 30–60 days (~20%), 60–90 days (~10%), >90 days (~10%)

## Field Generators

`amounts`, `dates`, `identifiers`, `company` (customer), `address` (ship-to), `payment_terms`, `percentage` (tax, discount), `carrier`, `incoterms`, `currency`, `product_code`, `unit_of_measure`
