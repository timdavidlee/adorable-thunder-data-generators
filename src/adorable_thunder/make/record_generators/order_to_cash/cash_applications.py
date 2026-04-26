import numpy as np
import pandas as pd

from adorable_thunder.make.field_generators.amounts import generate_amounts
from adorable_thunder.make.field_generators.identifiers import generate_n_random_uuids
from adorable_thunder.make.record_generators.schemas import CreatePgTableSql, PgColumn

CASH_APPLICATION_TABLE_NAME = "cash_applications"


def create_pg_sql_table_schema(pg_schema: str) -> CreatePgTableSql:
    return CreatePgTableSql(
        pg_schema=pg_schema,
        pg_table=CASH_APPLICATION_TABLE_NAME,
        llm_description="Records the allocation of a cash receipt to a specific invoice. applied_amount ≤ invoice total_amount; open_balance = invoice total − applied_amount (0.00 when fully settled).",
        pg_columns=[
            PgColumn(
                name="application_id",
                data_type="UUID",
                modifiers="PRIMARY KEY",
                llm_description="Unique identifier for the cash application record.",
                llm_example_values="'d0e1f2a3-b4c5-6789-defa-890123456789'",
            ),
            PgColumn(
                name="receipt_id",
                data_type="UUID",
                modifiers="NOT NULL",
                llm_description="Foreign key to the cash receipt being applied.",
                llm_example_values="'c9d0e1f2-a3b4-5678-cdef-789012345678'",
            ),
            PgColumn(
                name="invoice_id",
                data_type="UUID",
                modifiers="NOT NULL",
                llm_description="Foreign key to the invoice the receipt is applied against.",
                llm_example_values="'b8c9d0e1-f2a3-4567-bcde-678901234567'",
            ),
            PgColumn(
                name="applied_amount",
                data_type="NUMERIC(18, 2)",
                modifiers="NOT NULL",
                llm_description="Portion of the receipt allocated to this invoice. Must be ≤ invoice total_amount and ≤ amount_received.",
                llm_example_values="'5100.00', '47000.00', '237877.50'",
            ),
            PgColumn(
                name="open_balance",
                data_type="NUMERIC(18, 2)",
                modifiers="NOT NULL",
                llm_description="Remaining unpaid balance on the invoice after this application. 0.00 when fully settled; positive when partially paid.",
                llm_example_values="'0.00', '410.00', '12500.00'",
            ),
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
