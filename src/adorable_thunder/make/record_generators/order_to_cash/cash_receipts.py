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
from adorable_thunder.make.record_generators.schemas import CreatePgTableSql, PgColumn

_RECEIPT_STATUSES = np.array(["posted", "pending", "on_hold", "reversed"])
_RECEIPT_STATUS_WEIGHTS = np.array([0.60, 0.25, 0.10, 0.05])

_PAYMENT_METHODS = np.array(["ACH", "Wire Transfer", "Check", "Credit Card", "Virtual Card"])
_PAYMENT_METHOD_WEIGHTS = np.array([0.35, 0.30, 0.10, 0.20, 0.05])

CASH_RECEIPTS_TABLE_NAME = "cash_receipts"


def create_pg_sql_table_schema(pg_schema: str) -> CreatePgTableSql:
    return CreatePgTableSql(
        pg_schema=pg_schema,
        pg_table=CASH_RECEIPTS_TABLE_NAME,
        llm_description="Incoming cash payments received from customers against outstanding invoices. ~25% are partial payments (85–99% of invoice total). received_date clusters near invoice due_date.",
        pg_columns=[
            PgColumn(
                name="receipt_id",
                data_type="UUID",
                modifiers="PRIMARY KEY",
                llm_description="Unique identifier for the cash receipt.",
                llm_example_values="'c9d0e1f2-a3b4-5678-cdef-789012345678'",
            ),
            PgColumn(
                name="invoice_id",
                data_type="UUID",
                modifiers="NOT NULL",
                llm_description="Foreign key to the invoice being paid by this receipt.",
                llm_example_values="'b8c9d0e1-f2a3-4567-bcde-678901234567'",
            ),
            PgColumn(
                name="receipt_number",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Human-readable cash receipt reference number.",
                llm_example_values="'RCP-00001234', 'RCP-00009999'",
            ),
            PgColumn(
                name="received_date",
                data_type="DATE",
                modifiers="NOT NULL",
                llm_description="Date cash was received. On-time: within 3 days of due_date; late: up to 30 days after.",
                llm_example_values="'2024-03-14', '2025-04-28'",
            ),
            PgColumn(
                name="amount_received",
                data_type="NUMERIC(18, 2)",
                modifiers="NOT NULL",
                llm_description="Amount received. Full payment = invoice total_amount; partial payments are 85–99% of that.",
                llm_example_values="'5100.00', '47000.00', '237877.50'",
            ),
            PgColumn(
                name="currency_code",
                data_type="VARCHAR(3)",
                modifiers="NOT NULL",
                llm_description="ISO 4217 currency in which payment was received.",
                llm_example_values="'USD', 'EUR', 'GBP'",
            ),
            PgColumn(
                name="payment_method",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Method used by customer to remit payment. ACH ~35%, Wire ~30%, Credit Card ~20%, Check ~10%, Virtual Card ~5%.",
                llm_example_values="'ACH', 'Wire Transfer', 'Credit Card', 'Check', 'Virtual Card'",
            ),
            PgColumn(
                name="status",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Receipt processing status. Expected mix: posted ~60%, pending ~25%, on_hold ~10%, reversed ~5%.",
                llm_example_values="'posted', 'pending', 'on_hold', 'reversed'",
            ),
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
