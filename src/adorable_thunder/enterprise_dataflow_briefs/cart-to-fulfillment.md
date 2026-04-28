# Cart-to-Fulfillment (C2F)

**Flow:** Discovery → Product Detail → Cart → Checkout → Payment → Confirmation → Fulfillment

C2F covers the consumer e-commerce flow — anonymous browsing through paid order through shipment. It is the B2C counterpart to `order-to-cash`, which models B2B sales orders with quotes, contracts, and Net-N payment terms; C2F instead emphasizes anonymous funnel behavior, cart abandonment, and at-checkout payment capture.

## Records

| Record | Key Fields |
|---|---|
| **Product View** | view_id, anonymous_id, sku, viewed_at, source, session_id |
| **Cart** | cart_id, anonymous_id, line_items, created_at, last_updated_at, status |
| **Checkout Session** | checkout_id, cart_id, started_at, completed_at, abandoned, payment_method_attempted |
| **Order** | order_id, customer_id, ordered_at, line_items, subtotal, shipping, tax, total, status |
| **Payment** | payment_id, order_id, amount_charged, processor, authorized_at, captured_at, status |
| **Shipment** | shipment_id, order_id, carrier, tracking_number, shipped_at, delivered_at, address |

## Order Status Transitions

`placed` → `paid` → `picked` → `packed` → `shipped` → `delivered` → `returned`/`refunded`

## View Sources

`SEARCH`, `CATEGORY_BROWSE`, `RECOMMEND`, `EMAIL`, `PAID_AD`, `DIRECT`, `RETARGETING`

## Business Rules

- **Date chain**: product_view ≤ cart_created ≤ checkout_started ≤ order_placed ≤ payment_captured ≤ shipped ≤ delivered
- **Amount integrity**: order_total = subtotal − discount + shipping + tax; payment auth ≤ order_total, capture = order_total
- **Inventory hold**: cart-to-checkout window holds stock for N minutes; expired carts release inventory back to available pool
- **Abandonment classification**: a checkout_session with started_at but no completed_at after T minutes is `abandoned`; abandonment-recovery emails target these
- **Return window**: returns accepted within 30–90 days of delivery; outside window flags as exception

## Realism Benchmarks

- **Funnel conversion**: view → cart-add 5–15%; cart-add → order 30–50%; overall conversion 1–4% of sessions
- **Cart abandonment**: 60–80% of carts abandon; abandonment-recovery email recovers 5–15%
- **Avg order value**: $40–$120 for general retail; $80–$300 for apparel; $200+ for home goods
- **Shipping mix**: standard 60–75%, expedited 15–25%, overnight 5–10%
- **Return rate**: 8–15% for general retail; 20–35% for apparel (size / fit returns); <5% for grocery
- **Payment auth failure**: 2–5% of attempted payments; higher on first-purchase customers and BNPL methods

## Field Generators

`identifiers`, `dates`, `amounts`, `product_code`, `unit_of_measure`, `address`, `carrier`, `country`, `percentage` (tax, conversion, return rates), `person`
