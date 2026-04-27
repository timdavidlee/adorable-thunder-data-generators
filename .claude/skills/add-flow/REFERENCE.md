# Add Flow — Reference

## Enterprise brief format

File: `src/adorable_thunder/enterprise_dataflow_briefs/<flow-name>.md`

```markdown
# Flow Name (ABBR)

**Flow:** Stage A → Stage B → Stage C → Stage D

One-sentence description of what this flow covers.

## Records

| Record | Key Fields |
|---|---|
| **Stage A** | id, date, amount, status, ... |
| **Stage B** | id, stage_a_id, date, amount, status, ... |

## Business Rules

- **Date chain**: stage_a_date ≤ stage_b_date ≤ stage_c_date
- **Amount integrity**: downstream_amount ≈ upstream_amount (±tolerance)
- **Status transitions**: ...

## Realism Benchmarks

- **Amounts**: $X–$Y (lognormal); describe typical tiers
- **Status distribution**: status_a ~X%, status_b ~Y%, ...
- **Cycle times**: stage A → B: N–M days; ...
- **Multi-currency**: ~30% non-USD

## Field Generators

`amounts`, `dates`, `identifiers`, `company`, `users`, `cost_center`, `currency`, ...
```

---

## Scrutiny brief format

File: `src/adorable_thunder/scrutinize/specific_briefs/<flow-name>.md`

```markdown
# Flow Name — Scrutiny Brief

**Date chain** (high severity): `a_date ≤ b_date ≤ c_date`. Any inversion is a hard bug.

**Amount integrity**: `b_amount ≈ a_amount` (±N% tolerance). Flag large gaps.

**Status distribution**: status_x ~N%, status_y ~M%. Flag if >X% are one status.

**Field name** (severity): specific, actionable check description.
```

Each check should be one sentence, mention exact field names, and include
expected vs. flagged values.

---

## Generator patterns

### Stage file skeleton

```python
import numpy as np
import pandas as pd

from adorable_thunder.make.field_generators.amounts import generate_amounts
from adorable_thunder.make.field_generators.dates import extrapolate_off_dates, generate_random_dates
from adorable_thunder.make.field_generators.identifiers import (
    generate_n_random_uuids,
    generate_serial_numbers_with_prefix,
)
from adorable_thunder.make.record_generators.schemas import CreatePgTableSql, PgColumn

_STATUSES = np.array(["active", "closed", "cancelled"])
_STATUS_WEIGHTS = np.array([0.60, 0.30, 0.10])

STAGE_TABLE_NAME = "my_stage"


def create_pg_sql_table_schema(pg_schema: str) -> CreatePgTableSql:
    return CreatePgTableSql(
        pg_schema=pg_schema,
        pg_table=STAGE_TABLE_NAME,
        llm_description="One sentence describing this table and its role in the flow.",
        pg_columns=[
            PgColumn(
                name="stage_id",
                data_type="UUID",
                modifiers="PRIMARY KEY",
                llm_description="Unique identifier for this record.",
                llm_example_values="'a1b2c3d4-e5f6-7890-abcd-ef1234567890'",
            ),
            # ... more columns
        ],
    )


def generate_my_stage(
    n_samples: int,
    start_date: str = "2024-01-01",
    end_date: str = "2025-12-31",
    upstream_ids: np.ndarray | None = None,
    upstream_dates: pd.Series | None = None,
) -> pd.DataFrame:
    if upstream_ids is None:
        upstream_ids = generate_n_random_uuids(n_samples)

    if upstream_dates is not None:
        stage_dates = extrapolate_off_dates(upstream_dates, min_days=1, max_days=30)
    else:
        stage_dates = generate_random_dates(start_date, end_date, n_samples)

    return pd.DataFrame({
        "stage_id": generate_n_random_uuids(n_samples),
        "upstream_id": upstream_ids,
        "stage_date": stage_dates,
        "status": np.random.choice(_STATUSES, p=_STATUS_WEIGHTS, size=n_samples),
    })
```

