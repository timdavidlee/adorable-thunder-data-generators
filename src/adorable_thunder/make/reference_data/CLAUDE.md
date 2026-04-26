# reference_data

Static lookup tables used as source pools by the generators. All data is fictional and deterministic — no external dependencies, no randomness.

## Files

| File | Exported symbol(s) | Description |
|---|---|---|
| `carriers.py` | `CARRIERS` | 36 carriers as `(scac_code, carrier_name, primary_mode)` tuples; modes: road, parcel, ocean, air, rail |
| `cities.py` | `CITIES` | ~140 major commercial cities as `(city, state_province, country_code, postal_code)` tuples, covering all 47 countries in `countries.py` |
| `company_names.py` | `COMPANY_NAMES` | ~200 fictional supplier/vendor names across 6 industries (Technology, Logistics, Materials, Entertainment, Finance, Manufacturing) |
| `company_users.py` | `COMPANY_USER_EMAILS` | ~360 fictional user emails, ~5 per company in `COMPANY_NAMES` (same industry grouping) |
| `company2products.py` | _(see file)_ | Maps company names to product/service catalogs |
| `cost_centers.py` | `COST_CENTERS` | 40 cost center strings in `CC-XXXX – Department Name` format, covering corporate functions |
| `countries.py` | `COUNTRIES` | 47 countries as `(iso2_code, country_name, gdp_usd_trillions)` tuples, ordered by GDP descending |
| `incoterms.py` | `INCOTERMS` | All 11 Incoterms 2020 rules as `(code, name, applicable_transport)` tuples |
| `ledger_accounts.py` | `ASSET_ACCOUNTS`, `LIABILITY_ACCOUNTS`, `EQUITY_ACCOUNTS`, `REVENUE_ACCOUNTS`, `COGS_ACCOUNTS`, `OPEX_ACCOUNTS`, `OTHER_INCOME_EXPENSE_ACCOUNTS`, `GENERAL_LEDGER_ACCOUNTS` | Chart of accounts tuples `(account_code, account_name)`; `GENERAL_LEDGER_ACCOUNTS` is the concatenation of all the above |
| `payment_terms.py` | `PAYMENT_TERMS` | 12 standard enterprise payment terms as `(code, label, net_days)` tuples, ordered by frequency |
| `person_names.py` | `FIRST_NAMES`, `LAST_NAMES` | ~150 first names and ~150 last names drawn from diverse global cultures |
| `units_of_measure.py` | `UNITS_OF_MEASURE` | 33 UOM codes as `(code, description, category)` tuples; categories: count, weight, volume, length, area, time, service, digital |

## Conventions

- All lists are plain Python literals — no functions, no classes.
- `COMPANY_NAMES` and `COMPANY_USER_EMAILS` are implicitly linked: emails follow the pattern `firstname.lastname@<companydomain>.com` and appear in the same order as the companies.
- Ledger account codes follow standard accounting ranges: 1xxx assets, 2xxx liabilities, 3xxx equity, 4xxx revenue, 5xxx COGS, 6xxx opex, 7xxx other income/expense.
- When adding new reference data, keep entries fictional and avoid reusing real company or person names.