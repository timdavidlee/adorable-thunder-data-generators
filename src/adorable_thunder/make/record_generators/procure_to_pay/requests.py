import numpy as np
import pandas as pd

from adorable_thunder.make.common.math import round_weights_and_rebalance
from adorable_thunder.make.field_generators.amounts import generate_amounts
from adorable_thunder.make.field_generators.company import generate_company_names
from adorable_thunder.make.field_generators.cost_center import (
    generate_cost_center_names,
)
from adorable_thunder.make.field_generators.currency import TOP_CURRENCIES
from adorable_thunder.make.field_generators.dates import generate_random_dates
from adorable_thunder.make.field_generators.identifiers import (
    generate_n_random_uuids,
    generate_serial_numbers_with_prefix,
)
from adorable_thunder.make.field_generators.users import generate_user_emails
from adorable_thunder.make.record_generators.schemas import CreatePgTableSql, PgColumn

_REQUEST_STATUSES = np.array(["approved", "initiated", "pending", "rejected"])
_REQUEST_STATUS_WEIGHTS = np.array([0.55, 0.20, 0.15, 0.10])

_NON_USD = [c for c in TOP_CURRENCIES if c.code != "USD"]
_NON_USD_CODES = np.array([c.code for c in _NON_USD])
_NON_USD_CAPS = np.array([c.market_cap_trillions for c in _NON_USD])
_NON_USD_WEIGHTS = round_weights_and_rebalance(_NON_USD_CAPS / _NON_USD_CAPS.sum(), precision=4)


REQUESTS_TABLE_NAME = "requests"


def create_pg_sql_table_schema(pg_schema: str) -> CreatePgTableSql:
    return CreatePgTableSql(
        pg_schema=pg_schema,
        pg_table=REQUESTS_TABLE_NAME,
        pg_columns=[
            PgColumn(name="request_id", modifiers="UUID PRIMARY KEY"),
            PgColumn(name="document_number", modifiers="TEXT NOT NULL"),
            PgColumn(name="request_date", modifiers="DATE NOT NULL"),
            PgColumn(name="requester_email", modifiers="TEXT NOT NULL"),
            PgColumn(name="owner_email", modifiers="TEXT NOT NULL"),
            PgColumn(name="supplier_name", modifiers="TEXT NOT NULL"),
            PgColumn(name="amount_usd", modifiers="NUMERIC(18, 2) NOT NULL"),
            PgColumn(name="currency_code", modifiers="VARCHAR(3) NOT NULL"),
            PgColumn(name="cost_center", modifiers="TEXT NOT NULL"),
            PgColumn(name="status", modifiers="TEXT NOT NULL"),
        ],
    )


def generate_requests(
    n_samples: int,
    start_date: str = "2024-01-01",
    end_date: str = "2025-12-31",
) -> pd.DataFrame:
    amounts_usd = generate_amounts(
        n_samples,
        min_amount=1_000.0,
        max_amount=100_000.0,
        mu=10.0,
        sigma=1.5,
    )

    is_non_usd = np.random.random(n_samples) < 0.30
    currency_codes = np.where(
        is_non_usd,
        np.random.choice(_NON_USD_CODES, p=_NON_USD_WEIGHTS, size=n_samples),
        "USD",
    )

    return pd.DataFrame(
        {
            "request_id": generate_n_random_uuids(n_samples),
            "document_number": generate_serial_numbers_with_prefix(
                n_samples, prefix="REQ-", total_length=12
            ),
            "request_date": generate_random_dates(start_date, end_date, n_samples),
            "requester_email": generate_user_emails(n_samples),
            "owner_email": generate_user_emails(n_samples),
            "supplier_name": generate_company_names(n_samples),
            "amount_usd": amounts_usd,
            "currency_code": currency_codes,
            "cost_center": generate_cost_center_names(n_samples),
            "status": np.random.choice(
                _REQUEST_STATUSES, p=_REQUEST_STATUS_WEIGHTS, size=n_samples
            ),
        }
    )
