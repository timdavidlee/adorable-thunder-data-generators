import numpy as np
import pandas as pd

from adorable_thunder.make.field_generators._random_state import get_random_state
from adorable_thunder.make.field_generators.amounts import generate_amounts
from adorable_thunder.make.field_generators.dates import extrapolate_off_dates
from adorable_thunder.make.field_generators.identifiers import generate_n_random_uuids
from adorable_thunder.make.record_generators.schemas import CreatePgTableSql, PgColumn

_CONVERSION_TYPES = np.array(
    ["opportunity_created", "trial_started", "purchase", "demo_completed", "contract_signed"]
)
_CONVERSION_TYPE_WEIGHTS = np.array([0.35, 0.25, 0.20, 0.15, 0.05])

_ATTRIBUTION_MODELS = np.array(
    ["FIRST_TOUCH", "LAST_TOUCH", "LINEAR", "TIME_DECAY", "POSITION_BASED"]
)
_ATTRIBUTION_MODEL_WEIGHTS = np.array([0.20, 0.25, 0.20, 0.20, 0.15])

CONVERSIONS_TABLE_NAME = "conversions"


def create_pg_sql_table_schema(pg_schema: str) -> CreatePgTableSql:
    return CreatePgTableSql(
        pg_schema=pg_schema,
        pg_table=CONVERSIONS_TABLE_NAME,
        llm_description="Bottom-of-funnel events where a lead takes a high-value action (purchase, trial, opportunity). Each conversion references the lead and campaign it originated from. Revenue attribution may be split across campaigns in multi-touch models.",
        pg_columns=[
            PgColumn(
                name="conversion_id",
                data_type="UUID",
                modifiers="PRIMARY KEY",
                llm_description="Unique identifier for this conversion event.",
                llm_example_values="'f6a7b8c9-d0e1-2345-fabc-456789012345'",
            ),
            PgColumn(
                name="lead_id",
                data_type="UUID",
                modifiers="NOT NULL",
                llm_description="Foreign key to the lead capture that preceded this conversion.",
                llm_example_values="'e5f6a7b8-c9d0-1234-efab-345678901234'",
            ),
            PgColumn(
                name="campaign_id",
                data_type="UUID",
                modifiers="NOT NULL",
                llm_description="Campaign credited with this conversion under the chosen attribution model.",
                llm_example_values="'a1b2c3d4-e5f6-7890-abcd-ef1234567890'",
            ),
            PgColumn(
                name="conversion_date",
                data_type="DATE",
                modifiers="NOT NULL",
                llm_description="Date the conversion occurred. Must be ≥ lead captured_date.",
                llm_example_values="'2024-03-20', '2024-08-05'",
            ),
            PgColumn(
                name="conversion_type",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Type of conversion action. Mix: opportunity_created ~35%, trial_started ~25%, purchase ~20%, demo_completed ~15%, contract_signed ~5%.",
                llm_example_values="'opportunity_created', 'trial_started', 'purchase', 'demo_completed', 'contract_signed'",
            ),
            PgColumn(
                name="revenue_attributed",
                data_type="NUMERIC(18, 2)",
                modifiers="NOT NULL",
                llm_description="Revenue credited to this campaign under the attribution model. In multi-touch models, the sum across campaigns may exceed actual deal value — this is expected.",
                llm_example_values="'5000.00', '25000.00', '120000.00'",
            ),
            PgColumn(
                name="attribution_model",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Attribution model used. Mix: LAST_TOUCH ~25%, FIRST_TOUCH ~20%, LINEAR ~20%, TIME_DECAY ~20%, POSITION_BASED ~15%.",
                llm_example_values="'FIRST_TOUCH', 'LAST_TOUCH', 'LINEAR', 'TIME_DECAY', 'POSITION_BASED'",
            ),
        ],
    )


def generate_conversions(
    n_samples: int,
    lead_ids: np.ndarray,
    campaign_ids: np.ndarray,
    captured_dates: pd.Series,
) -> pd.DataFrame:
    # Conversions happen 1–30 days after lead capture (nurture cycle)
    conversion_dates = extrapolate_off_dates(captured_dates, min_days=1, max_days=30)

    revenue = generate_amounts(
        n_samples,
        min_amount=500.0,
        max_amount=500_000.0,
        mu=10.0,
        sigma=1.5,
    )

    return pd.DataFrame(
        {
            "conversion_id": generate_n_random_uuids(n_samples),
            "lead_id": lead_ids,
            "campaign_id": campaign_ids,
            "conversion_date": conversion_dates,
            "conversion_type": get_random_state().choice(
                _CONVERSION_TYPES, p=_CONVERSION_TYPE_WEIGHTS, size=n_samples
            ),
            "revenue_attributed": np.round(revenue, 2),
            "attribution_model": get_random_state().choice(
                _ATTRIBUTION_MODELS, p=_ATTRIBUTION_MODEL_WEIGHTS, size=n_samples
            ),
        }
    )
