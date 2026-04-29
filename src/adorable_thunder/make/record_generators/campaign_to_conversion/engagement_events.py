import numpy as np
import pandas as pd

from adorable_thunder.make.field_generators._random_state import get_random_state
from adorable_thunder.make.field_generators.dates import extrapolate_off_dates
from adorable_thunder.make.field_generators.identifiers import generate_n_random_uuids
from adorable_thunder.make.record_generators.schemas import CreatePgTableSql, PgColumn

_EVENT_TYPES = np.array(["click", "open", "video_view", "scroll", "form_start"])
_EVENT_TYPE_WEIGHTS = np.array([0.40, 0.30, 0.15, 0.10, 0.05])

_DEVICES = np.array(["desktop", "mobile", "tablet"])
_DEVICE_WEIGHTS = np.array([0.50, 0.40, 0.10])

ENGAGEMENT_EVENTS_TABLE_NAME = "engagement_events"


def create_pg_sql_table_schema(pg_schema: str) -> CreatePgTableSql:
    return CreatePgTableSql(
        pg_schema=pg_schema,
        pg_table=ENGAGEMENT_EVENTS_TABLE_NAME,
        llm_description="Contact interactions with a campaign after receiving an impression (clicks, opens, video views, etc.). Engagement events are a subset of impressions — not every impression generates an engagement.",
        pg_columns=[
            PgColumn(
                name="event_id",
                data_type="UUID",
                modifiers="PRIMARY KEY",
                llm_description="Unique identifier for this engagement event.",
                llm_example_values="'d4e5f6a7-b8c9-0123-defa-234567890123'",
            ),
            PgColumn(
                name="impression_id",
                data_type="UUID",
                modifiers="NOT NULL",
                llm_description="Foreign key to the impression that prompted this engagement.",
                llm_example_values="'b2c3d4e5-f6a7-8901-bcde-f12345678901'",
            ),
            PgColumn(
                name="campaign_id",
                data_type="UUID",
                modifiers="NOT NULL",
                llm_description="Foreign key to the campaign. Denormalised from impression for query convenience.",
                llm_example_values="'a1b2c3d4-e5f6-7890-abcd-ef1234567890'",
            ),
            PgColumn(
                name="contact_id",
                data_type="UUID",
                modifiers="NOT NULL",
                llm_description="Contact who engaged. Must match the contact_id on the parent impression.",
                llm_example_values="'c3d4e5f6-a7b8-9012-cdef-123456789012'",
            ),
            PgColumn(
                name="event_type",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Type of engagement. Mix: click ~40%, open ~30%, video_view ~15%, scroll ~10%, form_start ~5%.",
                llm_example_values="'click', 'open', 'video_view', 'scroll', 'form_start'",
            ),
            PgColumn(
                name="engagement_date",
                data_type="DATE",
                modifiers="NOT NULL",
                llm_description="Date of engagement. Must be ≥ impression_date and within the campaign window.",
                llm_example_values="'2024-03-11', '2024-07-23'",
            ),
            PgColumn(
                name="device",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Device type used. Mix: desktop ~50%, mobile ~40%, tablet ~10%.",
                llm_example_values="'desktop', 'mobile', 'tablet'",
            ),
        ],
    )


def generate_engagement_events(
    n_samples: int,
    impression_ids: np.ndarray,
    campaign_ids: np.ndarray,
    contact_ids: np.ndarray,
    impression_dates: pd.Series,
) -> pd.DataFrame:
    # Engagements happen 0–2 days after impression
    engagement_dates = extrapolate_off_dates(impression_dates, min_days=0, max_days=2)

    return pd.DataFrame(
        {
            "event_id": generate_n_random_uuids(n_samples),
            "impression_id": impression_ids,
            "campaign_id": campaign_ids,
            "contact_id": contact_ids,
            "event_type": get_random_state().choice(_EVENT_TYPES, p=_EVENT_TYPE_WEIGHTS, size=n_samples),
            "engagement_date": engagement_dates,
            "device": get_random_state().choice(_DEVICES, p=_DEVICE_WEIGHTS, size=n_samples),
        }
    )
