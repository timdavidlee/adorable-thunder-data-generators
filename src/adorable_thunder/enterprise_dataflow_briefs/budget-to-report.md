# Budget-to-Report (B2R)

**Flow:** Budget Creation → Approval → Actuals Capture → Forecast Update → Variance Analysis → Management Reporting

B2R governs the financial planning and analysis cycle. Data spans multiple scenarios across cost centers, GL accounts, and fiscal periods.

## Records

| Record | Key Fields |
|---|---|
| **Budget Line** | budget_id, fiscal_period, cost_center, account_code, scenario, amount, version, status |
| **Forecast Line** | forecast_id, fiscal_period, cost_center, account_code, scenario, amount, version, updated_date |
| **Actual Line** | sourced from R2R GL; fiscal_period, cost_center, account_code, actual_amount |
| **Variance Report Line** | period, cost_center, account_code, budget_amount, forecast_amount, actual_amount, bud_variance, fcast_variance |

## Scenarios

| Scenario | Description |
|---|---|
| `ORIGINAL_BUDGET` | Approved plan at start of fiscal year; locked after approval |
| `REVISED_BUDGET` | Mid-year reforecast approved by finance leadership |
| `FORECAST` | Rolling monthly estimate; replaced (not accumulated) each revision |
| `ACTUALS` | Posted GL amounts from R2R |

## Business Rules

- **Budget lock**: ORIGINAL_BUDGET is immutable after board approval
- **Variance sign convention**: for expense accounts, positive variance = overspend (actual > budget)
- **Completeness**: every active cost_center × account_code pair should have a budget entry per period
- **Forecast replacement**: new FORECAST entries overwrite the previous version for the same period/cost_center/account
- **Revenue vs. expense**: variance direction is favorable/unfavorable depending on account type

## Realism Benchmarks

- **Budget variance**: typical actuals within ±10% of budget; >20% requires explanation; >30% is an outlier
- **Seasonal patterns**: opex higher in Q1 (hiring) and Q4 (year-end spend); revenue lower in Q1
- **Forecast versions**: 2–4 per fiscal year is standard
- **Coverage**: all 40 cost centers should have entries; missing cost centers flag a data gap

## Field Generators

`amounts`, `fiscal_period`, `cost_center`, `ledger_account`, `percentage` (variance rates), `identifiers`
