# Acquire-to-Retire (A2R) — Scrutiny Brief

**Capitalization threshold**: no asset with `cost < $2,500` should be capitalized. Items below this threshold are expensed, not tracked as fixed assets.

**Depreciation math** (high severity): for each `depreciation_run`, `book_value_end = book_value_start − depreciation_amount`. Also verify `depreciation_amount ≈ cost / useful_life_years / 12` for straight-line assets. Math errors here are generator bugs.

**Book value floor**: `book_value_end ≥ salvage_value` (typically $0 or 10% of cost). Negative book values are impossible.

**Gain/loss on disposal** (high severity): `gain_loss = proceeds − book_value_at_disposal`. Verify arithmetic; wrong signs (e.g. positive gain when proceeds < book value) are bugs.

**Fully depreciated but active**: 10–20% of the asset portfolio should have `book_value = 0` but `status = in_service`. A dataset where all fully-depreciated assets are also disposed is unrealistic.

**Asset class vs. useful life**: IT equipment should be 3–5 years; buildings 30–40. Mismatches (e.g. laptops with 20-year lives) indicate a generator wiring error.

**Depreciation continuity**: for each asset, `book_value_start` of period N must equal `book_value_end` of period N−1. Gaps or resets in the depreciation schedule indicate a generator sequencing bug.

**Accumulated depreciation check**: `accumulated_depreciation` for a given period should equal the sum of all `depreciation_amount` values from acquisition through that period. Mismatches indicate the field is being independently generated rather than derived.

**Asset cost vs. class range**: costs should be plausible for the asset class — laptops $800–$3k, servers $10k–$100k, buildings $1M+. A laptop at $500k or a building at $50k is a generator wiring error.

**Disposal after acquisition**: `disposal_date > acquisition_date`. Assets disposed before they were acquired are impossible.

**Status progression**: assets should not jump from `planned` directly to `disposed` without passing through `in_service`. Status sequences that skip intermediate states indicate a generator logic gap.
