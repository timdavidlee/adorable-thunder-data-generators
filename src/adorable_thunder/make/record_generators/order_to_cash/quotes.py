import numpy as np
import pandas as pd

from adorable_thunder.make.field_generators._random_state import get_random_state
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
        llm_description="Sales quotes sent to prospective customers. A quote that is accepted becomes a Sales Order. Quotes expire 30–90 days after issue.",
        pg_columns=[
            PgColumn(
                name="quote_id",
                data_type="UUID",
                modifiers="PRIMARY KEY",
                llm_description="Unique identifier for the quote.",
                llm_example_values="'e5f6a7b8-c9d0-1234-efab-345678901234'",
            ),
            PgColumn(
                name="quote_number",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Human-readable quote reference number.",
                llm_example_values="'QUO-00001234', 'QUO-00009999'",
            ),
            PgColumn(
                name="quote_date",
                data_type="DATE",
                modifiers="NOT NULL",
                llm_description="Date the quote was issued to the customer. Must be ≤ expiry_date and ≤ order_date of any linked sales order.",
                llm_example_values="'2024-02-01', '2025-03-10'",
            ),
            PgColumn(
                name="expiry_date",
                data_type="DATE",
                modifiers="NOT NULL",
                llm_description="Date after which the quoted prices are no longer valid. Typically quote_date + 30–90 days.",
                llm_example_values="'2024-03-01', '2025-06-08'",
            ),
            PgColumn(
                name="customer_name",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Legal or trading name of the prospective customer.",
                llm_example_values="'Widgets Corp', 'Northstar Logistics LLC'",
            ),
            PgColumn(
                name="sales_rep_email",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Corporate email of the sales representative who issued the quote.",
                llm_example_values="'alice.jones@acme.com', 'bob.smith@acme.com'",
            ),
            PgColumn(
                name="line_item_count",
                data_type="INTEGER",
                modifiers="NOT NULL",
                llm_description="Number of distinct product or service lines on the quote. Typically 1–10.",
                llm_example_values="'1', '4', '10'",
            ),
            PgColumn(
                name="amount_usd",
                data_type="NUMERIC(18, 2)",
                modifiers="NOT NULL",
                llm_description="Pre-discount quote total in USD. B2B range $500–$500k; lognormal peak ~$10k.",
                llm_example_values="'5000.00', '48750.00', '312000.00'",
            ),
            PgColumn(
                name="currency_code",
                data_type="VARCHAR(3)",
                modifiers="NOT NULL",
                llm_description="ISO 4217 currency of the quote. ~70% USD; ~30% non-USD.",
                llm_example_values="'USD', 'EUR', 'GBP', 'CAD'",
            ),
            PgColumn(
                name="discount_rate",
                data_type="NUMERIC(6, 4)",
                modifiers="NOT NULL",
                llm_description="Fractional discount applied to the quote total. Most orders 0–10%; large-volume deals 15–30%.",
                llm_example_values="'0.0000', '0.0500', '0.1500', '0.2500'",
            ),
            PgColumn(
                name="status",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Quote lifecycle status. Expected mix: accepted ~50%, pending ~25%, expired ~15%, rejected ~10%.",
                llm_example_values="'accepted', 'pending', 'expired', 'rejected'",
            ),
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

    is_non_usd = get_random_state().random(n_samples) < 0.30
    currency_codes = np.where(
        is_non_usd,
        get_random_state().choice(_NON_USD_CODES, p=_NON_USD_WEIGHTS, size=n_samples),
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
            "line_item_count": get_random_state().randint(1, 11, size=n_samples),
            "amount_usd": amounts_usd,
            "currency_code": currency_codes,
            "discount_rate": generate_discount_rates(n_samples),
            "status": get_random_state().choice(_QUOTE_STATUSES, p=_QUOTE_STATUS_WEIGHTS, size=n_samples),
        }
    )
