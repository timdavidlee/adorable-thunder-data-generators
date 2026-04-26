import numpy as np
import pandas as pd

from adorable_thunder.make.common.math import round_weights_and_rebalance
from adorable_thunder.make.field_generators.amounts import generate_amounts
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
from adorable_thunder.make.field_generators.percentage import generate_discount_rates
from adorable_thunder.make.field_generators.users import generate_user_emails
from adorable_thunder.make.record_generators.schemas import CreatePgTableSql, PgColumn

_QUOTE_STATUSES = np.array(["accepted", "pending", "expired", "rejected"])
_QUOTE_STATUS_WEIGHTS = np.array([0.50, 0.25, 0.15, 0.10])

_NON_USD = [c for c in TOP_CURRENCIES if c.code != "USD"]
_NON_USD_CODES = np.array([c.code for c in _NON_USD])
_NON_USD_CAPS = np.array([c.market_cap_trillions for c in _NON_USD])
_NON_USD_WEIGHTS = round_weights_and_rebalance(_NON_USD_CAPS / _NON_USD_CAPS.sum(), precision=4)

QUOTES_TABLE_NAME = "quotes"


def create_pg_sql_table_schema(pg_schema: str) -> CreatePgTableSql:
    return CreatePgTableSql(
        pg_schema=pg_schema,
        pg_table=QUOTES_TABLE_NAME,
        pg_columns=[
            PgColumn(name="quote_id", modifiers="UUID PRIMARY KEY"),
            PgColumn(name="quote_number", modifiers="TEXT NOT NULL"),
            PgColumn(name="quote_date", modifiers="DATE NOT NULL"),
            PgColumn(name="expiry_date", modifiers="DATE NOT NULL"),
            PgColumn(name="customer_name", modifiers="TEXT NOT NULL"),
            PgColumn(name="sales_rep_email", modifiers="TEXT NOT NULL"),
            PgColumn(name="line_item_count", modifiers="INTEGER NOT NULL"),
            PgColumn(name="amount_usd", modifiers="NUMERIC(18, 2) NOT NULL"),
            PgColumn(name="currency_code", modifiers="VARCHAR(3) NOT NULL"),
            PgColumn(name="discount_rate", modifiers="NUMERIC(6, 4) NOT NULL"),
            PgColumn(name="status", modifiers="TEXT NOT NULL"),
        ],
    )


def generate_quotes(
    n_samples: int,
    start_date: str = "2024-01-01",
    end_date: str = "2025-12-31",
) -> pd.DataFrame:
    amounts_usd = generate_amounts(
        n_samples,
        min_amount=500.0,
        max_amount=500_000.0,
        mu=9.5,
        sigma=1.8,
    )

    is_non_usd = np.random.random(n_samples) < 0.30
    currency_codes = np.where(
        is_non_usd,
        np.random.choice(_NON_USD_CODES, p=_NON_USD_WEIGHTS, size=n_samples),
        "USD",
    )

    quote_dates = generate_random_dates(start_date, end_date, n_samples)
    expiry_dates = extrapolate_off_dates(quote_dates, min_days=30, max_days=90)

    return pd.DataFrame(
        {
            "quote_id": generate_n_random_uuids(n_samples),
            "quote_number": generate_serial_numbers_with_prefix(
                n_samples, prefix="QUO-", total_length=12
            ),
            "quote_date": quote_dates,
            "expiry_date": expiry_dates,
            "customer_name": generate_company_names(n_samples),
            "sales_rep_email": generate_user_emails(n_samples),
            "line_item_count": np.random.randint(1, 11, size=n_samples),
            "amount_usd": amounts_usd,
            "currency_code": currency_codes,
            "discount_rate": generate_discount_rates(n_samples),
            "status": np.random.choice(_QUOTE_STATUSES, p=_QUOTE_STATUS_WEIGHTS, size=n_samples),
        }
    )
