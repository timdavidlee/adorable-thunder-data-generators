# Onboard-to-Offboard (O2O) — Scrutiny Brief

**Date chain** (high severity): `branches.opened_on ≤ clients.onboarded_on ≤ accounts.opened_on ≤ plan_changes.changed_on ≤ accounts.closed_on`. Any inversion is a hard bug.

**Closure fields** (high severity): `status = 'closed'` exactly when `closed_on` and `close_reason` are both populated. An open account with a close date, or a closed one without a reason, is a bug.

**Activity window** (high severity): no `monthly_activity` row for a month before `opened_on`'s month or after `closed_on`'s month. Activity after closure is impossible.

**Plan chain** (high severity): per account, ordered `plan_changes` chain (`to_plan` of one = `from_plan` of the next), and `accounts.plan_code` equals the last `to_plan`. No change to `SMART` before 2025-12-01.

**Primary account**: every client has exactly one KZT account opened within 3 days of `onboarded_on`. Clients with no accounts are a wiring bug.

**Fee increase signal**: `tariff_plans` has two BUSINESS rows split at 2025-03-01 (4,900 → 8,900). BUSINESS monthly closures from 2025-04 to 2025-07 should run at 2–3× their 2024 rate, highest in Karaganda; if the rate is flat, the business event isn't modeled.

**Dormancy**: 5–10% of open accounts should have `txn_count = 0` for their last 3+ months while still open. Zero dormant accounts makes "who left?" too easy; more than 20% is unrealistic.

**Partial exits**: among clients with 2+ accounts, some should have closed one and kept another. If every multi-account client closes all accounts together, the "closed accounts ≠ lost clients" lesson disappears.

**Attrition rate**: outside the fee-increase window, 0.8–1.2% of open accounts close per month. Above 3% or below 0.3% is unrealistic.

**Currency mix**: KZT ~85% of accounts, USD ~10%, EUR ~5%. Foreign-currency loans ~12%, with lower rates (7–10%) than KZT loans (16–22%).

**Balances by segment**: median `avg_balance_kzt` rises micro < small < medium by roughly an order of magnitude per step. Flat balances across segments mean the segment isn't wired in.

**Loan status**: `closed_on` populated only for `repaid` and `defaulted`; `active` loans must have `maturity_on` after the dataset end or the client still open.
