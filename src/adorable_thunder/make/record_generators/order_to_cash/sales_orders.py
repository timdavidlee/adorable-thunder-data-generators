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
from adorable_thunder.make.field_generators.percentage import generate_discount_rates
from adorable_thunder.make.record_generators.schemas import CreatePgTableSql, PgColumn

_ORDER_STATUSES = np.array(["confirmed", "in_progress", "pending", "cancelled"])
_ORDER_STATUS_WEIGHTS = np.array([0.55, 0.20, 0.15, 0.10])

# Enterprise B2B payment terms — excludes non-standard terms (Due on Receipt, COD, Prepaid, Net 7)
_OTC_PAYMENT_TERMS = np.array(
    ["Net 30", "Net 45", "Net 60", "2/10 Net 30", "Net 15", "Net 90", "Net 120", "End of Month"]
)
_OTC_PAYMENT_TERM_WEIGHTS = np.array([0.35, 0.20, 0.15, 0.10, 0.08, 0.06, 0.04, 0.02])

_NON_USD = [c for c in TOP_CURRENCIES if c.code != "USD"]
_NON_USD_CODES = np.array([c.code for c in _NON_USD])
_NON_USD_CAPS = np.array([c.market_cap_trillions for c in _NON_USD])
_NON_USD_WEIGHTS = round_weights_and_rebalance(_NON_USD_CAPS / _NON_USD_CAPS.sum(), precision=4)

SALES_ORDER_TABLE_NAME = "sales_orders"


def create_pg_sql_table_schema(pg_schema: str) -> CreatePgTableSql:
    return CreatePgTableSql(
        pg_schema=pg_schema,
        pg_table=SALES_ORDER_TABLE_NAME,
        llm_description="Confirmed customer sales orders derived from accepted quotes. net_amount_usd = gross_amount_usd × (1 − discount_rate). Order date is quote_date + 1–5 days.",
        pg_columns=[
            PgColumn(
                name="order_id",
                data_type="UUID",
                modifiers="PRIMARY KEY",
                llm_description="Unique identifier for the sales order.",
                llm_example_values="'f6a7b8c9-d0e1-2345-fabc-456789012345'",
            ),
            PgColumn(
                name="quote_id",
                data_type="UUID",
                modifiers="NOT NULL",
                llm_description="Foreign key to the accepted quote that generated this order.",
                llm_example_values="'e5f6a7b8-c9d0-1234-efab-345678901234'",
            ),
            PgColumn(
                name="order_number",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Human-readable sales order reference number.",
                llm_example_values="'ORD-00001234', 'ORD-00009999'",
            ),
            PgColumn(
                name="order_date",
                data_type="DATE",
                modifiers="NOT NULL",
                llm_description="Date the order was confirmed. Must be ≥ quote_date and ≤ ship_date.",
                llm_example_values="'2024-02-05', '2025-03-14'",
            ),
            PgColumn(
                name="customer_name",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Legal or trading name of the buying customer.",
                llm_example_values="'Widgets Corp', 'Northstar Logistics LLC'",
            ),
            PgColumn(
                name="line_item_count",
                data_type="INTEGER",
                modifiers="NOT NULL",
                llm_description="Number of distinct line items on the order. Typically 1–10.",
                llm_example_values="'1', '4', '10'",
            ),
            PgColumn(
                name="gross_amount_usd",
                data_type="NUMERIC(18, 2)",
                modifiers="NOT NULL",
                llm_description="Pre-discount order total in USD. Should be within ±2% of linked quote amount_usd.",
                llm_example_values="'5100.00', '49200.00', '315000.00'",
            ),
            PgColumn(
                name="discount_rate",
                data_type="NUMERIC(6, 4)",
                modifiers="NOT NULL",
                llm_description="Fractional discount applied. Most orders 0–10%; volume deals 15–30%. Should match quote discount_rate.",
                llm_example_values="'0.0000', '0.0500', '0.1500', '0.2500'",
            ),
            PgColumn(
                name="net_amount_usd",
                data_type="NUMERIC(18, 2)",
                modifiers="NOT NULL",
                llm_description="Post-discount order total in USD. net_amount_usd = gross_amount_usd × (1 − discount_rate).",
                llm_example_values="'5100.00', '46740.00', '236250.00'",
            ),
            PgColumn(
                name="currency_code",
                data_type="VARCHAR(3)",
                modifiers="NOT NULL",
                llm_description="ISO 4217 currency in which the order was placed.",
                llm_example_values="'USD', 'EUR', 'GBP', 'CAD'",
            ),
            PgColumn(
                name="net_amount_local",
                data_type="NUMERIC(18, 2)",
                modifiers="NOT NULL",
                llm_description="Net order amount in the customer's local currency. Equals net_amount_usd when currency_code = 'USD'.",
                llm_example_values="'5100.00', '43200.00', '315000.00'",
            ),
            PgColumn(
                name="payment_terms",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Agreed payment terms. Net 30 ~35%, Net 45 ~20%, Net 60 ~15% per O2C brief.",
                llm_example_values="'Net 30', 'Net 45', 'Net 60', '2/10 Net 30'",
            ),
            PgColumn(
                name="status",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Order lifecycle status. Expected mix: confirmed ~55%, in_progress ~20%, pending ~15%, cancelled ~10%.",
                llm_example_values="'confirmed', 'in_progress', 'pending', 'cancelled'",
            ),
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
            "payment_terms": np.random.choice(
                _OTC_PAYMENT_TERMS, p=_OTC_PAYMENT_TERM_WEIGHTS, size=n_samples
            ),
            "status": np.random.choice(_ORDER_STATUSES, p=_ORDER_STATUS_WEIGHTS, size=n_samples),
        }
    )
