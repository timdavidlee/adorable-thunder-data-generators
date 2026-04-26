# Acquire-to-Retire (A2R)

**Flow:** Asset Requisition → PO → Asset Receipt → Asset Master → Depreciation Schedule → Disposal/Retirement

A2R tracks the full lifecycle of a fixed asset from acquisition through disposal. It intersects with Procure-to-Pay at acquisition and with R2R for depreciation postings.

## Records

| Record | Key Fields |
|---|---|
| **Asset Master** | asset_id, asset_class, description, acquisition_date, cost, useful_life_years, depreciation_method, status, location, cost_center |
| **Depreciation Run** | run_id, asset_id, period, book_value_start, depreciation_amount, book_value_end, accumulated_depreciation |
| **Asset Disposal** | disposal_id, asset_id, disposal_date, disposal_type, proceeds, book_value_at_disposal, gain_loss |

## Asset Classes & Useful Lives

| Class | Useful Life | Depreciation Method |
|---|---|---|
| IT Equipment | 3–5 years | Straight-line |
| Office Furniture | 7–10 years | Straight-line |
| Vehicles | 5 years | Straight-line or Declining Balance |
| Leasehold Improvements | Lease term | Straight-line |
| Buildings | 30–40 years | Straight-line |
| Intangibles / Software | 3–5 years | Straight-line |
| Machinery & Equipment | 5–15 years | Straight-line or Sum-of-years |

## Business Rules

- **Capitalization threshold**: items below $2,500–$5,000 are expensed, not capitalized
- **Depreciation start**: begins the month following acquisition (half-year convention also common)
- **Book value floor**: book value ≥ salvage value (typically $0 or 10% of cost)
- **Gain/loss on disposal**: gain_loss = proceeds − book_value_at_disposal
- **Status transitions**: `planned` → `in_service` → `fully_depreciated` / `disposed`

## Realism Benchmarks

- **Asset costs**: laptops $800–$3k; servers $10k–$100k; vehicles $25k–$80k; machinery $50k–$2M
- **Depreciation amounts**: annual = cost / useful_life (straight-line)
- **Disposal proceeds**: IT 10–30% of cost; vehicles 30–50%; buildings vary widely
- **Portfolio size**: mid-large enterprise: 500–10,000 active assets
- **Fully depreciated but active**: 10–20% of asset portfolio is common (assets used past book life)

## Field Generators

`amounts`, `dates`, `identifiers`, `cost_center`, `ledger_account`, `country` (asset location), `fiscal_period`
