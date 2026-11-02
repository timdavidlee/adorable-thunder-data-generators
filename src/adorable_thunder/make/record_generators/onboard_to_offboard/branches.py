import numpy as np
import pandas as pd

from adorable_thunder.make.field_generators.dates import generate_random_dates
from adorable_thunder.make.record_generators.schemas import CreatePgTableSql, PgColumn

# (region, city, number of branches, share of clients)
REGIONS: list[tuple[str, str, int, float]] = [
    ("Almaty", "Almaty", 6, 0.28),
    ("Astana", "Astana", 5, 0.22),
    ("Shymkent", "Shymkent", 3, 0.14),
    ("Karaganda", "Karaganda", 4, 0.14),
    ("Aktobe", "Aktobe", 3, 0.11),
    ("Atyrau", "Atyrau", 3, 0.11),
]

BRANCHES_TABLE_NAME = "branches"


def create_pg_sql_table_schema(pg_schema: str) -> CreatePgTableSql:
    return CreatePgTableSql(
        pg_schema=pg_schema,
        pg_table=BRANCHES_TABLE_NAME,
        llm_description="Bank branches where small-business clients are onboarded and served.",
        pg_columns=[
            PgColumn(
                name="branch_id",
                data_type="TEXT",
                modifiers="PRIMARY KEY",
                llm_description="Branch code.",
                llm_example_values="'BR-01', 'BR-24'",
            ),
            PgColumn(
                name="branch_name",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Display name: city plus branch number.",
                llm_example_values="'Almaty No. 3', 'Karaganda No. 1'",
            ),
            PgColumn(
                name="region",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Region the branch reports to.",
                llm_example_values="'Almaty', 'Astana', 'Karaganda'",
            ),
            PgColumn(
                name="city",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="City the branch is in.",
                llm_example_values="'Almaty', 'Shymkent'",
            ),
            PgColumn(
                name="opened_on",
                data_type="DATE",
                modifiers="NOT NULL",
                llm_description="Date the branch opened; before any client onboarded there.",
                llm_example_values="'2009-04-12'",
            ),
        ],
    )


def generate_branches() -> pd.DataFrame:
    rows: list[tuple[str, str, str]] = []
    for region, city, n_branches, _ in REGIONS:
        for number in range(1, n_branches + 1):
            rows.append((f"{city} No. {number}", region, city))
    n_rows = len(rows)
    return pd.DataFrame(
        {
            "branch_id": [f"BR-{i:02d}" for i in range(1, n_rows + 1)],
            "branch_name": [name for name, _, _ in rows],
            "region": [region for _, region, _ in rows],
            "city": [city for _, _, city in rows],
            "opened_on": generate_random_dates("2008-01-01", "2018-12-31", n_rows).dt.date,
        }
    )


def region_weights() -> tuple[np.ndarray, np.ndarray]:
    names = np.array([region for region, _, _, _ in REGIONS])
    weights = np.array([share for _, _, _, share in REGIONS])
    return names, weights / weights.sum()
