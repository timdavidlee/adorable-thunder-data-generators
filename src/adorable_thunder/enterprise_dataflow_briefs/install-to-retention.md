# Install-to-Retention (I2R)

**Flow:** Install → First Open → Account Creation → Tutorial Completion → First Meaningful Action → Day-2 Retention → Day-7 Retention → Day-30 Retention → First Purchase

I2R covers the mobile app activation, retention, and monetization funnel. Unlike linear B2B funnels, the analytical lens is **cohort-based**: users are grouped by install_date and tracked at fixed day-offsets to build retention curves. The bulk of the value of this flow lives in the cohort retention math, not in any individual user's path.

## Records

| Record | Key Fields |
|---|---|
| **Install** | install_id, device_id, platform, source, campaign_id, installed_at |
| **Session** | session_id, user_id, session_number, started_at, ended_at, screens_viewed |
| **Account** | account_id, user_id, created_at, signup_method |
| **Activation Event** | event_id, user_id, event_name, occurred_at, properties |
| **Retention Snapshot** | snapshot_id, cohort_date, day_offset, users_returned, cohort_size |
| **In-App Purchase** | iap_id, user_id, product_sku, amount, currency, purchased_at, store |

## Acquisition Sources

`ORGANIC_SEARCH`, `PAID_SEARCH`, `PAID_SOCIAL`, `INFLUENCER`, `REFERRAL`, `CROSS_PROMO`, `WEB_TO_APP`

## Activation Events (examples)

`ACCOUNT_CREATED`, `TUTORIAL_COMPLETED`, `PROFILE_SETUP`, `FIRST_MEANINGFUL_ACTION` (app-specific: first save, first match, first message, first track played)

## Business Rules

- **Date chain**: install_date ≤ first_open ≤ account_created ≤ tutorial_complete ≤ first_meaningful_action ≤ first_purchase
- **Retention math**: dN_retention = users_active_on_day_N / cohort_size; reported as decimal (0.25) or percent (25%), consistent within a dataset
- **Cohort definition**: cohort_date = install_date; day_offset measured in calendar days (not session count)
- **Activation gate**: users who don't complete tutorial within 24h have 3–5× the churn rate of completers
- **Status transitions**: device `installed` → `activated` (first open) → `registered` → `engaged` (≥3 sessions) → `paying`

## Realism Benchmarks

- **Install → first open**: 70–90% (organic), 60–80% (paid)
- **Retention curves**: Day-1 25–40%; Day-7 10–20%; Day-30 3–8% for typical consumer apps; top performers run 2–3× higher at every offset
- **Tutorial completion**: 50–75% of first-opens; non-completers churn at 3–5× the rate of completers
- **Conversion to paying**: 1–5% for free-to-play games; 5–15% for premium utility apps; 0.5–2% for ad-supported social
- **ARPDAU** (avg revenue per daily active user): $0.05–$0.50 for casual games; $1–$5 for top-grossing titles
- **Platform split**: iOS 25–45%, Android 55–75% by install volume in most markets; iOS users spend 1.5–3× more

## Field Generators

`identifiers`, `dates`, `amounts`, `currency`, `country`, `percentage` (retention, conversion rates), `person`
