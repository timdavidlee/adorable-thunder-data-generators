# Campaign-to-Conversion (C2C) — Scrutiny Brief

**Funnel ordering** (high severity): `impression_date ≤ engagement_date ≤ lead_captured_date ≤ conversion_date`. Conversions before impressions, or leads captured before engagement, are hard bugs.

**Channel-appropriate rates**: email open rates 20–35%, CTR 2–5%; paid search CTR 2–8%; display CTR 0.1–0.3%. A dataset where every channel has identical engagement rates indicates the generator isn't modeling channel-specific behavior.

**Budget pacing**: `daily_spend ≤ campaign_budget / campaign_duration_days`. Campaigns that overspend their daily budget every single day, or that spend zero on most days, are unrealistic.

**Multi-touch attribution**: in multi-touch attribution models, `sum(attributed_revenue across campaigns)` can exceed actual revenue — this is expected and should not be flagged as an error.

**Impression-to-conversion funnel taper**: impressions >> engagements >> leads >> conversions. A funnel where conversions outnumber leads, or leads outnumber engagements, is structurally broken.

**Campaign date bounds**: no impressions, engagement events, or lead captures should be dated before `campaign.start_date` or after `campaign.end_date`. Events outside the campaign window indicate the generator is not enforcing the campaign lifecycle.

**CPL sanity**: `budget / leads_captured` should fall within channel-appropriate CPL ranges (email $5–$20; paid search $30–$200; events $50–$300). CPLs far outside these ranges indicate a budget or volume miscalibration in the generator.

**Contact uniqueness per campaign**: the same `contact_id` should not appear as a new `lead_capture` more than once per campaign. Duplicate lead captures for the same contact inflate funnel metrics and would be deduped in any real marketing system.
