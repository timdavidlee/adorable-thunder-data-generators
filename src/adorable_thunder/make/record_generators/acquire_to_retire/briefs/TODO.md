# Insights Wishlist TODO — acquire_to_retire

Living TODO of field/data additions proposed by `/insights-wishlist`. Full runs are archived under `docs/generated/iter/acquire-to-retire/`. Prune entries here as they are implemented or become irrelevant.

## 2026-04-28 run

### Top 5
1. **assets.purchase_order_id + assets.vendor_name** (high) — cross-table hook to P2P; traces capex spend to the fixed-asset register.
2. **assets.gl_account + depreciation_runs.posting_date + depreciation_runs.journal_entry_id** (high) — cross-table hook to R2R; closes the loop between asset register and financial statements.
3. **assets.in_service_date** (high) — distinct from `acquisition_date`; unlocks "time to productive use" capex efficiency metrics.
4. **assets.assigned_to_email** (high) — custodian; foundation for IT asset management, offboarding, ownership audits.
5. **disposals.disposal_reason_code** (high) — the *why* of retirement (vs. `disposal_type` which captures *how*); enables replacement-rate forecasting.

### All proposals

**assets**
- **assets.purchase_order_id** (cross-table, high) — link to P2P PO that acquired the asset.
- **assets.gl_account** (cross-table, high) — GL account for depreciation expense; rollup to R2R/B2R.
- **assets.in_service_date** (behavioral, high) — capitalization begins here, not at acquisition.
- **assets.assigned_to_email** (behavioral, high) — custodian / user of the asset.
- **assets.vendor_name** (cross-table, medium) — supplier capex concentration analytics.
- **assets.serial_number** (analytics, medium) — warranty, recall, physical inventory matching.
- **assets.lease_or_owned** (analytics, medium) — IFRS 16 / ASC 842 distinction.
- **assets.business_unit** (analytics, medium) — exec-level rollup above `cost_center`.
- **assets.tax_class** (analytics, medium) — tax depreciation classification.
- **assets.asset_tag** (analytics, low) — physical inventory tag.
- **assets.warranty_end_date** (analytics, low) — service-contract analytics.
- **assets.manufacturer** (analytics, low) — concentration / recall.

**depreciation_runs**
- **depreciation_runs.posting_date** (cross-table, high) — actual GL post date.
- **depreciation_runs.journal_entry_id** (cross-table, high) — link to R2R journal entry.
- **depreciation_runs.period_end_date** (visualization, medium) — date column derived from `period` text.
- **depreciation_runs.tax_depreciation_amount** (analytics, medium) — book-vs-tax / deferred-tax analytics.
- **depreciation_runs.is_period_close** (behavioral, low) — close-cycle indicator.

**disposals**
- **disposals.disposal_reason_code** (behavioral, high) — END_OF_LIFE / REPLACEMENT / TECH_REFRESH / SURPLUS / DAMAGED / REGULATORY.
- **disposals.replacement_asset_id** (cross-table, medium) — asset-lifecycle chains, refresh cycles.
- **disposals.disposal_journal_entry_id** (cross-table, medium) — GL entry for gain/loss.
- **disposals.disposal_method** (analytics, medium) — AUCTION / BROKER / INTERNAL / SCRAP_VENDOR; recovery-rate channel analysis.
- **disposals.buyer_name** (cross-table, low) — buyer of sold/trade-in assets.
- **disposals.approver_email** (behavioral, low) — controls / SoD for large disposals.

### Out of scope (would need new tables)
- **Asset transfer / movement log** — no event log of cost-center / location moves over an asset's life.
- **Maintenance / repair events** — capitalized repairs (>$2,500) have their own lifecycle.
- **Lease schedule** — leased assets (if `lease_or_owned` were added) need a schedule with rent payments and lease terms.
