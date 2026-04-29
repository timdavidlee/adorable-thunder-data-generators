import numpy as np
import pandas as pd

from adorable_thunder.make.field_generators._random_state import get_random_state
from adorable_thunder.make.field_generators.identifiers import (
    generate_n_random_uuids,
    generate_serial_numbers_with_prefix,
)
from adorable_thunder.make.record_generators.schemas import CreatePgTableSql, PgColumn

_RENEWAL_STATUSES = np.array(["completed", "pending", "lost"])
_RENEWAL_STATUS_WEIGHTS = np.array([0.85, 0.05, 0.10])

RENEWALS_TABLE_NAME = "renewals"


def create_pg_sql_table_schema(pg_schema: str) -> CreatePgTableSql:
    return CreatePgTableSql(
        pg_schema=pg_schema,
        pg_table=RENEWALS_TABLE_NAME,
        llm_description=(
            "Renewal records for subscriptions whose end_date has passed. Only generated for "
            "non-churned subscriptions. expansion_amount = new_mrr - old_mrr; can be negative "
            "(contraction). Healthy NRR runs 100–130%."
        ),
        pg_columns=[
            PgColumn(
                name="renewal_id",
                data_type="UUID",
                modifiers="PRIMARY KEY",
                llm_description="Unique identifier for the renewal.",
                llm_example_values="'e5f6a7b8-c9d0-1234-efab-567890123456'",
            ),
            PgColumn(
                name="sub_id",
                data_type="UUID",
                modifiers="NOT NULL",
                llm_description="Foreign key to the subscription being renewed.",
                llm_example_values="'a1b2c3d4-e5f6-7890-abcd-ef1234567890'",
            ),
            PgColumn(
                name="renewal_number",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Human-readable renewal reference number.",
                llm_example_values="'REN-00001234'",
            ),
            PgColumn(
                name="renewal_date",
                data_type="DATE",
                modifiers="NOT NULL",
                llm_description=(
                    "Date of renewal; equals the subscription end_date for the prior term."
                ),
                llm_example_values="'2025-02-01', '2025-08-15'",
            ),
            PgColumn(
                name="new_term_months",
                data_type="INTEGER",
                modifiers="NOT NULL",
                llm_description="Term length of the renewed subscription in months.",
                llm_example_values="'12', '24'",
            ),
            PgColumn(
                name="prior_mrr",
                data_type="NUMERIC(18, 2)",
                modifiers="NOT NULL",
                llm_description="MRR of the subscription before the renewal.",
                llm_example_values="'500.00', '8500.00'",
            ),
            PgColumn(
                name="new_mrr",
                data_type="NUMERIC(18, 2)",
                modifiers="NOT NULL",
                llm_description=(
                    "MRR of the subscription after the renewal. Equals prior_mrr for flat "
                    "renewals; higher for expansion; lower for contraction."
                ),
                llm_example_values="'600.00', '8500.00', '7000.00'",
            ),
            PgColumn(
                name="expansion_amount",
                data_type="NUMERIC(18, 2)",
                modifiers="NOT NULL",
                llm_description=(
                    "new_mrr - prior_mrr; positive = expansion, negative = contraction."
                ),
                llm_example_values="'100.00', '0.00', '-1500.00'",
            ),
            PgColumn(
                name="status",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description=(
                    "Renewal status. Expected mix: completed ~85%, lost ~10%, pending ~5%."
                ),
                llm_example_values="'completed', 'lost', 'pending'",
            ),
        ],
    )


def generate_renewals(
    sub_ids: np.ndarray,
    sub_end_dates: pd.Series,
    sub_statuses: np.ndarray,
    auto_renew: np.ndarray,
    mrr_usd: np.ndarray,
    term_months: np.ndarray,
    dataset_end: str,
) -> pd.DataFrame:
    """Renewals for non-churned subscriptions whose end_date has passed."""
    dataset_end_ts = pd.Timestamp(dataset_end)
    ends = pd.to_datetime(sub_end_dates).reset_index(drop=True)

    not_churned = sub_statuses != "churned"
    past_end = ends.to_numpy() <= dataset_end_ts.to_numpy()
    eligible = not_churned & past_end
    eligible_idx = np.where(eligible)[0]

    if len(eligible_idx) == 0:
        return pd.DataFrame(
            columns=[
                "renewal_id",
                "sub_id",
                "renewal_number",
                "renewal_date",
                "new_term_months",
                "prior_mrr",
                "new_mrr",
                "expansion_amount",
                "status",
            ]
        )

    n = len(eligible_idx)

    # Auto-renew accounts always get a renewal record. Manual-renew accounts renew ~70% of the time.
    keeps = np.where(auto_renew[eligible_idx], True, get_random_state().random(n) < 0.70)
    keep_idx = eligible_idx[keeps]
    n = len(keep_idx)
    if n == 0:
        return pd.DataFrame(
            columns=[
                "renewal_id",
                "sub_id",
                "renewal_number",
                "renewal_date",
                "new_term_months",
                "prior_mrr",
                "new_mrr",
                "expansion_amount",
                "status",
            ]
        )

    # MRR change distribution: 60% flat, 25% expansion, 15% contraction.
    bands = get_random_state().choice([0, 1, 2], size=n, p=[0.60, 0.25, 0.15])
    multipliers = np.where(
        bands == 0,
        1.0,
        np.where(
            bands == 1,
            get_random_state().uniform(1.05, 1.40, size=n),
            get_random_state().uniform(0.70, 0.95, size=n),
        ),
    )
    prior_mrr = mrr_usd[keep_idx]
    new_mrr = np.round(prior_mrr * multipliers, 2)
    expansion = np.round(new_mrr - prior_mrr, 2)

    new_term = np.where(
        term_months[keep_idx] >= 12,
        get_random_state().choice([12, 24, 36], p=[0.65, 0.25, 0.10], size=n),
        12,
    )

    return pd.DataFrame(
        {
            "renewal_id": generate_n_random_uuids(n),
            "sub_id": sub_ids[keep_idx],
            "renewal_number": generate_serial_numbers_with_prefix(
                n, prefix="REN-", total_length=12
            ),
            "renewal_date": ends.iloc[keep_idx].reset_index(drop=True),
            "new_term_months": new_term,
            "prior_mrr": prior_mrr,
            "new_mrr": new_mrr,
            "expansion_amount": expansion,
            "status": get_random_state().choice(_RENEWAL_STATUSES, p=_RENEWAL_STATUS_WEIGHTS, size=n),
        }
    )
