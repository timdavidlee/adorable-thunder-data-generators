import numpy as np
import pandas as pd

from adorable_thunder.make.field_generators.amounts import generate_amounts
from adorable_thunder.make.field_generators.dates import extrapolate_off_dates
from adorable_thunder.make.field_generators.identifiers import (
    generate_n_random_uuids,
    generate_serial_numbers_with_prefix,
)
from adorable_thunder.make.field_generators.users import generate_user_emails
from adorable_thunder.make.record_generators.schemas import CreatePgTableSql, PgColumn

_STAGES = np.array(
    ["Prospecting", "Qualification", "Discovery", "Proposal", "Negotiation", "Closed Won", "Closed Lost"]
)
# Distribution: cluster in Qualification/Proposal; few in Negotiation; 20% closed (6% Won, 14% Lost)
_STAGE_WEIGHTS = np.array([0.08, 0.28, 0.22, 0.17, 0.05, 0.06, 0.14])

_STAGE_PROBABILITY: dict[str, float] = {
    "Prospecting": 5.0,
    "Qualification": 15.0,
    "Discovery": 25.0,
    "Proposal": 40.0,
    "Negotiation": 60.0,
    "Closed Won": 100.0,
    "Closed Lost": 0.0,
}

_SEGMENT_WEIGHTS = np.array([0.50, 0.35, 0.15])  # SMB, mid-market, enterprise

OPPORTUNITIES_TABLE_NAME = "opportunities"


def create_pg_sql_table_schema(pg_schema: str) -> CreatePgTableSql:
    return CreatePgTableSql(
        pg_schema=pg_schema,
        pg_table=OPPORTUNITIES_TABLE_NAME,
        llm_description="Sales pipeline opportunities linked to qualified contacts. Stage clusters in Qualification (~28%) and Proposal (~17%). Win rate ~30% of closed (Closed Won / (Closed Won + Closed Lost)). Deal values span SMB ($5k-$50k), mid-market ($50k-$500k), and enterprise ($500k-$5M+).",
        pg_columns=[
            PgColumn(
                name="opp_id",
                data_type="UUID",
                modifiers="PRIMARY KEY",
                llm_description="Unique identifier for the opportunity.",
                llm_example_values="'c3d4e5f6-a7b8-9012-cdef-123456789012'",
            ),
            PgColumn(
                name="opp_number",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Human-readable opportunity reference number.",
                llm_example_values="'OPP-000123', 'OPP-009999'",
            ),
            PgColumn(
                name="contact_id",
                data_type="UUID",
                modifiers="NOT NULL",
                llm_description="FK to the contact driving this opportunity.",
                llm_example_values="'b2c3d4e5-f6a7-8901-bcde-f12345678901'",
            ),
            PgColumn(
                name="company",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Prospect company name, carried from the linked contact.",
                llm_example_values="'Acme Corp', 'Global Tech Solutions'",
            ),
            PgColumn(
                name="stage",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Pipeline stage. Distribution: Qualification ~28%, Discovery ~22%, Proposal ~17%, Prospecting ~8%, Negotiation ~5%, Closed Lost ~14%, Closed Won ~6%.",
                llm_example_values="'Prospecting', 'Qualification', 'Discovery', 'Proposal', 'Negotiation', 'Closed Won', 'Closed Lost'",
            ),
            PgColumn(
                name="deal_value",
                data_type="NUMERIC(18, 2)",
                modifiers="NOT NULL",
                llm_description="Estimated contract value in USD. SMB $5k-$50k (~50%), mid-market $50k-$500k (~35%), enterprise $500k-$5M+ (~15%).",
                llm_example_values="'25000.00', '180000.00', '1500000.00'",
            ),
            PgColumn(
                name="created_date",
                data_type="DATE",
                modifiers="NOT NULL",
                llm_description="Date the opportunity was created in the CRM. Must be ≥ the linked contact's creation date.",
                llm_example_values="'2024-02-10', '2024-07-15'",
            ),
            PgColumn(
                name="close_date",
                data_type="DATE",
                modifiers="NOT NULL",
                llm_description="Expected or actual close date. 30–180 days after created_date. Must be in the past for Closed Won/Lost.",
                llm_example_values="'2024-05-10', '2025-01-31'",
            ),
            PgColumn(
                name="owner_email",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Sales rep responsible for the opportunity. Must be distributed across multiple reps — no single rep should own >40% of pipeline.",
                llm_example_values="'alice.chen@company.com', 'bob.smith@company.com'",
            ),
            PgColumn(
                name="probability",
                data_type="NUMERIC(5, 2)",
                modifiers="NOT NULL",
                llm_description="Close probability (0–100). Must match stage exactly: Prospecting=5, Qualification=15, Discovery=25, Proposal=40, Negotiation=60, Closed Won=100, Closed Lost=0.",
                llm_example_values="'5.00', '25.00', '100.00', '0.00'",
            ),
        ],
    )


def generate_opportunities(
    n_samples: int,
    contact_ids: np.ndarray,
    companies: np.ndarray,
    contact_dates: pd.Series,
    end_date: str = "2025-12-31",
) -> pd.DataFrame:
    stages = np.random.choice(_STAGES, p=_STAGE_WEIGHTS, size=n_samples)
    probabilities = np.array([_STAGE_PROBABILITY[s] for s in stages])

    segments = np.random.choice(["smb", "midmarket", "enterprise"], p=_SEGMENT_WEIGHTS, size=n_samples)
    deal_values = np.where(
        segments == "enterprise",
        generate_amounts(n_samples, min_amount=500_000, max_amount=5_000_000, mu=14.0, sigma=0.7),
        np.where(
            segments == "midmarket",
            generate_amounts(n_samples, min_amount=50_000, max_amount=500_000, mu=11.5, sigma=0.7),
            generate_amounts(n_samples, min_amount=5_000, max_amount=50_000, mu=9.5, sigma=0.7),
        ),
    )

    # Opportunity opened 0–30 days after contact creation
    created_dates = extrapolate_off_dates(contact_dates, min_days=0, max_days=30)

    # Close date base: open opps use today (so close is in the future);
    # closed opps use their created_date (so close is in the past — already happened).
    is_closed = np.isin(stages, ["Closed Won", "Closed Lost"])
    today = pd.Timestamp.today().normalize()
    base_dates = created_dates.copy()
    base_dates[~is_closed] = today
    close_dates = pd.to_datetime(extrapolate_off_dates(base_dates, min_days=30, max_days=180))
    # Closed Won/Lost must never have a future close date (deal already happened)
    yesterday = today - pd.Timedelta(days=1)
    stale_closed = pd.Series(is_closed) & (close_dates > yesterday)
    close_dates = close_dates.where(~stale_closed, other=yesterday)

    return pd.DataFrame(
        {
            "opp_id": generate_n_random_uuids(n_samples),
            "opp_number": generate_serial_numbers_with_prefix(
                n_samples, prefix="OPP-", total_length=10
            ),
            "contact_id": contact_ids,
            "company": companies,
            "stage": stages,
            "deal_value": np.round(deal_values, 2),
            "created_date": created_dates,
            "close_date": close_dates,
            "owner_email": generate_user_emails(n_samples),
            "probability": probabilities,
        }
    )
