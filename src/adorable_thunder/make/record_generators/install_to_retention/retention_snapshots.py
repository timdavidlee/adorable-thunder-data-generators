import pandas as pd

from adorable_thunder.make.field_generators.identifiers import generate_n_random_uuids
from adorable_thunder.make.record_generators.schemas import CreatePgTableSql, PgColumn

RETENTION_SNAPSHOTS_TABLE_NAME = "retention_snapshots"

_DAY_OFFSETS_AND_FLAGS = [
    (1, "_retained_d1"),
    (7, "_retained_d7"),
    (30, "_retained_d30"),
]


def create_pg_sql_table_schema(pg_schema: str) -> CreatePgTableSql:
    return CreatePgTableSql(
        pg_schema=pg_schema,
        pg_table=RETENTION_SNAPSHOTS_TABLE_NAME,
        llm_description=(
            "Cohort retention snapshots aggregated from installs. One row per "
            "(cohort_date, source, platform, day_offset). cohort_date is the first day of the "
            "install month — monthly grain keeps cohort sizes meaningful at typical dataset "
            "scales. retention_rate = users_returned / cohort_size. users_returned must be "
            "monotonic non-increasing across day_offset within a cohort."
        ),
        pg_columns=[
            PgColumn(
                name="snapshot_id",
                data_type="UUID",
                modifiers="PRIMARY KEY",
                llm_description="Unique identifier for the cohort snapshot row.",
                llm_example_values="'f6a7b8c9-d0e1-2345-fabc-678901234567'",
            ),
            PgColumn(
                name="cohort_date",
                data_type="DATE",
                modifiers="NOT NULL",
                llm_description="First day of the install month — defines the cohort.",
                llm_example_values="'2024-01-01', '2025-06-01'",
            ),
            PgColumn(
                name="source",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Acquisition channel for the cohort.",
                llm_example_values="'ORGANIC_SEARCH', 'PAID_SOCIAL'",
            ),
            PgColumn(
                name="platform",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="OS platform for the cohort.",
                llm_example_values="'iOS', 'Android'",
            ),
            PgColumn(
                name="day_offset",
                data_type="INTEGER",
                modifiers="NOT NULL",
                llm_description="Days after install at which retention is measured.",
                llm_example_values="'1', '7', '30'",
            ),
            PgColumn(
                name="cohort_size",
                data_type="INTEGER",
                modifiers="NOT NULL",
                llm_description="Total installs in the cohort.",
                llm_example_values="'120', '45'",
            ),
            PgColumn(
                name="users_returned",
                data_type="INTEGER",
                modifiers="NOT NULL",
                llm_description=(
                    "Installs from the cohort that were active at day_offset. "
                    "Monotonic non-increasing across day_offset within a cohort."
                ),
                llm_example_values="'42', '18', '6'",
            ),
            PgColumn(
                name="retention_rate",
                data_type="NUMERIC(6, 4)",
                modifiers="NOT NULL",
                llm_description=(
                    "users_returned / cohort_size, rounded to 4 decimals. "
                    "Typical values: d1 0.25–0.40, d7 0.10–0.20, d30 0.03–0.08."
                ),
                llm_example_values="'0.3500', '0.1500', '0.0500'",
            ),
        ],
    )


def generate_retention_snapshots(installs: pd.DataFrame) -> pd.DataFrame:
    df = installs[
        [
            "install_id",
            "source",
            "platform",
            "installed_at",
            "_retained_d1",
            "_retained_d7",
            "_retained_d30",
        ]
    ].copy()
    # Monthly cohorts give meaningful sample sizes at typical dataset scales (n=10k).
    # Weekly buckets x source x platform leave many cohorts with size=1, forcing
    # retention_rate to 0/1 and breaking the analytical curve the table exists for.
    df["cohort_date"] = pd.to_datetime(df["installed_at"]).dt.to_period("M").dt.start_time

    pieces: list[pd.DataFrame] = []
    for offset, flag_col in _DAY_OFFSETS_AND_FLAGS:
        agg = (
            df.groupby(["cohort_date", "source", "platform"])
            .agg(cohort_size=("install_id", "count"), users_returned=(flag_col, "sum"))
            .reset_index()
        )
        agg["day_offset"] = offset
        pieces.append(agg)

    snapshots = pd.concat(pieces, ignore_index=True)
    snapshots["users_returned"] = snapshots["users_returned"].astype(int)
    snapshots["retention_rate"] = (
        snapshots["users_returned"] / snapshots["cohort_size"]
    ).round(4)
    snapshots.insert(0, "snapshot_id", generate_n_random_uuids(len(snapshots)))
    snapshots["cohort_date"] = snapshots["cohort_date"].dt.date
    return snapshots[
        [
            "snapshot_id",
            "cohort_date",
            "source",
            "platform",
            "day_offset",
            "cohort_size",
            "users_returned",
            "retention_rate",
        ]
    ]
