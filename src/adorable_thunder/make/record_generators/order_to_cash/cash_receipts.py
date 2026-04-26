import numpy as np
import pandas as pd

from adorable_thunder.make.field_generators.amounts import generate_amounts
from adorable_thunder.make.field_generators.dates import (
    extrapolate_off_dates,
    generate_random_dates,
)
from adorable_thunder.make.field_generators.identifiers import (
    generate_n_random_uuids,
    generate_serial_numbers_with_prefix,
)
from adorable_thunder.make.record_generators.schemas import CreatePgTableSql

_RECEIPT_STATUSES = np.array(["posted", "pending", "on_hold", "reversed"])
_RECEIPT_STATUS_WEIGHTS = np.array([0.60, 0.25, 0.10, 0.05])

_PAYMENT_METHODS = np.array(
    ["ACH", "Wire Transfer", "Check", "Credit Card", "Virtual Card"]
)
_PAYMENT_METHOD_WEIGHTS = np.array([0.35, 0.30, 0.10, 0.20, 0.05])

CASH_RECEIPTS_TABLE_NAME = "cash_applications"


def create_pg_sql_table_schema(pg_schema: str) -> CreatePgTableSql:
    return CreatePgTableSql(
        pg_schema=pg_schema,
        pg_table=CASH_RECEIPTS_TABLE_NAME,
        pg_columns=[
            "receipt_id      UUID           PRIMARY KEY",
            "invoice_id      UUID           NOT NULL",
            "receipt_number  TEXT           NOT NULL",
            "received_date   DATE           NOT NULL",
            "amount_received NUMERIC(18, 2) NOT NULL",
            "currency_code   VARCHAR(3)     NOT NULL",
            "payment_method  TEXT           NOT NULL",
            "status          TEXT           NOT NULL",
        ],
    )


def generate_cash_receipts(
    n_samples: int,
    start_date: str = "2024-01-01",
    end_date: str = "2025-12-31",
    invoice_ids: np.ndarray | None = None,
    due_dates: pd.Series | None = None,
    invoice_totals_usd: np.ndarray | None = None,
    currency_codes: np.ndarray | None = None,
) -> pd.DataFrame:
    if invoice_ids is None:
        invoice_ids = generate_n_random_uuids(n_samples)

    if due_dates is not None:
        # On-time payers cluster near due_date; late payers up to 30 days over
        received_dates = extrapolate_off_dates(due_dates, min_days=-3, max_days=30)
    else:
        received_dates = generate_random_dates(start_date, end_date, n_samples)

    if invoice_totals_usd is not None:
        # ~25% partial payments (85–99% of invoice total); rest are full
        is_partial = np.random.random(n_samples) < 0.25
        partial_rates = np.random.uniform(0.85, 0.99, n_samples)
        amounts_received = np.where(
            is_partial,
            np.round(invoice_totals_usd * partial_rates, 2),
            invoice_totals_usd,
        )
    else:
        amounts_received = generate_amounts(
            n_samples,
            min_amount=500.0,
            max_amount=500_000.0,
            mu=9.5,
            sigma=1.8,
        )

    if currency_codes is None:
        currency_codes = np.full(n_samples, "USD")

    return pd.DataFrame(
        {
            "receipt_id": generate_n_random_uuids(n_samples),
            "invoice_id": invoice_ids,
            "receipt_number": generate_serial_numbers_with_prefix(
                n_samples, prefix="RCP-", total_length=12
            ),
            "received_date": received_dates,
            "amount_received": amounts_received,
            "currency_code": currency_codes,
            "payment_method": np.random.choice(
                _PAYMENT_METHODS, p=_PAYMENT_METHOD_WEIGHTS, size=n_samples
            ),
            "status": np.random.choice(
                _RECEIPT_STATUSES, p=_RECEIPT_STATUS_WEIGHTS, size=n_samples
            ),
        }
    )
