# Install-to-Retention (I2R) — Scrutiny Brief

**Date chain** (high severity): `installed_at ≤ first_open_at ≤ account.created_at ≤ tutorial_completed_at ≤ first_meaningful_action_at ≤ first_purchase_at`. Any inversion is a hard bug — installs cannot open before they're installed, accounts cannot be created before first open.

**Cohort retention monotonicity** (high severity): for any `(cohort_date, source, platform)` group, `users_returned_d1 ≥ users_returned_d7 ≥ users_returned_d30`. A user retained at day 30 must also have been retained at day 7 and day 1. Inversions across day_offset values are impossible in real data. `cohort_date` is the first day of the install month.

**First-open rate by source**: ~70–90% of organic installs (`ORGANIC_SEARCH`, `REFERRAL`, `WEB_TO_APP`) should have a `first_open_at`; ~60–80% of paid installs (`PAID_SEARCH`, `PAID_SOCIAL`, `INFLUENCER`, `CROSS_PROMO`). A dataset where paid and organic open at the same rate misses a real acquisition-quality signal.

**Retention curve shape**: Day-1 retention 25–40%, Day-7 10–20%, Day-30 3–8% for typical consumer apps. Retention curves that are flat (e.g. d1=d7=d30) or that climb across day offsets indicate a generator bug.

**Tutorial-completion churn gate**: users who complete the tutorial should retain at 3–5× the rate of non-completers at every day offset. If completers and non-completers have similar d7/d30 retention rates, the activation gate is not being modeled.

**Platform split**: iOS 25–45%, Android 55–75% by install volume. A dataset that's >70% iOS or >85% Android is unusual unless the brief specifies a target market.

**Conversion to paying**: 1–5% of first-opens should reach an `In-App Purchase`. 0% paying users is too clean; >15% paying is unrealistic for a typical consumer app. Paying users should also be retained at d7+ — a payer with no retention signal is a flag.

**Campaign attribution**: `campaign_id` must be populated for paid sources (`PAID_SEARCH`, `PAID_SOCIAL`, `INFLUENCER`, `CROSS_PROMO`) and NULL for organic (`ORGANIC_SEARCH`, `REFERRAL`, `WEB_TO_APP`). Paid installs without a campaign or organic installs with a campaign indicate a generator wiring error.

**Store-platform alignment**: `store = 'app_store'` should only appear with `platform = 'iOS'`; `store = 'google_play'` only with `platform = 'Android'`. Mismatches are physically impossible.

**IAP amount distribution**: in-app purchase amounts should cluster on common price points ($0.99, $2.99, $4.99, $9.99, $19.99, $49.99, $99.99) — uniform amounts across the range indicate the generator is not modeling app store pricing tiers.

**Activation event coverage**: every install with a `TUTORIAL_COMPLETED` event should also have a preceding `ACCOUNT_CREATED` or `PROFILE_SETUP` event. Tutorial completions without account creation are an ordering bug.

**Cohort size sanity**: `users_returned ≤ cohort_size` for every retention snapshot row. `users_returned > cohort_size` is impossible.
