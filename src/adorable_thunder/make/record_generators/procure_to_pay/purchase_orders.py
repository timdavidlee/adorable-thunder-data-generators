import numpy as np
import pandas as pd

from adorable_thunder.make.common.math import round_weights_and_rebalance
from adorable_thunder.make.field_generators.amounts import (
    generate_amounts,
    generate_local_currency_amounts,
)
from adorable_thunder.make.field_generators.company import generate_company_names
from adorable_thunder.make.field_generators.currency import TOP_CURRENCIES
from adorable_thunder.make.field_generators.dates import (
    extrapolate_off_dates,
    generate_random_dates,
)
from adorable_thunder.make.field_generators.identifiers import (
    generate_n_random_uuids,
    generate_serial_numbers_with_prefix,
)
from adorable_thunder.make.field_generators.payment_terms import generate_payment_terms
from adorable_thunder.make.record_generators.schemas import CreatePgTableSql, PgColumn

_PO_STATUSES = np.array(["approved", "pending", "draft", "rejected", "cancelled"])
_PO_STATUS_WEIGHTS = np.array([0.55, 0.25, 0.10, 0.07, 0.03])

_NON_USD = [c for c in TOP_CURRENCIES if c.code != "USD"]
_NON_USD_CODES = np.array([c.code for c in _NON_USD])
_NON_USD_CAPS = np.array([c.market_cap_trillions for c in _NON_USD])
_NON_USD_WEIGHTS = round_weights_and_rebalance(_NON_USD_CAPS / _NON_USD_CAPS.sum(), precision=4)


PURCHASE_ORDERS_TABLE_NAME = "purchase_orders"


def create_pg_sql_table_schema(pg_schema: str) -> CreatePgTableSql:
    return CreatePgTableSql(
        pg_schema=pg_schema,
        pg_table=PURCHASE_ORDERS_TABLE_NAME,
        pg_columns=[
            PgColumn(name="po_id", modifiers="UUID PRIMARY KEY"),
            PgColumn(name="request_id", modifiers="UUID NOT NULL"),
            PgColumn(name="po_number", modifiers="TEXT NOT NULL"),
            PgColumn(name="po_date", modifiers="DATE NOT NULL"),
            PgColumn(name="supplier_name", modifiers="TEXT NOT NULL"),
            PgColumn(name="line_item_count", modifiers="INTEGER NOT NULL"),
            PgColumn(name="total_amount_usd", modifiers="NUMERIC(18, 2) NOT NULL"),
            PgColumn(name="currency_code", modifiers="VARCHAR(3) NOT NULL"),
            PgColumn(name="total_amount_local", modifiers="NUMERIC(18, 2) NOT NULL"),
            PgColumn(name="payment_terms", modifiers="TEXT NOT NULL"),
            PgColumn(name="status", modifiers="TEXT NOT NULL"),
        ],
    )


def generate_purchase_orders(
    n_samples: int,
    start_date: str = "2024-01-01",
    end_date: str = "2025-12-31",
    request_ids: np.ndarray | None = None,
    request_dates: pd.Series | None = None,
) -> pd.DataFrame:
    """Generate a DataFrame of synthetic purchase order records.

    Pass request_ids/request_dates from an upstream requests stage to link POs
    to requests and enforce the date chain (po_date = request_date + 1–10 days).
    When None, placeholder UUIDs and random dates within start_date/end_date are used.
    """
    if request_ids is None:
        request_ids = generate_n_random_uuids(n_samples)

    amounts_usd = generate_amounts(
        n_samples,
        min_amount=1_000.0,
        max_amount=500_000.0,
        mu=10.0,
        sigma=1.8,
    )

    # ~30% non-USD per P2P flow brief
    is_non_usd = np.random.random(n_samples) < 0.30
    currency_codes = np.where(
        is_non_usd,
        np.random.choice(_NON_USD_CODES, p=_NON_USD_WEIGHTS, size=n_samples),
        "USD",
    )
    fx_df = generate_local_currency_amounts(amounts_usd, currency_codes)

    if request_dates is not None:
        po_dates = extrapolate_off_dates(request_dates, min_days=1, max_days=10)
    else:
        po_dates = generate_random_dates(start_date, end_date, n_samples)

    return pd.DataFrame(
        {
            "po_id": generate_n_random_uuids(n_samples),
            "request_id": request_ids,
            "po_number": generate_serial_numbers_with_prefix(
                n_samples, prefix="PO-", total_length=10
            ),
            "po_date": po_dates,
            "supplier_name": generate_company_names(n_samples),
            "line_item_count": np.random.randint(1, 11, size=n_samples),
            "total_amount_usd": fx_df["amount_usd"],
            "currency_code": fx_df["currency_code"],
            "total_amount_local": fx_df["amount_local"],
            "payment_terms": generate_payment_terms(n_samples),
            "status": np.random.choice(_PO_STATUSES, p=_PO_STATUS_WEIGHTS, size=n_samples),
        }
    )
