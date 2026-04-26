# record_generators

Full-record generators. Each subdirectory corresponds to one data flow and assembles complete DataFrames by combining atomic field generators from `../field_generators/`.

## Conventions

- Each flow gets its own subdirectory (e.g. `procure_to_pay/`, `order_to_cash/`)
- Within a flow directory:
  - One file per stage of the flow (e.g. `requests.py`, `purchase_orders.py`, `invoices.py`, `payments.py`)
  - A `flow.py` that imports all stage generators and wires them together into the full end-to-end dataset
  - An `__init__.py` that exports the top-level entry point from `flow.py`
- The top-level entry point in each `flow.py` is a Pydantic `GeneratorConfig` model with a `.make() -> dict[str, pd.DataFrame]` method (one DataFrame per stage, keyed by stage name)
  - this should also have a method `.make_in_dir() -> None` that creates a directory `/procure_to_pay/` with the various dataframes saved as `.parquet` format
- Field-level logic stays in `../field_generators/` — record generators only assemble and relate columns
- Cross-field constraints (e.g. completed_date must be after request_date, FK references between stages) belong here, not in field generators
- for each *.py (e.g. `requests.py`, `purchase_orders.py`, `invoices.py`, `payments.py`)
  - there should be a `generate_...` function which returns a pandas dataframe
  - there should also be a `create_pg_sql_table_schema(pg_schema: str) -> CreatePgTableSql` — returns a `CreatePgTableSql` instance (not a raw SQL string); call `.sql_statement` on it to get the DDL
  - schema for the postgresql should be `procure_to_pay.requests` etc
- each flow's `__init__.py` exports a `_FLOW_SCHEMA` dict mapping stage name → `CreatePgTableSql` (pre-filled with the flow's pg_schema), alongside `GeneratorConfig`


## Flow briefs

Business rules, realism benchmarks, and schema definitions for each flow:

@../../enterprise_dataflow_briefs/CLAUDE.md
