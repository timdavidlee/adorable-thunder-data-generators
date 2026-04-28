# Discover-to-Subscribe (D2S)

**Flow:** Free Content Discovery → Trailer View → Free Trial Signup → First Episode Watched → Binge Behavior → Trial Conversion

D2S covers the streaming-platform acquisition funnel from anonymous discovery through paid subscription. It is the consumer-media analog of `signup-to-renewal` (SaaS PLG funnel), with content-driven activation in place of feature-driven activation.

## Records

| Record | Key Fields |
|---|---|
| **Discovery Event** | event_id, anonymous_id, content_id, surface, timestamp, session_id |
| **Trailer Play** | play_id, anonymous_id, content_id, started_at, completion_pct, device |
| **Trial Signup** | trial_id, account_id, signup_date, trial_length_days, source_content_id, payment_method_on_file |
| **Watch Session** | session_id, account_id, content_id, episode_number, started_at, ended_at, completion_pct, device |
| **Conversion** | conversion_id, trial_id, conversion_date, plan, mrr, churned_during_trial |
| **Cancellation / Churn** | churn_id, account_id, churn_date, reason_code, last_active_date |

## Discovery Surfaces

`HOME_RAIL`, `SEARCH`, `RECOMMEND`, `CATEGORY_BROWSE`, `SOCIAL_DEEP_LINK`, `PARTNER_REFERRAL`

## Plan Tiers

| Tier | Typical Price/Month | Notes |
|---|---|---|
| Ad-supported | $5–$10 | Largest share of new signups post-2023 |
| Standard | $10–$18 | Ad-free, 1080p |
| Premium | $18–$25 | 4K, multi-stream, downloads |

## Business Rules

- **Date chain**: discovery_event ≤ trailer_play ≤ trial_signup ≤ first_watch ≤ conversion_date or trial_end
- **Trial outcome**: every trial resolves to `converted` or `churned` by trial_end_date — no open-ended trials
- **Binge classification**: ≥3 episodes of the same series within a 24h window flags `binge` behavior on that account/series pair
- **Status transitions**: anonymous → trial → paid → churned / lapsed → win-back

## Realism Benchmarks

- **Trial-to-paid conversion**: 40–60% for premium services; 25–40% for ad-supported tiers
- **First-episode-watched within 24h of trial signup**: 60–80%; trials with no first watch convert <10%
- **Binge rate**: 20–35% of new series watchers binge ≥3 episodes in their first session
- **Avg trial length**: 7–30 days; longer trials see lower conversion (decision fatigue, payment-method changes)
- **Plan mix at signup**: ad-supported 30–50%, standard 35–55%, premium 10–20% (post-2023 shift)
- **Monthly churn after conversion**: 2–6%; first-month churn is 2–3× steady-state

## Field Generators

`identifiers`, `dates`, `amounts`, `person`, `country`, `percentage` (conversion, binge, churn rates), `payment_terms`
