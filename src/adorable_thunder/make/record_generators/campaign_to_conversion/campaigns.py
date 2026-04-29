import numpy as np
import pandas as pd

from adorable_thunder.make.field_generators._random_state import get_random_state
from adorable_thunder.make.field_generators.amounts import generate_amounts
from adorable_thunder.make.field_generators.dates import generate_random_dates
from adorable_thunder.make.field_generators.identifiers import (
    generate_n_random_uuids,
    generate_serial_numbers_with_prefix,
)
from adorable_thunder.make.record_generators.schemas import CreatePgTableSql, PgColumn

_CHANNELS = np.array(["Email", "Paid Search", "Paid Social", "Organic Search", "Display", "Events"])
_CHANNEL_WEIGHTS = np.array([0.25, 0.20, 0.20, 0.15, 0.12, 0.08])

_STATUSES = np.array(["active", "completed", "paused", "draft"])
_STATUS_WEIGHTS = np.array([0.40, 0.35, 0.15, 0.10])

_AUDIENCES = np.array(
    [
        "Enterprise Decision Makers",
        "SMB Owners",
        "Technical Practitioners",
        "Finance Leaders",
        "Marketing Professionals",
        "Procurement Managers",
    ]
)

CAMPAIGNS_TABLE_NAME = "campaigns"


def create_pg_sql_table_schema(pg_schema: str) -> CreatePgTableSql:
    return CreatePgTableSql(
        pg_schema=pg_schema,
        pg_table=CAMPAIGNS_TABLE_NAME,
        llm_description="Marketing campaigns run across channels. Each campaign has a budget, date range, target audience, and status. All downstream funnel events (impressions, engagements, leads, conversions) reference a campaign_id.",
        pg_columns=[
            PgColumn(
                name="campaign_id",
                data_type="UUID",
                modifiers="PRIMARY KEY",
                llm_description="Unique identifier for the campaign.",
                llm_example_values="'a1b2c3d4-e5f6-7890-abcd-ef1234567890'",
            ),
            PgColumn(
                name="campaign_name",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Human-readable campaign name.",
                llm_example_values="'CAMP-000123'",
            ),
            PgColumn(
                name="channel",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Marketing channel. Mix: Email ~25%, Paid Search ~20%, Paid Social ~20%, Organic Search ~15%, Display ~12%, Events ~8%.",
                llm_example_values="'Email', 'Paid Search', 'Paid Social', 'Display', 'Events'",
            ),
            PgColumn(
                name="start_date",
                data_type="DATE",
                modifiers="NOT NULL",
                llm_description="Date the campaign launched. All funnel events must fall between start_date and end_date.",
                llm_example_values="'2024-01-15', '2024-06-01'",
            ),
            PgColumn(
                name="end_date",
                data_type="DATE",
                modifiers="NOT NULL",
                llm_description="Date the campaign closed. Must be after start_date. Typical duration 7–90 days.",
                llm_example_values="'2024-02-15', '2024-08-31'",
            ),
            PgColumn(
                name="budget_usd",
                data_type="NUMERIC(18, 2)",
                modifiers="NOT NULL",
                llm_description="Total approved campaign budget in USD, calibrated to channel CPM so CPL lands in brief range. Email $20–$100; Paid Search $200–$600; Paid Social $100–$400; Display $50–$200; Events $300–$1,000.",
                llm_example_values="'55.00', '320.00', '750.00'",
            ),
            PgColumn(
                name="target_audience",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Persona or segment the campaign targets.",
                llm_example_values="'Enterprise Decision Makers', 'SMB Owners', 'Technical Practitioners'",
            ),
            PgColumn(
                name="status",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Campaign lifecycle status. Expected mix: active ~40%, completed ~35%, paused ~15%, draft ~10%.",
                llm_example_values="'active', 'completed', 'paused', 'draft'",
            ),
        ],
    )


def generate_campaigns(
    n_samples: int,
    start_date: str = "2024-01-01",
    end_date: str = "2025-12-31",
) -> pd.DataFrame:
    campaign_starts = generate_random_dates(start_date, end_date, n_samples)
    # Campaign durations: 7–90 days
    durations = get_random_state().randint(7, 91, size=n_samples)
    campaign_ends = campaign_starts + pd.to_timedelta(durations, unit="D")

    channels = get_random_state().choice(_CHANNELS, p=_CHANNEL_WEIGHTS, size=n_samples)

    # Budget ranges are calibrated to produce 500–1,000 impressions per campaign when
    # divided by the channel CPM rate in flow.py (CPM = CPL_midpoint × 0.0045 × 1000).
    budgets = np.where(
        np.isin(channels, ["Events"]),
        generate_amounts(n_samples, min_amount=300, max_amount=1_000, mu=6.5, sigma=0.5),
        np.where(
            np.isin(channels, ["Paid Search"]),
            generate_amounts(n_samples, min_amount=200, max_amount=600, mu=5.8, sigma=0.4),
            np.where(
                np.isin(channels, ["Paid Social"]),
                generate_amounts(n_samples, min_amount=100, max_amount=400, mu=5.5, sigma=0.4),
                np.where(
                    np.isin(channels, ["Display"]),
                    generate_amounts(n_samples, min_amount=50, max_amount=200, mu=4.8, sigma=0.4),
                    np.where(
                        np.isin(channels, ["Organic Search"]),
                        generate_amounts(
                            n_samples, min_amount=30, max_amount=120, mu=4.2, sigma=0.4
                        ),
                        generate_amounts(
                            n_samples, min_amount=20, max_amount=100, mu=3.9, sigma=0.4
                        ),
                    ),
                ),
            ),
        ),
    )

    return pd.DataFrame(
        {
            "campaign_id": generate_n_random_uuids(n_samples),
            "campaign_name": generate_serial_numbers_with_prefix(
                n_samples, prefix="CAMP-", total_length=12
            ),
            "channel": channels,
            "start_date": campaign_starts,
            "end_date": campaign_ends,
            "budget_usd": np.round(budgets, 2),
            "target_audience": get_random_state().choice(_AUDIENCES, size=n_samples),
            "status": get_random_state().choice(_STATUSES, p=_STATUS_WEIGHTS, size=n_samples),
        }
    )
