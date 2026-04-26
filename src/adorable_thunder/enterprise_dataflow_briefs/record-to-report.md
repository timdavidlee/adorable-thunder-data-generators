# Record-to-Report (R2R)

**Flow:** Source Transactions → Journal Entries → GL Postings → Trial Balance → Reconciliation → Financial Statements

R2R covers the accounting close cycle — capturing transactions in the general ledger and producing auditable financial reports. Entries originate from sub-ledgers (AP, AR, payroll) or are entered manually (accruals, adjustments, reclassifications).

## Records

| Record | Key Fields |
|---|---|
| **Journal Entry Header** | entry_id, entry_date, posting_date, fiscal_period, entity, entry_type, description, status |
| **Journal Entry Line** | entry_id, line_number, account_code, account_name, debit_amount, credit_amount, cost_center |
| **GL Balance** | account_code, period, entity, opening_balance, period_activity, closing_balance |
| **Reconciliation** | recon_id, account_code, period, gl_balance, sub_ledger_balance, difference, status |

## Entry Types

`RECURRING` (same amount each period), `ACCRUAL` (estimate; reversed next period), `ADJUSTMENT`, `RECLASSIFICATION`, `ELIMINATION` (intercompany), `PREPAYMENT_RELEASE`

## Business Rules

- **Double-entry**: sum(debit_amounts) = sum(credit_amounts) per journal entry header — no exceptions
- **Period lock**: entries cannot be posted to closed periods; late entries require override approval
- **Accrual reversal**: ACCRUAL entries generate a matching reversal entry dated the first day of the next period
- **Status transitions**: `draft` → `posted` → `reversed`
- **Intercompany eliminations**: must zero out matching interco transactions across legal entities

## Realism Benchmarks

- **Entry volume**: mid-large enterprise: 500–5,000 journal entries per monthly close
- **Close timing**: ~30% of entries fall in the last 3 business days of the period; ~5% are late entries posted in the next period
- **Amount range**: $100–$10M; payroll and accrual entries tend toward the high end ($50k–$5M)
- **Accrual share**: ~20–40% of period-end entries are accruals that reverse next period

## Field Generators

`ledger_account`, `amounts`, `dates`, `fiscal_period`, `cost_center`, `identifiers`, `currency`
