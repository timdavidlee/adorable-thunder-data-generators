import numpy as np
import pandas as pd

from adorable_thunder.make.common.math import round_weights_and_rebalance
from adorable_thunder.make.field_generators.amounts import generate_amounts
from adorable_thunder.make.field_generators.currency import TOP_CURRENCIES
from adorable_thunder.make.field_generators.dates import (
    generate_random_dates,
)
from adorable_thunder.make.field_generators.identifiers import generate_n_random_uuids
from adorable_thunder.make.record_generators.schemas import CreatePgTableSql, PgColumn

_PAYMENT_STATUSES = np.array(["paid", "scheduled", "on_hold", "cancelled"])
_PAYMENT_STATUS_WEIGHTS = np.array([0.60, 0.25, 0.10, 0.05])

_PAYMENT_METHODS = np.array(["ACH", "Wire Transfer", "Check", "Credit Card", "Virtual Card"])
_PAYMENT_METHOD_WEIGHTS = np.array([0.40, 0.30, 0.15, 0.10, 0.05])

_NON_USD = [c for c in TOP_CURRENCIES if c.code != "USD"]
_NON_USD_CODES = np.array([c.code for c in _NON_USD])
_NON_USD_CAPS = np.array([c.market_cap_trillions for c in _NON_USD])
_NON_USD_WEIGHTS = round_weights_and_rebalance(_NON_USD_CAPS / _NON_USD_CAPS.sum(), precision=4)


PAYMENTS_TABLE_NAME = "payments"


def create_pg_sql_table_schema(pg_schema: str) -> CreatePgTableSql:
    return CreatePgTableSql(
        pg_schema=pg_schema,
        pg_table=PAYMENTS_TABLE_NAME,
        llm_description="Outgoing payments made to suppliers against approved invoices. Payment date clusters near invoice due_date; late payers may be up to 30 days over.",
        pg_columns=[
            PgColumn(
                name="payment_id",
                data_type="UUID",
                modifiers="PRIMARY KEY",
                llm_description="Unique identifier for the payment record.",
                llm_example_values="'d4e5f6a7-b8c9-0123-defa-234567890123'",
            ),
            PgColumn(
                name="invoice_id",
                data_type="UUID",
                modifiers="NOT NULL",
                llm_description="Foreign key to the invoice being settled by this payment.",
                llm_example_values="'c3d4e5f6-a7b8-9012-cdef-123456789012'",
            ),
            PgColumn(
                name="payment_date",
                data_type="DATE",
                modifiers="NOT NULL",
                llm_description="Date payment was disbursed. On-time payers: within 3 days of due_date; late: up to 30 days after.",
                llm_example_values="'2024-05-19', '2025-03-25'",
            ),
            PgColumn(
                name="amount_paid",
                data_type="NUMERIC(18, 2)",
                modifiers="NOT NULL",
                llm_description="Amount disbursed in USD. Should equal amount_invoiced for full payments.",
                llm_example_values="'15180.00', '87650.25', '449800.00'",
            ),
            PgColumn(
                name="currency_code",
                data_type="VARCHAR(3)",
                modifiers="NOT NULL",
                llm_description="ISO 4217 currency in which payment was made.",
                llm_example_values="'USD', 'EUR', 'GBP'",
            ),
            PgColumn(
                name="payment_method",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Disbursement method. ACH ~40%, Wire Transfer ~30%, Check ~15%, Credit Card ~10%, Virtual Card ~5%.",
                llm_example_values="'ACH', 'Wire Transfer', 'Check', 'Credit Card', 'Virtual Card'",
            ),
            PgColumn(
                name="status",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Payment lifecycle status. Expected mix: paid ~60%, scheduled ~25%, on_hold ~10%, cancelled ~5%.",
                llm_example_values="'paid', 'scheduled', 'on_hold', 'cancelled'",
            ),
        ],
    )


def generate_payments(
    n_samples: int,
    start_date: str = "2024-01-01",
    end_date: str = "2025-12-31",
    invoice_ids: np.ndarray | None = None,
    due_dates: pd.Series | None = None,
    invoice_amounts_usd: np.ndarray | None = None,
    currency_codes: np.ndarray | None = None,
) -> pd.DataFrame:
    if invoice_ids is None:
        invoice_ids = generate_n_random_uuids(n_samples)

    if due_dates is not None:
        # 85% on-time (within ±3 days of due_date), 15% late (+4 to +30 days)
        n = len(due_dates)
        late_mask = np.random.random(n) < 0.15
        on_time_days = np.random.randint(-3, 4, size=n)
        late_days = np.random.randint(4, 31, size=n)
        random_days = np.where(late_mask, late_days, on_time_days)
        payment_dates = due_dates + pd.to_timedelta(random_days, unit="D")
    else:
        payment_dates = generate_random_dates(start_date, end_date, n_samples)

    if invoice_amounts_usd is not None:
        amounts_paid = invoice_amounts_usd
    else:
        amounts_paid = generate_amounts(
            n_samples,
            min_amount=1_000.0,
            max_amount=500_000.0,
            mu=10.0,
            sigma=1.8,
        )

    if currency_codes is None:
        is_non_usd = np.random.random(n_samples) < 0.30
        currency_codes = np.where(
            is_non_usd,
            np.random.choice(_NON_USD_CODES, p=_NON_USD_WEIGHTS, size=n_samples),
            "USD",
        )

    return pd.DataFrame(
        {
            "payment_id": generate_n_random_uuids(n_samples),
            "invoice_id": invoice_ids,
            "payment_date": payment_dates,
            "amount_paid": amounts_paid,
            "currency_code": currency_codes,
            "payment_method": np.random.choice(
                _PAYMENT_METHODS, p=_PAYMENT_METHOD_WEIGHTS, size=n_samples
            ),
            "status": np.random.choice(
                _PAYMENT_STATUSES, p=_PAYMENT_STATUS_WEIGHTS, size=n_samples
            ),
        }
    )
