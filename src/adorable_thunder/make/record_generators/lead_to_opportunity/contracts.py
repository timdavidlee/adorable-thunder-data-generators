import numpy as np
import pandas as pd

from adorable_thunder.make.field_generators.dates import extrapolate_off_dates
from adorable_thunder.make.field_generators.identifiers import (
    generate_n_random_uuids,
    generate_serial_numbers_with_prefix,
)
from adorable_thunder.make.field_generators.payment_terms import generate_payment_terms
from adorable_thunder.make.record_generators.schemas import CreatePgTableSql, PgColumn

_CONTRACT_TYPES = np.array(["MSA", "SOW", "NDA", "RESELLER_AGREEMENT", "PILOT"])
_CONTRACT_TYPE_WEIGHTS = np.array([0.35, 0.30, 0.15, 0.12, 0.08])

_CONTRACT_STATUSES = np.array(["active", "completed", "expired", "terminated"])
_CONTRACT_STATUS_WEIGHTS = np.array([0.60, 0.25, 0.10, 0.05])

CONTRACTS_TABLE_NAME = "contracts"


def create_pg_sql_table_schema(pg_schema: str) -> CreatePgTableSql:
    return CreatePgTableSql(
        pg_schema=pg_schema,
        pg_table=CONTRACTS_TABLE_NAME,
        llm_description="Executed contracts for Closed Won opportunities only. total_value should closely approximate the linked quote.total_amount (within 5%). Contract terms are typically 12–36 months.",
        pg_columns=[
            PgColumn(
                name="contract_id",
                data_type="UUID",
                modifiers="PRIMARY KEY",
                llm_description="Unique identifier for the contract.",
                llm_example_values="'e5f6a7b8-c9d0-1234-efab-345678901234'",
            ),
            PgColumn(
                name="contract_number",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Human-readable contract reference.",
                llm_example_values="'CTR-000001', 'CTR-009999'",
            ),
            PgColumn(
                name="opp_id",
                data_type="UUID",
                modifiers="NOT NULL",
                llm_description="FK to the Closed Won opportunity this contract executes.",
                llm_example_values="'c3d4e5f6-a7b8-9012-cdef-123456789012'",
            ),
            PgColumn(
                name="contract_type",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Contract form. Mix: MSA ~35%, SOW ~30%, NDA ~15%, RESELLER_AGREEMENT ~12%, PILOT ~8%.",
                llm_example_values="'MSA', 'SOW', 'NDA', 'RESELLER_AGREEMENT', 'PILOT'",
            ),
            PgColumn(
                name="start_date",
                data_type="DATE",
                modifiers="NOT NULL",
                llm_description="Contract effective date. Must be ≥ the linked quote_date.",
                llm_example_values="'2024-07-01', '2025-01-01'",
            ),
            PgColumn(
                name="end_date",
                data_type="DATE",
                modifiers="NOT NULL",
                llm_description="Contract expiry date. Typically 12–36 months after start_date.",
                llm_example_values="'2025-06-30', '2028-01-01'",
            ),
            PgColumn(
                name="total_value",
                data_type="NUMERIC(18, 2)",
                modifiers="NOT NULL",
                llm_description="Contracted total value. Should approximate quote.total_amount within 5% — large gaps are a flag.",
                llm_example_values="'22500.00', '162000.00', '1350000.00'",
            ),
            PgColumn(
                name="payment_terms",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Payment terms agreed in the contract.",
                llm_example_values="'Net 30', 'Net 60', 'Net 45'",
            ),
            PgColumn(
                name="status",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Contract lifecycle status. Mix: active ~60%, completed ~25%, expired ~10%, terminated ~5%.",
                llm_example_values="'active', 'completed', 'expired', 'terminated'",
            ),
        ],
    )


def generate_contracts(
    n_samples: int,
    opp_ids: np.ndarray,
    quote_totals: np.ndarray,
    quote_dates: pd.Series,
) -> pd.DataFrame:
    # Contract effective 0–14 days after quote date
    start_dates = extrapolate_off_dates(quote_dates, min_days=0, max_days=14)
    # Term: 12, 24, or 36 months (approximated as 365/730/1095 days)
    term_days = np.random.choice([365, 730, 1095], p=[0.40, 0.35, 0.25], size=n_samples)
    end_dates = start_dates + pd.to_timedelta(term_days, unit="D")

    # Contract value ≈ quote total ± 5%
    variance = 1 + np.random.uniform(-0.05, 0.05, size=n_samples)
    total_values = np.round(quote_totals * variance, 2)

    return pd.DataFrame(
        {
            "contract_id": generate_n_random_uuids(n_samples),
            "contract_number": generate_serial_numbers_with_prefix(
                n_samples, prefix="CTR-", total_length=10
            ),
            "opp_id": opp_ids,
            "contract_type": np.random.choice(
                _CONTRACT_TYPES, p=_CONTRACT_TYPE_WEIGHTS, size=n_samples
            ),
            "start_date": start_dates,
            "end_date": end_dates,
            "total_value": total_values,
            "payment_terms": generate_payment_terms(n_samples),
            "status": np.random.choice(
                _CONTRACT_STATUSES, p=_CONTRACT_STATUS_WEIGHTS, size=n_samples
            ),
        }
    )
