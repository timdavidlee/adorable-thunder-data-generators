import numpy as np
import pandas as pd

from adorable_thunder.make.field_generators._random_state import get_random_state
from adorable_thunder.make.field_generators.dates import generate_random_dates
from adorable_thunder.make.field_generators.identifiers import generate_n_random_uuids
from adorable_thunder.make.field_generators.users import generate_user_emails
from adorable_thunder.make.record_generators.schemas import CreatePgTableSql, PgColumn

CYCLE_COUNTS_TABLE_NAME = "cycle_counts"

# Per the brief: counts with |variance|/system_qty > 1% should be rare (<1–2%).
# Within "rare", split between mid (~1.5%) and large (~3%) variances.
_NO_VARIANCE_RATE = 0.85  # exact match
_SMALL_VARIANCE_RATE = 0.13  # ±1–3 units, well under 1% on most lines
_MID_VARIANCE_RATE = 0.015  # ~1–2% of system_qty
_LARGE_VARIANCE_RATE = 0.005  # ~3–8% of system_qty
# (sum = 1.0)

assert abs(
    _NO_VARIANCE_RATE + _SMALL_VARIANCE_RATE + _MID_VARIANCE_RATE + _LARGE_VARIANCE_RATE - 1.0
) < 1e-9


def create_pg_sql_table_schema(pg_schema: str) -> CreatePgTableSql:
    return CreatePgTableSql(
        pg_schema=pg_schema,
        pg_table=CYCLE_COUNTS_TABLE_NAME,
        llm_description=(
            "Periodic cycle-count audits comparing system_qty to a physical counted_qty "
            "for a single SKU at a single location. ~85% of counts match exactly; ~13% "
            "show negligible variance (±1–3 units); ~2% show variance that exceeds the "
            "1% investigation threshold. variance_qty = system_qty − counted_qty (positive "
            "= shortage)."
        ),
        pg_columns=[
            PgColumn(
                name="count_id",
                data_type="UUID",
                modifiers="PRIMARY KEY",
                llm_description="Unique identifier for the cycle count row.",
                llm_example_values="'f6a7b8c9-d0e1-2345-fabc-456789012345'",
            ),
            PgColumn(
                name="location_id",
                data_type="UUID",
                modifiers="NOT NULL",
                llm_description="Foreign key to storage_locations.location_id.",
                llm_example_values="'a1b2c3d4-e5f6-7890-abcd-ef1234567890'",
            ),
            PgColumn(
                name="sku",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="SKU at the location. Matches storage_locations.sku for the row.",
                llm_example_values="'PROD-0012345', 'PERISH-0004001'",
            ),
            PgColumn(
                name="system_qty",
                data_type="INTEGER",
                modifiers="NOT NULL",
                llm_description=(
                    "Quantity recorded in the WMS at the time of the count. Equals "
                    "storage_locations.current_qty for the matched row."
                ),
                llm_example_values="'120', '850', '4200'",
            ),
            PgColumn(
                name="counted_qty",
                data_type="INTEGER",
                modifiers="NOT NULL",
                llm_description=(
                    "Quantity physically counted by the auditor. Differs from system_qty "
                    "for the ~15% of counts with any variance."
                ),
                llm_example_values="'120', '849', '4135'",
            ),
            PgColumn(
                name="variance_qty",
                data_type="INTEGER",
                modifiers="NOT NULL",
                llm_description=(
                    "system_qty − counted_qty. Positive values are inventory shortages; "
                    "negative values are overages."
                ),
                llm_example_values="'0', '1', '-1', '65'",
            ),
            PgColumn(
                name="variance_pct",
                data_type="NUMERIC(7, 4)",
                modifiers="NOT NULL",
                llm_description=(
                    "variance_qty / system_qty as a percentage. Counts with |variance_pct| "
                    "> 1.0 trigger investigation."
                ),
                llm_example_values="'0.0000', '0.1176', '1.5476', '4.2300'",
            ),
            PgColumn(
                name="count_date",
                data_type="DATE",
                modifiers="NOT NULL",
                llm_description="Date the cycle count was performed.",
                llm_example_values="'2024-08-12', '2025-11-30'",
            ),
            PgColumn(
                name="counter",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Email of the warehouse worker who performed the count.",
                llm_example_values="'jane.doe@example.com'",
            ),
        ],
    )


