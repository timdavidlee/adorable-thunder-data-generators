# generators

Atomic field-level generators. Each function produces values for a **single column** across `n` records. Full record assembly (combining fields into a DataFrame) happens in `purchase_order_flow/`, not here.

## Interface convention

All generator functions follow this signature pattern:

```python
def generate_<thing>(n_samples: int, ...) -> np.ndarray | pd.Series:
```

- First argument is always `n_samples: int`
- Return `np.ndarray` for scalar columns (amounts, codes, emails, identifiers)
- Return `pd.Series` for date columns
- Return `pd.DataFrame` only when the output is inherently multi-column (e.g. `generate_local_currency_amounts` → `currency_code`, `rate`, `amount_usd`, `amount_local`)

## Files

| File | What it generates |
|---|---|
| `address.py` | Street address, city, state/province, country, postal code; filterable by country |
| `amounts.py` | USD amounts (lognormal distribution); local currency amounts via FX conversion |
| `carrier.py` | Carrier SCAC codes, names, transport modes; filterable by mode |
| `company.py` | Supplier/vendor names; company+product pairs |
| `cost_center.py` | Cost center strings sampled from reference pool |
| `country.py` | ISO2 country codes and names; GDP-weighted sampling |
| `currency.py` | Currency codes weighted by market cap; FX rate lookup; USD conversion |
| `dates.py` | Random dates in a range; dates extrapolated off an existing date series |
| `fiscal_period.py` | Fiscal period strings (`FY2025-Q2`, `FY2025-P03`) by quarter or month |
| `identifiers.py` | UUIDs; serial numbers with a prefix (e.g. `REQ-000123`) |
| `incoterms.py` | Incoterms 2020 codes; frequency-weighted; filterable by transport mode |
| `ledger_account.py` | GL account codes and names; filterable by account type |
| `payment_terms.py` | Payment term labels (Net 30, 2/10 Net 30, etc.); frequency-weighted |
| `percentage.py` | Tax rates, discount rates, gross margin rates, budget variance rates |
| `person.py` | First names, last names, full names; globally diverse pool |
| `phone.py` | E.164-format phone numbers; single-country or matched to a country code array |
| `product_code.py` | SKU/item codes with category prefix (PROD, MAT, SKU, SVC, etc.) |
| `splits.py` | Split/allocation values that sum to a total |
| `unit_of_measure.py` | UOM codes; filterable by category (count, weight, time, service, digital) |
| `users.py` | User emails sampled from the reference pool |
| `_random_state.py` | Shared random seed utilities |

## What belongs here

A function belongs in this directory if it generates values for **one field in isolation** — it does not know about other columns or the record it will become part of.

If a function needs two or more already-generated columns to produce its output (e.g. "pick a completion date that is after the request date"), it belongs in `purchase_order_flow/` where that context exists.

## Adding a new generator

1. Create a file named after the field type (`country.py`, `phone.py`, etc.)
2. Sample from `make/reference_data/` if the values should be drawn from a fixed pool; use a distribution (`np.random.*`) if they should be statistically varied
3. Export from the file directly — no need to register anywhere; callers import directly
