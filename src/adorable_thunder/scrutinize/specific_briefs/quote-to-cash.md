# Subscription / Quote-to-Cash (Q2C) — Scrutiny Brief

**Invoice cadence** (high severity): `invoice_date` for recurring invoices should be spaced exactly `billing_cycle_days` apart. Gaps or overlaps in billing periods indicate a generator timing bug.

**ARR derivation**: `ARR = MRR × 12`. If ARR is stored as a field, verify it matches. Mismatches indicate a derivation error.

**Churn sequencing**: churned subscriptions (`status = churned`) should have no renewal records and no invoices after the churn date. Invoices post-churn are a hard bug.

**Monthly churn rate**: 1–3% of active subscriptions churning per month is healthy. A dataset with 0% churn is unrealistic; >10% monthly churn indicates a generator parameter error.

**Pro-ration math**: mid-cycle additions/removals should generate a pro-rated charge = `MRR × (days_remaining / days_in_period)`. Charges that don't match this formula are a bug.

**NRR signal**: check whether expansion revenue (upsell) + new MRR − churned MRR nets to a plausible NRR of 100–130%. Heavily negative NRR (MRR shrinking every period) suggests churn is miscalibrated.

**Billing period non-overlap**: consecutive recurring invoices for the same subscription should have `billing_period_end` of invoice N equal to `billing_period_start` of invoice N+1. Overlaps or gaps between billing periods indicate a generator timing bug.

**Auto-renew behavior**: subscriptions with `auto_renew = True` should have a renewal record generated before `end_date`. Subscriptions with `auto_renew = False` that expire without a renewal record should transition to `churned`. Active subscriptions past `end_date` with no renewal and no churn status are a hard bug.

**Plan-MRR consistency**: MRR amounts should match the subscription plan tier — Starter $0–$100, Professional $100–$2k, Business $2k–$10k, Enterprise $10k+. A `Starter` plan with $50k MRR, or an `Enterprise` plan at $50 MRR, indicates the generator is not coupling plan and amount correctly.
