import numpy as np
import pandas as pd

from adorable_thunder.make.field_generators._random_state import get_random_state
from adorable_thunder.make.field_generators.identifiers import generate_n_random_uuids
from adorable_thunder.make.record_generators.schemas import CreatePgTableSql, PgColumn

DISPOSALS_TABLE_NAME = "disposals"

_DISPOSAL_TYPES = np.array(["SOLD", "SCRAPPED", "DONATED", "TRADE_IN", "LOST"])
_DISPOSAL_TYPE_WEIGHTS = np.array([0.55, 0.20, 0.05, 0.15, 0.05])

# Proceeds as a fraction of original cost, by asset class. Buildings can appreciate,
# IT depreciates fast, leasehold improvements rarely recover anything.
_PROCEEDS_RATE_BY_CLASS: dict[str, tuple[float, float]] = {
    "IT_EQUIPMENT": (0.10, 0.30),
    "OFFICE_FURNITURE": (0.05, 0.20),
    "VEHICLE": (0.30, 0.50),
    "LEASEHOLD_IMPROVEMENT": (0.00, 0.10),
    "BUILDING": (0.60, 1.50),
    "INTANGIBLE": (0.00, 0.10),
    "MACHINERY": (0.20, 0.40),
}


def create_pg_sql_table_schema(pg_schema: str) -> CreatePgTableSql:
    return CreatePgTableSql(
        pg_schema=pg_schema,
        pg_table=DISPOSALS_TABLE_NAME,
        llm_description=(
            "Asset retirement records — one row per disposed asset. proceeds vary by "
            "asset_class and disposal_type. gain_loss = proceeds - book_value_at_disposal "
            "(positive means a gain). disposal_date is always after acquisition_date."
        ),
        pg_columns=[
            PgColumn(
                name="disposal_id",
                data_type="UUID",
                modifiers="PRIMARY KEY",
                llm_description="Unique identifier for the disposal record.",
                llm_example_values="'c3d4e5f6-a7b8-9012-cdef-345678901234'",
            ),
            PgColumn(
                name="asset_id",
                data_type="UUID",
                modifiers="NOT NULL",
                llm_description="Foreign key to assets.asset_id.",
                llm_example_values="'a1b2c3d4-e5f6-7890-abcd-ef1234567890'",
            ),
            PgColumn(
                name="disposal_date",
                data_type="DATE",
                modifiers="NOT NULL",
                llm_description=(
                    "Date the asset was retired. Always after acquisition_date and on or "
                    "before the dataset end."
                ),
                llm_example_values="'2024-09-12', '2025-11-30'",
            ),
            PgColumn(
                name="disposal_type",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description=(
                    "Reason for retirement. SOLD ~55%, SCRAPPED ~20%, TRADE_IN ~15%, "
                    "DONATED ~5%, LOST ~5%."
                ),
                llm_example_values="'SOLD', 'SCRAPPED', 'TRADE_IN', 'DONATED', 'LOST'",
            ),
            PgColumn(
                name="proceeds",
                data_type="NUMERIC(18, 2)",
                modifiers="NOT NULL",
                llm_description=(
                    "Cash or trade-in value received. Zero for SCRAPPED, DONATED, and LOST. "
                    "Class-appropriate fraction of cost for SOLD/TRADE_IN."
                ),
                llm_example_values="'0.00', '12000.00', '4500000.00'",
            ),
            PgColumn(
                name="book_value_at_disposal",
                data_type="NUMERIC(18, 2)",
                modifiers="NOT NULL",
                llm_description=(
                    "Net book value at disposal_date — cost minus accumulated depreciation, "
                    "floored at salvage_value."
                ),
                llm_example_values="'1500.00', '0.00', '3200000.00'",
            ),
            PgColumn(
                name="gain_loss",
                data_type="NUMERIC(18, 2)",
                modifiers="NOT NULL",
                llm_description="proceeds minus book_value_at_disposal. Negative = loss.",
                llm_example_values="'-500.00', '0.00', '1300000.00'",
            ),
        ],
    )


def _months_between(start_ts: pd.Timestamp, end_ts: pd.Timestamp) -> int:
    return (end_ts.year - start_ts.year) * 12 + (end_ts.month - start_ts.month)


def generate_disposals(assets: pd.DataFrame, dataset_end: str) -> pd.DataFrame:
    disposed = assets[assets["status"] == "disposed"].reset_index(drop=True)
    n = len(disposed)
    if n == 0:
        return pd.DataFrame(
            columns=[
                "disposal_id",
                "asset_id",
                "disposal_date",
                "disposal_type",
                "proceeds",
                "book_value_at_disposal",
                "gain_loss",
            ]
        )

    dataset_end_ts = pd.Timestamp(dataset_end)
    acquisition_ts_list = pd.to_datetime(disposed["acquisition_date"]).to_list()
    costs = disposed["cost"].to_numpy().astype(float)
    salvage = disposed["salvage_value"].to_numpy().astype(float)
    useful_life_months = (disposed["useful_life_years"].to_numpy().astype(int)) * 12
    asset_classes = disposed["asset_class"].to_numpy()

    disposal_dates: list[pd.Timestamp] = []
    book_value_at_disposal = np.zeros(n, dtype=float)
    depreciation_per_month = np.round((costs - salvage) / useful_life_months, 2)

    for i in range(n):
        acquisition_ts = pd.Timestamp(acquisition_ts_list[i])
        # Disposal must be at least 1 year after acquisition and on or before dataset_end.
        min_disposal = acquisition_ts + pd.Timedelta(days=365)
        if min_disposal > dataset_end_ts:
            min_disposal = dataset_end_ts
        span_days = max((dataset_end_ts - min_disposal).days, 0)
        offset_days = int(get_random_state().random() * span_days) if span_days > 0 else 0
        disposal_ts = min_disposal + pd.Timedelta(days=offset_days)
        disposal_dates.append(disposal_ts)

        first_dep_month = (acquisition_ts + pd.offsets.MonthBegin(1)).normalize()
        disposal_month = disposal_ts.to_period("M").to_timestamp()
        months_active = max(_months_between(first_dep_month, disposal_month), 0)
        accumulated = min(
            round(float(depreciation_per_month[i]) * months_active, 2),
            round(float(costs[i]) - float(salvage[i]), 2),
        )
        book_value_at_disposal[i] = round(float(costs[i]) - accumulated, 2)

    disposal_types = get_random_state().choice(
        _DISPOSAL_TYPES, p=_DISPOSAL_TYPE_WEIGHTS, size=n
    )

    proceeds = np.zeros(n, dtype=float)
    for cls, (lo, hi) in _PROCEEDS_RATE_BY_CLASS.items():
        mask = asset_classes == cls
        if not mask.any():
            continue
        rates = get_random_state().uniform(lo, hi, size=int(mask.sum()))
        proceeds[mask] = np.round(costs[mask] * rates, 2)

    # Non-cash retirements yield no proceeds regardless of class.
    no_proceeds = np.isin(disposal_types, ["SCRAPPED", "DONATED", "LOST"])
    proceeds[no_proceeds] = 0.0

    gain_loss = np.round(proceeds - book_value_at_disposal, 2)

    return pd.DataFrame(
        {
            "disposal_id": generate_n_random_uuids(n),
            "asset_id": disposed["asset_id"].to_numpy(),
            "disposal_date": [ts.date() for ts in disposal_dates],
            "disposal_type": disposal_types,
            "proceeds": proceeds,
            "book_value_at_disposal": book_value_at_disposal,
            "gain_loss": gain_loss,
        }
    )
