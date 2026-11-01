# Onboard-to-Offboard (O2O)

**Flow:** Client Onboarding → Account Opening → Tariff Plan Changes → Monthly Account Activity → (Dormancy) → Account Closure

O2O covers a retail bank's small-business client book: clients are onboarded at a branch, open one or more current accounts on a tariff plan, move between plans, transact monthly, and eventually go dormant or close. Amounts are in Kazakhstani tenge (KZT). The analytical lens is **attrition**: who left, when, from which plan and region, and why. "Left" has several defensible definitions (every account closed, dormant, or downgraded), and the data supports all of them.

## Records

| Record | Key Fields |
|---|---|
| **Branch** | branch_id, branch_name, region, city, opened_on |
| **Tariff Plan** (price history) | plan_code, plan_name, monthly_fee_kzt, effective_from, effective_to |
| **Client** | client_id, legal_name, legal_form, bin, industry, segment, region, branch_id, onboarded_on |
| **Account** | account_id, client_id, iban, currency, plan_code, opened_on, closed_on, close_reason, status |
| **Plan Change** | plan_change_id, account_id, changed_on, from_plan, to_plan |
| **Monthly Activity** | account_id, month, avg_balance_kzt, txn_count, txn_volume_kzt |
| **Loan** | loan_id, client_id, currency, principal, rate_pct, term_months, issued_on, maturity_on, closed_on, status |

## Tariff Plans

`START` (micro, cheapest), `BUSINESS` (core plan), `PRO` (higher volume), `TRADE` (FX and import/export), `AGRO` (seasonal agriculture). `SMART` launches 2025-12-01 as a mid-tier alternative to `BUSINESS`. A plan's fee can change over time; each price period is one row.

## Business Events

- **BUSINESS fee increase**: 4,900 → 8,900 KZT/month effective 2025-03-01. Over the following months BUSINESS accounts close at an elevated rate (citing fees or a switch to another bank), concentrated in the Karaganda region, and a share downgrade to `START` instead of leaving.
- **SMART launch** (2025-12-01): some START and BUSINESS accounts move to SMART in its first month.

## Business Rules

- **Date chain**: branch.opened_on ≤ client.onboarded_on ≤ account.opened_on ≤ plan_change.changed_on ≤ account.closed_on ≤ dataset end
- **Primary account**: every client has a KZT account opened within 3 days of onboarding; ~25% also hold a second account (often USD or EUR)
- **Partial exits**: a client can close one account and keep another. A client has left the bank only when every account is closed
- **Dormancy**: some accounts stop transacting (txn_count = 0 for ≥ 3 consecutive months) without being closed. Dormant ≠ closed
- **Activity window**: monthly_activity rows exist only for months in which the account was open; none after closed_on's month
- **Wind-down**: accounts that close show falling txn_count over their last 2 months
- **Closure**: closed accounts have status = 'closed', a closed_on date, and a close_reason; open accounts have neither
- **Plan consistency**: account.plan_code equals the to_plan of the account's latest plan change, or its opening plan if none; consecutive plan changes chain (to_plan of one = from_plan of the next)
- **Fee lookup**: an account's fee for a month is the tariff_plans row for its plan whose effective window covers that month
- **Loans**: issued_on ≥ onboarded_on; maturity_on = issued_on + term_months; closed_on is set for repaid and defaulted loans

## Realism Benchmarks

- **Clients**: IE (individual entrepreneur) ~70%, LLP ~30%; segment micro ~65%, small ~30%, medium ~5%
- **Regions**: Almaty and Astana hold ~50% of clients; the rest spread over Shymkent, Karaganda, Aktobe, Atyrau
- **Plan mix at opening**: START ~40%, BUSINESS ~35%, PRO ~12%, TRADE ~8%, AGRO ~5%
- **Currency**: KZT ~85% of accounts, USD ~10%, EUR ~5%; foreign-currency loans ~12%
- **Attrition**: ~0.8–1.2% of accounts close per month in normal months; annual client attrition 10–15%
- **Dormancy**: 5–10% of open accounts dormant at any time
- **Balances**: average monthly balance lognormal; micro ~300k KZT, small ~2.5M KZT, medium ~20M KZT (median)
- **Loans**: ~25% of clients; KZT rate 16–22%, USD rate 7–10%; default ~4%

## Field Generators

`kz_business` (legal names, BINs, IBANs), `identifiers`, `dates`
