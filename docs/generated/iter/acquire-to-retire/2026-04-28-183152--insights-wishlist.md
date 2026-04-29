# Insights Wishlist — acquire-to-retire

## What ran

`/insights-wishlist acquire-to-retire` against the freshly-seeded `acquire_to_retire` schema (1000 assets, 5879 depreciation runs, 95 disposals).

## What changed

Read-only skill, no code changes. Wishlist follows.

### assets

- **assets.purchase_order_id** (cross-table, **high**) — link to P2P; capex spend → fixed-asset register.
- **assets.gl_account** (cross-table, **high**) — depreciation expense GL account; foundation for R2R/B2R rollup.
- **assets.in_service_date** (behavioral, **high**) — distinct from `acquisition_date`; capitalization begins when ready for use.
- **assets.assigned_to_email** (behavioral, **high**) — custodian; IT asset management, offboarding recovery.
- **assets.vendor_name** (cross-table, medium) — companion to `purchase_order_id`; vendor capex analytics.
- **assets.serial_number** (analytics, medium) — manufacturer ID; warranty, recall, physical inventory.
- **assets.lease_or_owned** (analytics, medium) — IFRS 16 / ASC 842 distinction.
- **assets.business_unit** (analytics, medium) — exec-level rollup above `cost_center`.
- **assets.tax_class** (analytics, medium) — tax depreciation differs from book; needed for tax-vs-book.
- **assets.asset_tag** (analytics, low) — physical inventory tag.
- **assets.warranty_end_date** (analytics, low) — service-contract analytics.
- **assets.manufacturer** (analytics, low) — concentration / recall analytics.

### depreciation_runs

- **depreciation_runs.posting_date** (cross-table, **high**) — actual GL post date (currently only a text `period`).
- **depreciation_runs.journal_entry_id** (cross-table, **high**) — link to R2R journal entry that booked the depreciation.
- **depreciation_runs.period_end_date** (visualization, medium) — date column derived from `period` for time-series.
- **depreciation_runs.tax_depreciation_amount** (analytics, medium) — book-vs-tax depreciation analytics, deferred-tax computation.
- **depreciation_runs.is_period_close** (behavioral, low) — close-cycle vs. mid-month timing.

### disposals

- **disposals.disposal_reason_code** (behavioral, **high**) — *why* (END_OF_LIFE, REPLACEMENT, TECH_REFRESH, SURPLUS, DAMAGED, REGULATORY) vs. *how* (`disposal_type`).
- **disposals.replacement_asset_id** (cross-table, medium) — asset-lifecycle chains, refresh-cycle analytics.
- **disposals.disposal_journal_entry_id** (cross-table, medium) — GL entry for the gain/loss.
- **disposals.disposal_method** (analytics, medium) — AUCTION / BROKER / INTERNAL / SCRAP_VENDOR; recovery-rate analysis.
- **disposals.buyer_name** (cross-table, low) — buyer of sold/trade-in assets.
- **disposals.approver_email** (behavioral, low) — controls / segregation-of-duties for large disposals.

### Top 5 wishlist (highest leverage)

1. **assets.purchase_order_id + assets.vendor_name** — cross-table hook to P2P; traces capex spend → fixed-asset register.
2. **assets.gl_account + depreciation_runs.posting_date + depreciation_runs.journal_entry_id** — cross-table hook to R2R; closes the loop between asset register and financial statements.
3. **assets.in_service_date** — distinct from `acquisition_date`; unlocks "time to productive use" capex efficiency metrics.
4. **assets.assigned_to_email** — the custodian; foundation for IT asset management, offboarding, ownership audits.
5. **disposals.disposal_reason_code** — captures the *why* of retirement; enables replacement-rate forecasting.

### Out of scope (would need new tables)

- **Asset transfer / movement log** — assets move between cost centers and locations during their life; today there's no event log.
- **Maintenance / repair events** — capitalized repairs (>$2,500) have their own lifecycle.
- **Lease schedule** — leased assets need their own table with rent payments and lease terms (IFRS 16 / ASC 842).

## Verification

Read-only skill, no code changes. The wishlist was derived from `information_schema.columns`, distribution queries on `depreciation_method` and `location_country`, and 5-row samples per table on the live `acquire_to_retire` schema.

## Follow-ups

None. Wishlist appended to `src/adorable_thunder/make/record_generators/acquire_to_retire/briefs/TODO.md` as the working list.
