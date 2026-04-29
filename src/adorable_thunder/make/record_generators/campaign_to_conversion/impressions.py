import numpy as np
import pandas as pd

from adorable_thunder.make.field_generators._random_state import get_random_state
from adorable_thunder.make.field_generators.dates import choose_random_date_between_dates
from adorable_thunder.make.field_generators.identifiers import generate_n_random_uuids
from adorable_thunder.make.record_generators.schemas import CreatePgTableSql, PgColumn

_PLACEMENTS = np.array(
    [
        "feed",
        "sidebar",
        "banner",
        "search_results",
        "email_body",
        "sponsored_content",
        "pre_roll",
        "homepage_hero",
    ]
)

IMPRESSIONS_TABLE_NAME = "impressions"


def create_pg_sql_table_schema(pg_schema: str) -> CreatePgTableSql:
    return CreatePgTableSql(
        pg_schema=pg_schema,
        pg_table=IMPRESSIONS_TABLE_NAME,
        llm_description="One row per ad/email impression served to a contact within a campaign window. Volume is highest in the funnel — every engagement and lead traces back to an impression.",
        pg_columns=[
            PgColumn(
                name="impression_id",
                data_type="UUID",
                modifiers="PRIMARY KEY",
                llm_description="Unique identifier for this impression event.",
                llm_example_values="'b2c3d4e5-f6a7-8901-bcde-f12345678901'",
            ),
            PgColumn(
                name="campaign_id",
                data_type="UUID",
                modifiers="NOT NULL",
                llm_description="Foreign key to the campaign that generated this impression.",
                llm_example_values="'a1b2c3d4-e5f6-7890-abcd-ef1234567890'",
            ),
            PgColumn(
                name="contact_id",
                data_type="UUID",
                modifiers="NOT NULL",
                llm_description="Identifier for the contact who received the impression. Not unique within the table — same contact may receive multiple impressions.",
                llm_example_values="'c3d4e5f6-a7b8-9012-cdef-123456789012'",
            ),
            PgColumn(
                name="impression_date",
                data_type="DATE",
                modifiers="NOT NULL",
                llm_description="Date the impression was served. Must fall between campaign start_date and end_date.",
                llm_example_values="'2024-03-10', '2024-07-22'",
            ),
            PgColumn(
                name="channel",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Channel of this impression, inherited from the parent campaign.",
                llm_example_values="'Email', 'Paid Search', 'Display'",
            ),
            PgColumn(
                name="placement",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Ad placement or slot where the impression appeared.",
                llm_example_values="'feed', 'sidebar', 'banner', 'email_body', 'search_results'",
            ),
        ],
    )


def generate_impressions(
    campaign_ids: np.ndarray,
    campaign_channels: np.ndarray,
    campaign_starts: pd.Series,
    campaign_ends: pd.Series,
    contact_pool_size: int = 50_000,
) -> pd.DataFrame:
    """Generate one impression row per element in campaign_ids.

    Caller is responsible for pre-expanding campaign arrays to per-impression length
    (e.g. via np.repeat) so that each row maps to exactly one campaign.
    """
    n = len(campaign_ids)
    impression_dates = choose_random_date_between_dates(campaign_starts, campaign_ends)

    return pd.DataFrame(
        {
            "impression_id": generate_n_random_uuids(n),
            "campaign_id": campaign_ids,
            "contact_id": generate_n_random_uuids(contact_pool_size)[
                get_random_state().randint(0, contact_pool_size, size=n)
            ],
            "impression_date": impression_dates,
            "channel": campaign_channels,
            "placement": get_random_state().choice(_PLACEMENTS, size=n),
        }
    )
