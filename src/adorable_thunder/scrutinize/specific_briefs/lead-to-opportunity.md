# Lead-to-Opportunity (L2O) — Scrutiny Brief

**Probability monotonicity** (high severity): `probability` must increase through pipeline stages — Prospecting (5%) → Qualification (15%) → Discovery (25%) → Proposal (40%) → Negotiation (60%) → Closed Won (100%) / Closed Lost (0%). Opportunities with probability that doesn't match their stage are a bug.

**Date chain** (high severity): `lead_created_date ≤ opp_created_date ≤ quote_date ≤ contract_start_date`. Close dates must be in the past for Closed Won/Lost.

**Deal value consistency**: `quote_total ≈ contract_total` (within discount range). Large unexplained gaps between quote and contract amounts are a flag.

**Win rate**: ~20–30% of closed opportunities should be `Closed Won`; 70–80% `Closed Lost`. A win rate of >60% is unrealistic for enterprise B2B.

**Stage distribution**: most open opportunities should cluster in Qualification and Proposal. Very few should be in Negotiation. If the pipeline is uniformly distributed across stages, it's unrealistic.

**Coverage ratio**: total open pipeline value should be 3–4× the quarterly quota (if quota is modeled). A pipeline where the stage distribution implies unrealistically high conversion would produce quota coverage well above this range.

**Lead source distribution**: leads should span multiple `source` values (`WEB_FORM`, `REFERRAL`, `TRADE_SHOW`, etc.). If >60% of leads share a single source, the generator is not varying the acquisition channel realistically.

**Owner concentration**: opportunities should be distributed across multiple `owner_email` values. If one rep owns >40% of total pipeline, the generator is likely defaulting to a small list of owners without randomizing.

**Stale open opportunities**: open opportunities (not Closed Won/Lost) with a `close_date` in the past are a data quality flag. A generator should either advance the stage or mark them lost — real CRM data has stale deals, but they should be a minority (<10%), not the default.
