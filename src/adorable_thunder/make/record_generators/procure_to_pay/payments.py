import numpy as np
import pandas as pd

from adorable_thunder.make.common.math import round_weights_and_rebalance
from adorable_thunder.make.field_generators.amounts import generate_amounts
from adorable_thunder.make.field_generators.currency import TOP_CURRENCIES
from adorable_thunder.make.field_generators.dates import (
    extrapolate_off_dates,
    generate_random_dates,
)
from adorable_thunder.make.field_generators.identifiers import generate_n_random_uuids
from adorable_thunder.make.record_generators.schemas import CreatePgTableSql

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
        pg_columns=[
            "payment_id     UUID           PRIMARY KEY",
            "invoice_id     UUID           NOT NULL",
            "payment_date   DATE           NOT NULL",
            "amount_paid    NUMERIC(18, 2) NOT NULL",
            "currency_code  VARCHAR(3)     NOT NULL",
            "payment_method TEXT           NOT NULL",
            "status         TEXT           NOT NULL",
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
        # On-time payers cluster near due_date; late payers up to 30 days over
        payment_dates = extrapolate_off_dates(due_dates, min_days=-3, max_days=30)
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
