import numpy as np
import pandas as pd

from adorable_thunder.make.field_generators._random_state import get_random_state
from adorable_thunder.make.field_generators.dates import extrapolate_off_dates
from adorable_thunder.make.field_generators.identifiers import (
    generate_n_random_uuids,
    generate_serial_numbers_with_prefix,
)
from adorable_thunder.make.record_generators.schemas import CreatePgTableSql, PgColumn

_FORM_TYPES = np.array(
    ["contact_form", "demo_request", "whitepaper_download", "webinar_registration", "free_trial"]
)
_FORM_TYPE_WEIGHTS = np.array([0.25, 0.25, 0.20, 0.20, 0.10])

_SOURCE_MEDIUMS = np.array(["cpc", "organic", "email", "social", "referral", "direct"])
_SOURCE_MEDIUM_WEIGHTS = np.array([0.30, 0.20, 0.20, 0.15, 0.10, 0.05])

LEAD_CAPTURES_TABLE_NAME = "lead_captures"


def create_pg_sql_table_schema(pg_schema: str) -> CreatePgTableSql:
    return CreatePgTableSql(
        pg_schema=pg_schema,
        pg_table=LEAD_CAPTURES_TABLE_NAME,
        llm_description="Form submissions and registrations that convert an anonymous contact into a known lead. One contact should generate at most one lead capture per campaign.",
        pg_columns=[
            PgColumn(
                name="lead_id",
                data_type="UUID",
                modifiers="PRIMARY KEY",
                llm_description="Unique identifier for this lead capture.",
                llm_example_values="'e5f6a7b8-c9d0-1234-efab-345678901234'",
            ),
            PgColumn(
                name="lead_number",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Human-readable sequential lead reference.",
                llm_example_values="'LEAD-000001', 'LEAD-009999'",
            ),
            PgColumn(
                name="campaign_id",
                data_type="UUID",
                modifiers="NOT NULL",
                llm_description="Campaign that sourced this lead.",
                llm_example_values="'a1b2c3d4-e5f6-7890-abcd-ef1234567890'",
            ),
            PgColumn(
                name="contact_id",
                data_type="UUID",
                modifiers="NOT NULL",
                llm_description="Contact who submitted the form. Should be unique per campaign — no duplicate lead captures for the same contact within the same campaign.",
                llm_example_values="'c3d4e5f6-a7b8-9012-cdef-123456789012'",
            ),
            PgColumn(
                name="form_type",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Type of form submitted. Mix: contact_form ~25%, demo_request ~25%, whitepaper_download ~20%, webinar_registration ~20%, free_trial ~10%.",
                llm_example_values="'contact_form', 'demo_request', 'whitepaper_download', 'webinar_registration', 'free_trial'",
            ),
            PgColumn(
                name="captured_date",
                data_type="DATE",
                modifiers="NOT NULL",
                llm_description="Date the lead form was submitted. Must be ≥ engagement_date and within campaign window.",
                llm_example_values="'2024-03-12', '2024-07-25'",
            ),
            PgColumn(
                name="source_medium",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="UTM medium of the converting visit. Mix: cpc ~30%, organic ~20%, email ~20%, social ~15%, referral ~10%, direct ~5%.",
                llm_example_values="'cpc', 'organic', 'email', 'social', 'referral'",
            ),
        ],
    )


def generate_lead_captures(
    n_samples: int,
    campaign_ids: np.ndarray,
    contact_ids: np.ndarray,
    engagement_dates: pd.Series,
) -> pd.DataFrame:
    # Leads captured 0–3 days after engagement
    captured_dates = extrapolate_off_dates(engagement_dates, min_days=0, max_days=3)

    return pd.DataFrame(
        {
            "lead_id": generate_n_random_uuids(n_samples),
            "lead_number": generate_serial_numbers_with_prefix(
                n_samples, prefix="LEAD-", total_length=11
            ),
            "campaign_id": campaign_ids,
            "contact_id": contact_ids,
            "form_type": get_random_state().choice(_FORM_TYPES, p=_FORM_TYPE_WEIGHTS, size=n_samples),
            "captured_date": captured_dates,
            "source_medium": get_random_state().choice(
                _SOURCE_MEDIUMS, p=_SOURCE_MEDIUM_WEIGHTS, size=n_samples
            ),
        }
    )