### Common field generator imports

```python
# Amounts
from adorable_thunder.make.field_generators.amounts import generate_amounts, generate_local_currency_amounts

# Dates
from adorable_thunder.make.field_generators.dates import generate_random_dates, extrapolate_off_dates

# Identifiers
from adorable_thunder.make.field_generators.identifiers import generate_n_random_uuids, generate_serial_numbers_with_prefix

# People / companies
from adorable_thunder.make.field_generators.users import generate_user_emails
from adorable_thunder.make.field_generators.company import generate_company_names

# Currency (~30% non-USD pattern)
from adorable_thunder.make.common.math import round_weights_and_rebalance
from adorable_thunder.make.field_generators.currency import TOP_CURRENCIES

_NON_USD = [c for c in TOP_CURRENCIES if c.code != "USD"]
_NON_USD_CODES = np.array([c.code for c in _NON_USD])
_NON_USD_CAPS = np.array([c.market_cap_trillions for c in _NON_USD])
_NON_USD_WEIGHTS = round_weights_and_rebalance(_NON_USD_CAPS / _NON_USD_CAPS.sum(), precision=4)

is_non_usd = np.random.random(n_samples) < 0.30
currency_codes = np.where(
    is_non_usd,
    np.random.choice(_NON_USD_CODES, p=_NON_USD_WEIGHTS, size=n_samples),
    "USD",
)

# Cost centers
from adorable_thunder.make.field_generators.cost_center import generate_cost_center_names

# Payment terms
from adorable_thunder.make.field_generators.payment_terms import generate_payment_terms

# Tax / discount rates
from adorable_thunder.make.field_generators.percentage import generate_tax_rates
```

### flow.py skeleton

```python
from typing import ClassVar

import pandas as pd

from adorable_thunder.make.record_generators.schemas import BaseGeneratorConfig

from .stage_a import STAGE_A_TABLE_NAME, generate_stage_a
from .stage_b import STAGE_B_TABLE_NAME, generate_stage_b

FLOW_NAME = "my_flow"  # snake_case


class GeneratorConfig(BaseGeneratorConfig):
    name: ClassVar[str] = FLOW_NAME
    start_date: str = "2024-01-01"
    end_date: str = "2025-12-31"

    def make(self) -> dict[str, pd.DataFrame]:
        stage_a = generate_stage_a(self.n_samples, self.start_date, self.end_date)

        active_a = stage_a[stage_a["status"] != "cancelled"].reset_index(drop=True)
        stage_b = generate_stage_b(
            len(active_a),
            start_date=self.start_date,
            end_date=self.end_date,
            upstream_ids=active_a["stage_a_id"].to_numpy(),
            upstream_dates=active_a["stage_a_date"],
        )

        return {
            STAGE_A_TABLE_NAME: stage_a,
            STAGE_B_TABLE_NAME: stage_b,
        }
```

### __init__.py skeleton

```python
from adorable_thunder.make.record_generators.schemas import CreatePgTableSql

from . import stage_a, stage_b
from .flow import FLOW_NAME, GeneratorConfig

FLOW_SCHEMAS: list[CreatePgTableSql] = [
    stage_a.create_pg_sql_table_schema(FLOW_NAME),
    stage_b.create_pg_sql_table_schema(FLOW_NAME),
]

__all__ = ["GeneratorConfig", "FLOW_SCHEMAS"]
```

---

## PgColumn data types

| Python type | Postgres type |
|---|---|
| UUID | `UUID` |
| String identifier / name | `TEXT` |
| Short code (3-char) | `VARCHAR(3)` |
| Integer count | `INTEGER` |
| Money / decimal | `NUMERIC(18, 2)` |
| Date only | `DATE` |
| Date + time | `TIMESTAMP` |

Common modifiers: `PRIMARY KEY`, `NOT NULL`, `REFERENCES schema.table(col)`
