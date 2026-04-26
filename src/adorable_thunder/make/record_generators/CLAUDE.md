# record_generators

Full-record generators. Each subdirectory corresponds to one data flow and assembles complete DataFrames by combining atomic field generators from `../field_generators/`.

## Conventions

- Each flow gets its own subdirectory (e.g. `procure_to_pay/`, `order_to_cash/`)
- Within a flow directory:
  - One file per stage of the flow (e.g. `requests.py`, `purchase_orders.py`, `invoices.py`, `payments.py`)
  - A `flow.py` that imports all stage generators and wires them together into the full end-to-end dataset
  - An `__init__.py` that exports the top-level entry point from `flow.py`
- The top-level entry point in each `flow.py` is a Pydantic `GeneratorConfig` model with a `.make() -> dict[str, pd.DataFrame]` method (one DataFrame per stage, keyed by stage name)
- Field-level logic stays in `../field_generators/` — record generators only assemble and relate columns
- Cross-field constraints (e.g. completed_date must be after request_date, FK references between stages) belong here, not in field generators

## Flow briefs

Business rules, realism benchmarks, and schema definitions for each flow:

@../../enterprise_dataflow_briefs/CLAUDE.md
