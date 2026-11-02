from datetime import date

import numpy as np
import pandas as pd

from adorable_thunder.make.field_generators._random_state import get_random_state
from adorable_thunder.make.field_generators.dates import generate_random_dates
from adorable_thunder.make.field_generators.kz_business import (
    generate_kz_bins,
    generate_kz_legal_names,
)
from adorable_thunder.make.record_generators.schemas import CreatePgTableSql, PgColumn

from .branches import region_weights

INDUSTRIES = np.array(
    [
        "retail_trade", "wholesale_import", "food_service", "construction",
        "transport_logistics", "agriculture", "professional_services", "manufacturing",
        "it_services", "beauty_health",
    ]
)  # fmt: skip
_INDUSTRY_WEIGHTS = np.array([0.22, 0.10, 0.11, 0.09, 0.10, 0.07, 0.10, 0.06, 0.07, 0.08])
SEGMENTS = np.array(["micro", "small", "medium"])
_SEGMENT_WEIGHTS = np.array([0.65, 0.30, 0.05])
# Clients onboarded before the dataset window form the existing book.
BOOK_START = "2019-01-01"

CLIENTS_TABLE_NAME = "clients"


def create_pg_sql_table_schema(pg_schema: str) -> CreatePgTableSql:
    return CreatePgTableSql(
        pg_schema=pg_schema,
        pg_table=CLIENTS_TABLE_NAME,
        llm_description=(
            "Small-business clients of the bank: individual entrepreneurs (IE) and limited "
            "liability partnerships (LLP), each served by one home branch."
        ),
        pg_columns=[
            PgColumn(
                name="client_id",
                data_type="TEXT",
                modifiers="PRIMARY KEY",
                llm_description="Client number.",
                llm_example_values="'CL-000001', 'CL-002417'",
            ),
            PgColumn(
                name="legal_name",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Registered name. Not unique: several IEs can share a name.",
                llm_example_values="'IE Abenov K.', 'Samal Logistics LLP'",
            ),
            PgColumn(
                name="legal_form",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="IE (individual entrepreneur) ~70%, LLP ~30%.",
                llm_example_values="'IE', 'LLP'",
            ),
            PgColumn(
                name="bin",
                data_type="TEXT",
                modifiers="NOT NULL UNIQUE",
                llm_description="12-digit business identification number; starts with YYMM.",
                llm_example_values="'210360004512'",
            ),
            PgColumn(
                name="industry",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Main line of business.",
                llm_example_values="'retail_trade', 'agriculture', 'it_services'",
            ),
            PgColumn(
                name="segment",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Size segment: micro ~65%, small ~30%, medium ~5%.",
                llm_example_values="'micro', 'small', 'medium'",
            ),
            PgColumn(
                name="region",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Region of the client's home branch.",
                llm_example_values="'Almaty', 'Karaganda'",
            ),
            PgColumn(
                name="branch_id",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Home branch; FK to branches.",
                llm_example_values="'BR-07'",
            ),
            PgColumn(
                name="onboarded_on",
                data_type="DATE",
                modifiers="NOT NULL",
                llm_description="Date the client relationship began; after the branch opened.",
                llm_example_values="'2020-06-15', '2025-02-03'",
            ),
        ],
    )


def generate_clients(n_samples: int, branches: pd.DataFrame, end_date: str) -> pd.DataFrame:
    rng = get_random_state()
    region_names, weights = region_weights()
    regions = rng.choice(region_names, p=weights, size=n_samples)
    branches_by_region: dict[str, list[str]] = {}
    for branch_id, region in zip(branches["branch_id"], branches["region"], strict=True):
        branches_by_region.setdefault(str(region), []).append(str(branch_id))
    branch_ids = np.array([rng.choice(branches_by_region[str(r)]) for r in regions])
    industries = rng.choice(INDUSTRIES, p=_INDUSTRY_WEIGHTS, size=n_samples)
    legal_forms = np.where(rng.random_sample(n_samples) < 0.70, "IE", "LLP")
    onboarded: list[date] = list(generate_random_dates(BOOK_START, end_date, n_samples).dt.date)
    onboarded.sort()
    return pd.DataFrame(
        {
            "client_id": [f"CL-{i:06d}" for i in range(1, n_samples + 1)],
            "legal_name": generate_kz_legal_names(n_samples, legal_forms, industries),
            "legal_form": legal_forms,
            "bin": generate_kz_bins(n_samples, onboarded, legal_forms),
            "industry": industries,
            "segment": rng.choice(SEGMENTS, p=_SEGMENT_WEIGHTS, size=n_samples),
            "region": regions,
            "branch_id": branch_ids,
            "onboarded_on": onboarded,
        }
    )
