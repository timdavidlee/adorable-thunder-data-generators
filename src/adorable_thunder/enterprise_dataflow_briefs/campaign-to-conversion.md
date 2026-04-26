# Campaign-to-Conversion (C2C)

**Flow:** Campaign Launch → Impression → Engagement (click/open) → Lead Capture → Conversion → Attribution

C2C captures marketing funnel events from campaign execution through conversion, supporting attribution analysis and ROI reporting.

## Records

| Record | Key Fields |
|---|---|
| **Campaign** | campaign_id, name, channel, start_date, end_date, budget, target_audience, status |
| **Impression** | impression_id, campaign_id, contact_id, timestamp, channel, placement |
| **Engagement Event** | event_id, campaign_id, contact_id, event_type, timestamp, device, referrer |
| **Lead Capture** | lead_id, campaign_id, contact_id, form_type, captured_date, source_medium |
| **Conversion** | conversion_id, lead_id, campaign_id, conversion_date, conversion_type, revenue_attributed |

## Channels & Benchmark Rates

| Channel | CTR / Open Rate | Conversion Rate | Typical CPL |
|---|---|---|---|
| Email | Open 20–35%, CTR 2–5% | 1–3% | $5–$20 |
| Paid Search (SEM) | CTR 2–8% | 3–8% | $30–$200 |
| Paid Social | CTR 0.5–2% | 1–4% | $20–$100 |
| Organic Search (SEO) | CTR 2–5% | 2–6% | $5–$30 |
| Display | CTR 0.1–0.3% | 0.5–1% | $10–$50 |
| Events / Webinar | Attendance 30–50% of registrants | 5–15% | $50–$300 |

## Attribution Models

`FIRST_TOUCH` (100% to first interaction), `LAST_TOUCH` (100% to last), `LINEAR` (equal split), `TIME_DECAY` (more weight to recent), `POSITION_BASED` (40/40/20 to first/last/middle)

## Business Rules

- **Funnel ordering**: impression_date ≤ engagement_date ≤ lead_captured_date ≤ conversion_date
- **Budget pacing**: daily_spend ≤ campaign_budget / campaign_duration_days
- **Multi-touch**: one conversion can have attributed revenue split across multiple campaign_ids
- **Attribution sum**: sum(attributed_revenue per campaign) may exceed total revenue in multi-touch models — this is expected, not a data error

## Realism Benchmarks

- **Impression-to-click**: 100:2 to 100:5 (2–5% CTR)
- **Click-to-lead**: 10–20% form completion rate on landing pages
- **Lead-to-customer**: 2–10% depending on lead quality and nurture program
- **Email volume**: campaigns typically reach 1,000–100,000 contacts; engagement events are a subset

## Field Generators

`identifiers`, `dates`, `amounts`, `person`, `country`, `percentage` (rates)
