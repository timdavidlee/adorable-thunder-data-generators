# Record-to-Report (R2R) — Scrutiny Brief

**Double-entry** (high severity, no tolerance): for every journal entry header, `sum(debit_amounts) = sum(credit_amounts)`. Any entry that doesn't balance is a hard error that would never appear in a real GL.

**Accrual reversals**: every entry with `entry_type = ACCRUAL` must have a matching reversal entry dated the first day of the following period. Accruals without reversals, or reversals that don't match the original amount, are bugs.

**Period lock**: no entries posted to a `posting_date` that falls in a period marked closed, unless an override is present. Entries backdated months into the past without explanation are suspicious.

**Close timing**: ~30% of period-end entries should fall in the last 3 business days of the month. A flat daily distribution is unrealistic.

**Entry volume**: expect 500–5,000 journal entries per monthly close for a mid-large enterprise. Far fewer suggests undergeneration; far more suggests the generator is not scoping to entity/period correctly.

**Late entries**: ~5% of entries should be dated in the period after the one they're recording (late postings). Zero late entries is too clean.

**Intercompany eliminations**: `ELIMINATION` entries must net to zero across both sides — every debit elimination in entity A must have a matching credit elimination in entity B for the same intercompany pair and amount. Unmatched eliminations leave the consolidated trial balance out of balance.

**Account normal balance**: revenue and liability accounts should net to credit; expense and asset accounts to debit. An expense account with a net credit balance, or a revenue account with a net debit, is suspicious unless it's a reversal entry.

**Fiscal period alignment**: the `fiscal_period` on each entry should correspond to the `entry_date`. An entry dated in March assigned to a Q1 period that ended in January is a mismatch and indicates a generator wiring error.

**Recurring entry consistency**: entries with `entry_type = RECURRING` should appear every period with the same amount (or a known indexed amount). A recurring entry that appears in some periods but not others, or with wildly varying amounts, is a bug.
