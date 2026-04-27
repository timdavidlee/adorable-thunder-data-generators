# Campaign-to-Conversion (C2C) — Scrutiny Brief

**Funnel ordering** (high severity): `impression_date ≤ engagement_date ≤ lead_captured_date ≤ conversion_date`. Any inversion is a hard bug.

**Campaign date bounds** (high severity): no impressions, engagement events, lead captures, or conversions should be dated before `campaign.start_date` or after `campaign.end_date`. Events outside the campaign window indicate the generator is not enforcing the campaign lifecycle.

**Impression-to-conversion funnel taper** (high severity): impressions >> engagements >> leads >> conversions. A funnel where conversions outnumber leads, or leads outnumber engagements, is structurally broken.

**Channel-appropriate engagement rates**: email open rates 20–35%, CTR 2–5%; paid search CTR 2–8%; display CTR 0.1–0.3%. A dataset where every channel has identical engagement rates indicates the generator isn't modelling channel-specific behaviour.

**Budget pacing**: `daily_spend ≤ campaign_budget / campaign_duration_days`. Campaigns that overspend their daily budget, or spend zero on most days, are unrealistic.

**CPL sanity**: `budget / leads_captured` should fall within channel-appropriate CPL ranges (email $5–$20; paid search $30–$200; events $50–$300). CPLs far outside these ranges indicate a budget or volume miscalibration.

**Contact uniqueness per campaign**: the same `contact_id` should not appear as a new `lead_capture` more than once per campaign. Duplicate lead captures for the same contact inflate funnel metrics.

**Multi-touch attribution sum**: in multi-touch models `sum(attributed_revenue across campaigns)` may legitimately exceed actual conversion revenue — do not flag this as an error. Flag it only if all records use the same attribution model (no variety).

**Campaign status distribution**: active campaigns should not be 100% of records — expect a mix of `active`, `completed`, `paused`, and `draft`. A dataset where all campaigns are `active` is unrealistic.

**Channel distribution**: campaigns should span multiple channels. If >50% of campaigns share a single channel, flag as a low-severity realism gap.
