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
from adorable_thunder.make.field_generators.percentage import generate_discount_rates
from adorable_thunder.make.record_generators.schemas import CreatePgTableSql

_ORDER_STATUSES = np.array(["confirmed", "in_progress", "pending", "cancelled"])
_ORDER_STATUS_WEIGHTS = np.array([0.55, 0.20, 0.15, 0.10])

_NON_USD = [c for c in TOP_CURRENCIES if c.code != "USD"]
_NON_USD_CODES = np.array([c.code for c in _NON_USD])
_NON_USD_CAPS = np.array([c.market_cap_trillions for c in _NON_USD])
_NON_USD_WEIGHTS = round_weights_and_rebalance(_NON_USD_CAPS / _NON_USD_CAPS.sum(), precision=4)

SALES_ORDER_TABLE_NAME = "sales_orders"


def create_pg_sql_table_schema(pg_schema: str) -> CreatePgTableSql:
    return CreatePgTableSql(
        pg_schema=pg_schema,
        pg_table=SALES_ORDER_TABLE_NAME,
        pg_columns=[
            "order_id         UUID           PRIMARY KEY",
            "quote_id         UUID           NOT NULL",
            "order_number     TEXT           NOT NULL",
            "order_date       DATE           NOT NULL",
            "customer_name    TEXT           NOT NULL",
            "line_item_count  INTEGER        NOT NULL",
            "gross_amount_usd NUMERIC(18, 2) NOT NULL",
            "discount_rate    NUMERIC(6, 4)  NOT NULL",
            "net_amount_usd   NUMERIC(18, 2) NOT NULL",
            "currency_code    VARCHAR(3)     NOT NULL",
            "net_amount_local NUMERIC(18, 2) NOT NULL",
            "payment_terms    TEXT           NOT NULL",
            "status           TEXT           NOT NULL",
        ],
    )


def generate_sales_orders(
    n_samples: int,
    start_date: str = "2024-01-01",
    end_date: str = "2025-12-31",
    quote_ids: np.ndarray | None = None,
    quote_dates: pd.Series | None = None,
    quote_amounts_usd: np.ndarray | None = None,
    quote_discount_rates: np.ndarray | None = None,
    quote_currency_codes: np.ndarray | None = None,
) -> pd.DataFrame:
    """Generate sales order records.

    Pass quote_* args to link orders to quotes and enforce the date chain
    (order_date = quote_date + 1–5 days) and inherit amounts/currency.
    When None, placeholders and independent values are used.
    """
    if quote_ids is None:
        quote_ids = generate_n_random_uuids(n_samples)

    if quote_dates is not None:
        order_dates = extrapolate_off_dates(quote_dates, min_days=1, max_days=5)
    else:
        order_dates = generate_random_dates(start_date, end_date, n_samples)

    if quote_amounts_usd is not None:
        variation = np.random.uniform(-0.02, 0.02, n_samples)
        gross_amounts_usd = np.round(quote_amounts_usd * (1 + variation), 2)
    else:
        gross_amounts_usd = generate_amounts(
            n_samples,
            min_amount=500.0,
            max_amount=500_000.0,
            mu=9.5,
            sigma=1.8,
        )

    discount_rates = (
        quote_discount_rates
        if quote_discount_rates is not None
        else generate_discount_rates(n_samples)
    )
    net_amounts_usd = np.round(gross_amounts_usd * (1 - discount_rates), 2)

    if quote_currency_codes is not None:
        currency_codes = quote_currency_codes
    else:
        is_non_usd = np.random.random(n_samples) < 0.30
        currency_codes = np.where(
            is_non_usd,
            np.random.choice(_NON_USD_CODES, p=_NON_USD_WEIGHTS, size=n_samples),
            "USD",
        )

    fx_df = generate_local_currency_amounts(net_amounts_usd, currency_codes)

    return pd.DataFrame(
        {
            "order_id": generate_n_random_uuids(n_samples),
            "quote_id": quote_ids,
            "order_number": generate_serial_numbers_with_prefix(
                n_samples, prefix="ORD-", total_length=12
            ),
            "order_date": order_dates,
            "customer_name": generate_company_names(n_samples),
            "line_item_count": np.random.randint(1, 11, size=n_samples),
            "gross_amount_usd": gross_amounts_usd,
            "discount_rate": discount_rates,
            "net_amount_usd": net_amounts_usd,
            "currency_code": fx_df["currency_code"],
            "net_amount_local": fx_df["amount_local"],
            "payment_terms": generate_payment_terms(n_samples),
            "status": np.random.choice(_ORDER_STATUSES, p=_ORDER_STATUS_WEIGHTS, size=n_samples),
        }
    )
