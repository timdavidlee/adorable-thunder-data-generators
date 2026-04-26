# Subscription / Quote-to-Cash (Q2C)

**Flow:** Quote → Contract → Subscription Activation → Recurring Invoice → Payment → Renewal or Churn

Q2C governs recurring revenue businesses — SaaS, managed services, usage-based billing. Revenue is recognized ratably over the subscription term, not at point of delivery.

## Records

| Record | Key Fields |
|---|---|
| **Subscription** | sub_id, customer_id, plan, billing_cycle, mrr, start_date, end_date, status |
| **Contract** | contract_id, sub_id, term_months, total_value, payment_terms, auto_renew, signed_date |
| **Recurring Invoice** | invoice_id, sub_id, invoice_date, billing_period_start, billing_period_end, amount, status |
| **Usage Record** | usage_id, sub_id, period, metric (seats/API_calls/GB), quantity, unit_price, amount |
| **Renewal** | renewal_id, sub_id, renewal_date, new_term_months, new_mrr, expansion_amount, status |

## Subscription Plans

| Tier | Typical MRR/Customer | Billing Cycle |
|---|---|---|
| Starter / Free | $0–$100 | Monthly |
| Professional | $100–$2,000 | Monthly or Annual |
| Business | $2,000–$10,000 | Annual |
| Enterprise | $10,000–$100,000+ | Annual (custom) |

## Business Rules

- **Invoice cadence**: invoice_date = subscription_start + N × billing_cycle_days
- **ARR = MRR × 12**: annual recurring revenue is a derived metric, not independently stored
- **Pro-rated billing**: mid-cycle additions/removals generate a pro-rated charge for the partial period
- **Churn**: status → `churned` after non-payment past grace period or explicit cancellation; no renewal record
- **Expansion revenue**: MRR increase from upsell is tracked separately from new business MRR

## Realism Benchmarks

- **Monthly churn rate**: 1–3% healthy SaaS; >5% indicates retention issues
- **Net Revenue Retention (NRR)**: >100% means expansion > churn; healthy = 110–130%
- **Renewal rate**: monthly subscriptions 85–90%; annual 90–95%
- **Expansion rate**: 15–30% of existing customers upgrade in any given year
- **Payment timing**: enterprise annual invoices Net 30; monthly SMB typically auto-pay within 3 days

## Field Generators

`identifiers`, `dates`, `amounts`, `company`, `payment_terms`, `country`, `percentage` (churn, expansion rates), `fiscal_period`
