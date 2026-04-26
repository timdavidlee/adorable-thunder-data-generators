# Budget-to-Report (B2R) — Scrutiny Brief

**Coverage** (high severity): every active `cost_center × account_code` pair should have a budget entry for every fiscal period. Sparse coverage — large gaps of missing combinations — is a structural bug.

**Variance bounds**: expect actuals within ±10% of budget for most lines; >20% should require an explanation flag; >30% is an outlier. A dataset where every line is within ±1% is too perfect; one where all lines are >50% off is broken.

**ORIGINAL_BUDGET immutability**: `ORIGINAL_BUDGET` entries should not change across versions. If the same period/cost_center/account has multiple `ORIGINAL_BUDGET` rows with different amounts, that's a bug.

**Forecast replacement**: for a given `period × cost_center × account`, `FORECAST` entries should replace (not accumulate) — one row per revision. Multiple FORECAST rows for the same key without incrementing version numbers are a bug.

**Seasonal patterns**: opex should be higher in Q1 (headcount ramp) and Q4 (year-end spend); revenue should be lower in Q1. Flat seasonal patterns across all accounts are suspicious.

**Variance sign convention** (high severity): for expense accounts, positive `bud_variance` = overspend (actual > budget); for revenue accounts, positive = favorable (actual > budget). A dataset where the sign convention is reversed or inconsistent across account types indicates a generator logic error.

**Period totals consistency**: the sum of period-level budget amounts for a given `cost_center × account_code` should equal the known annual budget for that combination. If period amounts sum to a wildly different figure than the annual total, the generator is not distributing budgets correctly.

**Zero-budget active accounts**: active cost centers should not have $0 budget for major GL accounts (headcount, rent, COGS). A cost center with employees but no salary budget, or a sales team with no revenue budget, is a structural gap.
