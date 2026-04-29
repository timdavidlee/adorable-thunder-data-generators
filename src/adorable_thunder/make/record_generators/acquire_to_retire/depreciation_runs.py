import pandas as pd

from adorable_thunder.make.field_generators.identifiers import generate_n_random_uuids
from adorable_thunder.make.record_generators.schemas import CreatePgTableSql, PgColumn

DEPRECIATION_RUNS_TABLE_NAME = "depreciation_runs"

# Number of recent monthly periods to emit per active asset. Six gives a useful
# trailing trend without exploding row count for typical n=10k portfolios.
_TRAILING_MONTHS = 6


def create_pg_sql_table_schema(pg_schema: str) -> CreatePgTableSql:
    return CreatePgTableSql(
        pg_schema=pg_schema,
        pg_table=DEPRECIATION_RUNS_TABLE_NAME,
        llm_description=(
            "Monthly depreciation snapshots — one row per asset per fiscal period for the "
            "last 6 active months of each non-planned asset. book_value_end = "
            "book_value_start - depreciation_amount; book_value floored at salvage_value; "
            "accumulated_depreciation = cost - book_value_end."
        ),
        pg_columns=[
            PgColumn(
                name="run_id",
                data_type="UUID",
                modifiers="PRIMARY KEY",
                llm_description="Unique identifier for the depreciation run row.",
                llm_example_values="'b2c3d4e5-f6a7-8901-bcde-f23456789012'",
            ),
            PgColumn(
                name="asset_id",
                data_type="UUID",
                modifiers="NOT NULL",
                llm_description="Foreign key to assets.asset_id.",
                llm_example_values="'a1b2c3d4-e5f6-7890-abcd-ef1234567890'",
            ),
            PgColumn(
                name="period",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Fiscal period in FYxxxx-Pxx format (monthly grain).",
                llm_example_values="'FY2025-P11', 'FY2025-P12'",
            ),
            PgColumn(
                name="book_value_start",
                data_type="NUMERIC(18, 2)",
                modifiers="NOT NULL",
                llm_description="Net book value at the start of the period.",
                llm_example_values="'48000.00', '12500.00'",
            ),
            PgColumn(
                name="depreciation_amount",
                data_type="NUMERIC(18, 2)",
                modifiers="NOT NULL",
                llm_description=(
                    "Depreciation booked in this period. Approx cost / useful_life_years / 12 "
                    "for straight-line; zero once book_value reaches salvage_value."
                ),
                llm_example_values="'500.00', '2750.00', '0.00'",
            ),
            PgColumn(
                name="book_value_end",
                data_type="NUMERIC(18, 2)",
                modifiers="NOT NULL",
                llm_description=(
                    "Net book value at the end of the period. Equals book_value_start "
                    "minus depreciation_amount, floored at salvage_value."
                ),
                llm_example_values="'47500.00', '0.00'",
            ),
            PgColumn(
                name="accumulated_depreciation",
                data_type="NUMERIC(18, 2)",
                modifiers="NOT NULL",
                llm_description=(
                    "Total depreciation booked from acquisition through this period — "
                    "equals cost minus book_value_end."
                ),
                llm_example_values="'2500.00', '85000.00'",
            ),
        ],
    )


def _months_between(start_ts: pd.Timestamp, end_ts: pd.Timestamp) -> int:
    return (end_ts.year - start_ts.year) * 12 + (end_ts.month - start_ts.month)


def generate_depreciation_runs(
    assets: pd.DataFrame, dataset_end: str, disposals: pd.DataFrame | None = None
) -> pd.DataFrame:
    dataset_end_ts = pd.Timestamp(dataset_end)

    disposed_dates: dict[str, pd.Timestamp] = {}
    if disposals is not None and len(disposals) > 0:
        for asset_id_val, disposal_date_val in zip(
            disposals["asset_id"].to_list(), disposals["disposal_date"].to_list()
        ):
            disposed_dates[str(asset_id_val)] = pd.Timestamp(str(disposal_date_val))

    eligible = assets[assets["status"] != "planned"].reset_index(drop=True)
    asset_ids = eligible["asset_id"].to_list()
    costs = eligible["cost"].to_numpy().astype(float)
    salvages = eligible["salvage_value"].to_numpy().astype(float)
    useful_life_years = eligible["useful_life_years"].to_numpy().astype(int)
    acquisition_dates = pd.to_datetime(eligible["acquisition_date"])

    rows: list[dict[str, object]] = []

    for i in range(len(eligible)):
        asset_id = str(asset_ids[i])
        cost = float(costs[i])
        salvage = float(salvages[i])
        useful_life_months = int(useful_life_years[i]) * 12
        depreciation_per_month = round((cost - salvage) / useful_life_months, 2)

        acquisition_ts = acquisition_dates.iloc[i]
        first_dep_month = (acquisition_ts + pd.offsets.MonthBegin(1)).normalize()

        last_active_ts = disposed_dates.get(asset_id, dataset_end_ts)
        last_dep_month = pd.Timestamp(last_active_ts).to_period("M").to_timestamp()

        if last_dep_month < first_dep_month:
            continue

        total_months_from_first = _months_between(first_dep_month, last_dep_month) + 1
        n_runs = min(_TRAILING_MONTHS, total_months_from_first)
        first_run_month = last_dep_month - pd.DateOffset(months=n_runs - 1)

        for j in range(n_runs):
            period_ts = first_run_month + pd.DateOffset(months=j)
            months_active_at_start = _months_between(first_dep_month, period_ts)
            accumulated_at_start = min(
                round(depreciation_per_month * months_active_at_start, 2),
                round(cost - salvage, 2),
            )
            book_value_start = round(cost - accumulated_at_start, 2)

            book_value_end = max(round(book_value_start - depreciation_per_month, 2), salvage)
            depreciation_amount = round(book_value_start - book_value_end, 2)
            accumulated_depreciation = round(cost - book_value_end, 2)

            period = f"FY{period_ts.year}-P{period_ts.month:02d}"
            rows.append(
                {
                    "asset_id": asset_id,
                    "period": period,
                    "book_value_start": book_value_start,
                    "depreciation_amount": depreciation_amount,
                    "book_value_end": book_value_end,
                    "accumulated_depreciation": accumulated_depreciation,
                }
            )

    if not rows:
        return pd.DataFrame(
            columns=[
                "run_id",
                "asset_id",
                "period",
                "book_value_start",
                "depreciation_amount",
                "book_value_end",
                "accumulated_depreciation",
            ]
        )

    df = pd.DataFrame(rows)
    df.insert(0, "run_id", generate_n_random_uuids(len(df)))
    return df[
        [
            "run_id",
            "asset_id",
            "period",
            "book_value_start",
            "depreciation_amount",
            "book_value_end",
            "accumulated_depreciation",
        ]
    ]
