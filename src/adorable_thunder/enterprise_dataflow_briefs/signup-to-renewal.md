# Signup-to-Renewal (S2R)

**Flow:** Ad/Content Marketing → Landing Page → Email Capture → Free Trial Signup → Onboarding Completion → First Value Moment → Repeated Usage → Trial-to-Paid Conversion → Upgrade Tier → Renewal

S2R covers the SaaS product-led growth funnel — from marketing touch through paid expansion and renewal. It bridges `campaign-to-conversion` (marketing top-of-funnel attribution) and `quote-to-cash` (recurring billing back-end), with a focus on the activation, retention, and expansion behavior that connects them.

## Records

| Record | Key Fields |
|---|---|
| **Marketing Touch** | touch_id, anonymous_id, channel, campaign_id, landing_page, timestamp |
| **Email Lead** | lead_id, anonymous_id, email, captured_at, source_touch_id |
| **Trial Signup** | trial_id, account_id, plan, signup_date, trial_length_days, source_lead_id |
| **Onboarding Step** | step_id, account_id, step_name, completed_at, time_to_complete_seconds |
| **Activation Event** | event_id, account_id, event_name, timestamp, value |
| **Conversion** | conversion_id, trial_id, converted_at, paid_plan, mrr, payment_method |
| **Subscription Change** | change_id, account_id, change_type, effective_date, mrr_delta |
| **Renewal** | renewal_id, account_id, renewal_date, new_term_months, churned, reason_code |

## MRR Change Types

`NEW` (new logo conversion), `EXPANSION` (upsell, seat add), `CONTRACTION` (downgrade, seat reduction), `CHURN` (cancellation), `REACTIVATION` (win-back)

## Business Rules

- **Date chain**: marketing_touch ≤ email_capture ≤ trial_signup ≤ onboarding_completed ≤ first_value ≤ conversion ≤ renewal
- **Activation gate**: accounts that don't reach onboarding completion within N days have <5% conversion rate — this should be visible in the data
- **MRR continuity**: post-conversion MRR ≥ trial-implied MRR; downgrades reduce MRR but don't end the subscription
- **Net retention math**: net_retention = (start_mrr + expansion − contraction − churn) / start_mrr
- **Status transitions**: account `lead` → `trial` → `paid` → `expanded` / `churned` / `lapsed`

## Realism Benchmarks

- **Email capture → trial signup**: 10–25%; trial → paid: 15–25% for self-serve, 30–50% with onboarding support
- **Time to first value**: median 5–30 min for tools; 1–7 days for collaboration / team products
- **Onboarding completion**: 40–70% within first session; drops to 20–40% if not completed in 24h
- **Renewal rate**: 85–95% annual for B2B; 70–85% monthly self-serve
- **Net Revenue Retention**: 100–130% healthy; expansion accounts for 20–40% of total growth
- **Trial length effect**: 14-day trials convert at 1.5–2× the rate of 30-day trials in self-serve segments

## Field Generators

`identifiers`, `dates`, `amounts`, `person`, `company`, `country`, `percentage` (conversion, retention, expansion rates), `payment_terms`, `fiscal_period`
