import numpy as np
import pandas as pd

from adorable_thunder.make.field_generators.identifiers import generate_n_random_uuids
from adorable_thunder.make.record_generators.schemas import CreatePgTableSql, PgColumn

_USAGE_METRICS = np.array(["seats", "api_calls", "gb_storage", "events"])
_USAGE_METRIC_WEIGHTS = np.array([0.35, 0.35, 0.20, 0.10])

# Per-unit price by metric (USD); broad ranges by metric type.
_METRIC_UNIT_PRICE: dict[str, tuple[float, float]] = {
    "seats": (10.0, 80.0),
    "api_calls": (0.0001, 0.01),
    "gb_storage": (0.05, 0.50),
    "events": (0.001, 0.05),
}

# Quantity scale per metric.
_METRIC_QTY_RANGE: dict[str, tuple[int, int]] = {
    "seats": (5, 500),
    "api_calls": (10_000, 5_000_000),
    "gb_storage": (10, 10_000),
    "events": (1_000, 1_000_000),
}

USAGE_FRACTION = 0.30
USAGE_RECORDS_TABLE_NAME = "usage_records"


def create_pg_sql_table_schema(pg_schema: str) -> CreatePgTableSql:
    return CreatePgTableSql(
        pg_schema=pg_schema,
        pg_table=USAGE_RECORDS_TABLE_NAME,
        llm_description=(
            "Metered usage records for usage-based subscriptions (~30% of subs). One record per "
            "subscription per billing period reports the metered metric, quantity, and resulting "
            "amount = quantity × unit_price. Periods follow the subscription billing cycle."
        ),
        pg_columns=[
            PgColumn(
                name="usage_id",
                data_type="UUID",
                modifiers="PRIMARY KEY",
                llm_description="Unique identifier for the usage record.",
                llm_example_values="'d4e5f6a7-b8c9-0123-defa-456789012345'",
            ),
            PgColumn(
                name="sub_id",
                data_type="UUID",
                modifiers="NOT NULL",
                llm_description="Foreign key to the subscription this usage applies to.",
                llm_example_values="'a1b2c3d4-e5f6-7890-abcd-ef1234567890'",
            ),
            PgColumn(
                name="period_start",
                data_type="DATE",
                modifiers="NOT NULL",
                llm_description="Inclusive start of the metered period.",
                llm_example_values="'2024-02-01'",
            ),
            PgColumn(
                name="period_end",
                data_type="DATE",
                modifiers="NOT NULL",
                llm_description="Exclusive end of the metered period.",
                llm_example_values="'2024-03-01'",
            ),
            PgColumn(
                name="metric",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Type of usage being metered.",
                llm_example_values="'seats', 'api_calls', 'gb_storage', 'events'",
            ),
            PgColumn(
                name="quantity",
                data_type="NUMERIC(18, 2)",
                modifiers="NOT NULL",
                llm_description="Metered quantity for the period.",
                llm_example_values="'150.00', '2500000.00', '8.50'",
            ),
            PgColumn(
                name="unit_price",
                data_type="NUMERIC(18, 6)",
                modifiers="NOT NULL",
                llm_description="Per-unit price applied to the quantity.",
                llm_example_values="'25.000000', '0.000500', '0.150000'",
            ),
            PgColumn(
                name="amount",
                data_type="NUMERIC(18, 2)",
                modifiers="NOT NULL",
                llm_description="Computed charge: quantity × unit_price, rounded to cents.",
                llm_example_values="'3750.00', '1250.00'",
            ),
        ],
    )


def _months_between(start: pd.Timestamp, end: pd.Timestamp) -> int:
    return (end.year - start.year) * 12 + (end.month - start.month)


def generate_usage_records(
    sub_ids: np.ndarray,
    sub_start_dates: pd.Series,
    sub_end_dates: pd.Series,
    billing_cycle_months: np.ndarray,
    churn_dates: pd.Series,
    dataset_end: str,
) -> pd.DataFrame:
    n = len(sub_ids)
    has_usage = np.random.random(n) < USAGE_FRACTION
    usage_idx = np.where(has_usage)[0]
    if len(usage_idx) == 0:
        return pd.DataFrame(
            columns=[
                "usage_id",
                "sub_id",
                "period_start",
                "period_end",
                "metric",
                "quantity",
                "unit_price",
                "amount",
            ]
        )

    sub_metrics = np.random.choice(_USAGE_METRICS, p=_USAGE_METRIC_WEIGHTS, size=len(usage_idx))
    dataset_end_ts = pd.Timestamp(dataset_end)
    starts = pd.to_datetime(sub_start_dates).reset_index(drop=True)
    ends = pd.to_datetime(sub_end_dates).reset_index(drop=True)
    churns = pd.to_datetime(churn_dates).reset_index(drop=True)

    rows: list[dict[str, object]] = []
    for j, i_raw in enumerate(usage_idx):
        i = int(i_raw)
        metric = sub_metrics[j]
        qty_lo, qty_hi = _METRIC_QTY_RANGE[metric]
        price_lo, price_hi = _METRIC_UNIT_PRICE[metric]
        # Per-subscription baseline so a sub stays in a band rather than swinging wildly.
        base_qty = np.random.uniform(qty_lo, qty_hi)
        unit_price = round(np.random.uniform(price_lo, price_hi), 6)

        start: pd.Timestamp = starts.iloc[i]
        end: pd.Timestamp = ends.iloc[i]
        churn: pd.Timestamp = churns.iloc[i]
        cap = min(end, dataset_end_ts)
        if pd.notna(churn):
            cap = min(cap, churn)
        if cap <= start:
            continue

        cycle = int(billing_cycle_months[i])
        max_periods = _months_between(start, cap) // cycle
        for period_idx in range(max_periods):
            period_start = start + pd.DateOffset(months=period_idx * cycle)
            period_end = start + pd.DateOffset(months=(period_idx + 1) * cycle)
            # ±25% noise around the baseline.
            qty = max(0.0, base_qty * np.random.uniform(0.75, 1.25))
            qty = round(qty, 2)
            amount = round(qty * unit_price, 2)
            rows.append(
                {
                    "sub_id": sub_ids[i],
                    "period_start": period_start,
                    "period_end": period_end,
                    "metric": metric,
                    "quantity": qty,
                    "unit_price": unit_price,
                    "amount": amount,
                }
            )

    df = pd.DataFrame(rows)
    n_rows = len(df)
    if n_rows == 0:
        return pd.DataFrame(
            columns=[
                "usage_id",
                "sub_id",
                "period_start",
                "period_end",
                "metric",
                "quantity",
                "unit_price",
                "amount",
            ]
        )

    df.insert(0, "usage_id", generate_n_random_uuids(n_rows))
    return df[
        [
            "usage_id",
            "sub_id",
            "period_start",
            "period_end",
            "metric",
            "quantity",
            "unit_price",
            "amount",
        ]
    ]
