import numpy as np
import pandas as pd

from adorable_thunder.make.field_generators.amounts import generate_amounts
from adorable_thunder.make.field_generators.identifiers import generate_n_random_uuids
from adorable_thunder.make.record_generators.schemas import CreatePgTableSql

CASH_APPLICATION_TABLE_NAME = "cash_applications"


def create_pg_sql_table_schema(pg_schema: str) -> CreatePgTableSql:
    return CreatePgTableSql(
        pg_schema=pg_schema,
        pg_table=CASH_APPLICATION_TABLE_NAME,
        pg_columns=[
            "application_id UUID           PRIMARY KEY",
            "receipt_id     UUID           NOT NULL",
            "invoice_id     UUID           NOT NULL",
            "applied_amount NUMERIC(18, 2) NOT NULL",
            "open_balance   NUMERIC(18, 2) NOT NULL",
        ],
    )


def generate_cash_applications(
    n_samples: int,
    receipt_ids: np.ndarray | None = None,
    invoice_ids: np.ndarray | None = None,
    amounts_received: np.ndarray | None = None,
    invoice_totals_usd: np.ndarray | None = None,
) -> pd.DataFrame:
    if receipt_ids is None:
        receipt_ids = generate_n_random_uuids(n_samples)
    if invoice_ids is None:
        invoice_ids = generate_n_random_uuids(n_samples)

    if amounts_received is not None:
        applied_amounts = amounts_received
    else:
        applied_amounts = generate_amounts(
            n_samples,
            min_amount=500.0,
            max_amount=500_000.0,
            mu=9.5,
            sigma=1.8,
        )

    if invoice_totals_usd is not None:
        open_balances = np.round(invoice_totals_usd - applied_amounts, 2)
    else:
        open_balances = np.zeros(n_samples)

    return pd.DataFrame(
        {
            "application_id": generate_n_random_uuids(n_samples),
            "receipt_id": receipt_ids,
            "invoice_id": invoice_ids,
            "applied_amount": applied_amounts,
            "open_balance": open_balances,
        }
    )