def _sample_variance(system_qty: np.ndarray, rng: np.random.RandomState) -> np.ndarray:
    n = len(system_qty)
    bucket = rng.choice(
        np.array(["none", "small", "mid", "large"]),
        p=np.array(
            [
                _NO_VARIANCE_RATE,
                _SMALL_VARIANCE_RATE,
                _MID_VARIANCE_RATE,
                _LARGE_VARIANCE_RATE,
            ]
        ),
        size=n,
    )

    variance = np.zeros(n, dtype=int)
    small_mask = bucket == "small"
    mid_mask = bucket == "mid"
    large_mask = bucket == "large"

    if small_mask.any():
        # Sub-1% variance: bound by 0.5% of system_qty so this bucket never crosses the
        # 1% investigation threshold. When 0.5% of system_qty rounds to zero (small
        # SKUs), the variance is zero — the line stays an exact match.
        n_small = int(small_mask.sum())
        cap = np.floor(system_qty[small_mask] * 0.005).astype(int)
        sign = rng.choice(np.array([-1, 1]), size=n_small)
        magnitude = np.floor(rng.random(size=n_small) * (cap + 1)).astype(int)
        variance[small_mask] = sign * magnitude

    if mid_mask.any():
        sign = rng.choice(np.array([-1, 1]), size=int(mid_mask.sum()))
        magnitude = np.ceil(
            system_qty[mid_mask] * rng.uniform(0.011, 0.025, size=int(mid_mask.sum()))
        ).astype(int)
        variance[mid_mask] = sign * np.maximum(magnitude, 1)

    if large_mask.any():
        sign = rng.choice(np.array([-1, 1]), size=int(large_mask.sum()))
        magnitude = np.ceil(
            system_qty[large_mask] * rng.uniform(0.03, 0.08, size=int(large_mask.sum()))
        ).astype(int)
        variance[large_mask] = sign * np.maximum(magnitude, 1)

    return variance


def generate_cycle_counts(
    n_samples: int,
    storage_locations: pd.DataFrame,
    start_date: str = "2024-01-01",
    end_date: str = "2025-12-31",
) -> pd.DataFrame:
    rng = get_random_state()

    populated = storage_locations[storage_locations["sku"].notna()].reset_index(drop=True)
    if len(populated) == 0:
        return pd.DataFrame(
            {
                "count_id": np.array([], dtype=object),
                "location_id": np.array([], dtype=object),
                "sku": np.array([], dtype=object),
                "system_qty": np.array([], dtype=int),
                "counted_qty": np.array([], dtype=int),
                "variance_qty": np.array([], dtype=int),
                "variance_pct": np.array([], dtype=float),
                "count_date": pd.Series([], dtype="datetime64[ns]"),
                "counter": np.array([], dtype=object),
            }
        )

    indices = rng.randint(0, len(populated), size=n_samples)
    chosen = populated.iloc[indices].reset_index(drop=True)
    system_qty = chosen["current_qty"].to_numpy().astype(int)
    system_qty = np.maximum(system_qty, 1)

    variance_qty = _sample_variance(system_qty, rng)
    counted_qty = np.maximum(system_qty - variance_qty, 0)
    variance_pct = np.round(np.abs(variance_qty) / system_qty * 100, 4)

    return pd.DataFrame(
        {
            "count_id": generate_n_random_uuids(n_samples),
            "location_id": chosen["location_id"].to_numpy(),
            "sku": chosen["sku"].to_numpy(),
            "system_qty": system_qty,
            "counted_qty": counted_qty,
            "variance_qty": variance_qty,
            "variance_pct": variance_pct,
            "count_date": generate_random_dates(start_date, end_date, n_samples),
            "counter": generate_user_emails(n_samples),
        }
    )
