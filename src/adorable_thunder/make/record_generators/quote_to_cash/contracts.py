import numpy as np
import pandas as pd

from adorable_thunder.make.field_generators.identifiers import (
    generate_n_random_uuids,
    generate_serial_numbers_with_prefix,
)
from adorable_thunder.make.field_generators.payment_terms import generate_payment_terms
from adorable_thunder.make.record_generators.schemas import CreatePgTableSql, PgColumn

CONTRACTS_TABLE_NAME = "contracts"


def create_pg_sql_table_schema(pg_schema: str) -> CreatePgTableSql:
    return CreatePgTableSql(
        pg_schema=pg_schema,
        pg_table=CONTRACTS_TABLE_NAME,
        llm_description=(
            "Signed contracts that govern each subscription. signed_date is 0–14 days before the "
            "subscription start_date. total_value = mrr_usd × term_months."
        ),
        pg_columns=[
            PgColumn(
                name="contract_id",
                data_type="UUID",
                modifiers="PRIMARY KEY",
                llm_description="Unique identifier for the contract.",
                llm_example_values="'b2c3d4e5-f6a7-8901-bcde-f23456789012'",
            ),
            PgColumn(
                name="sub_id",
                data_type="UUID",
                modifiers="NOT NULL",
                llm_description="Foreign key to the subscription this contract covers.",
                llm_example_values="'a1b2c3d4-e5f6-7890-abcd-ef1234567890'",
            ),
            PgColumn(
                name="contract_number",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Human-readable contract reference number.",
                llm_example_values="'CON-00001234', 'CON-00009999'",
            ),
            PgColumn(
                name="signed_date",
                data_type="DATE",
                modifiers="NOT NULL",
                llm_description=(
                    "Date the contract was signed; 0–14 days before subscription start_date."
                ),
                llm_example_values="'2024-01-25', '2025-03-05'",
            ),
            PgColumn(
                name="term_months",
                data_type="INTEGER",
                modifiers="NOT NULL",
                llm_description=(
                    "Length of the contract term in months. Monthly subs are 12; "
                    "annual subs are 12, 24, or 36."
                ),
                llm_example_values="'12', '24', '36'",
            ),
            PgColumn(
                name="total_value",
                data_type="NUMERIC(18, 2)",
                modifiers="NOT NULL",
                llm_description="Total contract value = mrr_usd × term_months.",
                llm_example_values="'1188.00', '24000.00', '420000.00'",
            ),
            PgColumn(
                name="payment_terms",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Payment terms agreed in the contract.",
                llm_example_values="'Net 30', 'Net 45', '2/10 Net 30'",
            ),
            PgColumn(
                name="auto_renew",
                data_type="BOOLEAN",
                modifiers="NOT NULL",
                llm_description="Whether the contract auto-renews at end of term.",
                llm_example_values="'true', 'false'",
            ),
            PgColumn(
                name="status",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description=(
                    "Contract lifecycle status. Expected mix: active ~70%, expired ~20%, "
                    "terminated ~10%."
                ),
                llm_example_values="'active', 'expired', 'terminated'",
            ),
        ],
    )


def generate_contracts(
    n_samples: int,
    sub_ids: np.ndarray,
    sub_start_dates: pd.Series,
    term_months: np.ndarray,
    mrr_usd: np.ndarray,
    auto_renew: np.ndarray,
    sub_statuses: np.ndarray,
) -> pd.DataFrame:
    sign_offsets = np.random.randint(0, 15, size=n_samples)
    signed_dates = pd.Series(sub_start_dates - pd.to_timedelta(sign_offsets, unit="D"))

    total_values = np.round(mrr_usd * term_months, 2)
    payment_terms = generate_payment_terms(n_samples)

    # Map subscription status → contract status. Churned subs → terminated contracts.
    contract_status = np.where(
        sub_statuses == "churned",
        "terminated",
        np.where(sub_statuses == "paused", "active", "active"),
    )

    return pd.DataFrame(
        {
            "contract_id": generate_n_random_uuids(n_samples),
            "sub_id": sub_ids,
            "contract_number": generate_serial_numbers_with_prefix(
                n_samples, prefix="CON-", total_length=12
            ),
            "signed_date": signed_dates,
            "term_months": term_months,
            "total_value": total_values,
            "payment_terms": payment_terms,
            "auto_renew": auto_renew,
            "status": contract_status,
        }
    )
