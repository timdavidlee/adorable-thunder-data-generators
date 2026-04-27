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
        llm_description="Formal purchase orders issued to suppliers after a request is approved. PO date must be ≥ its linked request_date. Amounts can exceed request amounts for enterprise-tier orders.",
        pg_columns=[
            PgColumn(
                name="po_id",
                data_type="UUID",
                modifiers="PRIMARY KEY",
                llm_description="Unique identifier for the purchase order.",
                llm_example_values="'b2c3d4e5-f6a7-8901-bcde-f12345678901'",
            ),
            PgColumn(
                name="request_id",
                data_type="UUID",
                modifiers="NOT NULL",
                llm_description="Foreign key to the originating purchase request.",
                llm_example_values="'a1b2c3d4-e5f6-7890-abcd-ef1234567890'",
            ),
            PgColumn(
                name="po_number",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Human-readable PO reference number assigned sequentially.",
                llm_example_values="'PO-00001234', 'PO-00009999'",
            ),
            PgColumn(
                name="po_date",
                data_type="DATE",
                modifiers="NOT NULL",
                llm_description="Date the PO was issued. Must be ≥ request_date and ≤ invoice_date.",
                llm_example_values="'2024-03-20', '2025-01-15'",
            ),
            PgColumn(
                name="supplier_name",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Legal or trading name of the vendor the PO is addressed to.",
                llm_example_values="'Acme Supplies Ltd', 'Global Tech Solutions Inc'",
            ),
            PgColumn(
                name="line_item_count",
                data_type="INTEGER",
                modifiers="NOT NULL",
                llm_description="Number of distinct line items on the PO. Typically 1–10.",
                llm_example_values="'1', '3', '7', '10'",
            ),
            PgColumn(
                name="total_amount_usd",
                data_type="NUMERIC(18, 2)",
                modifiers="NOT NULL",
                llm_description="PO total converted to USD. Range $1k–$500k; enterprise POs can exceed $500k.",
                llm_example_values="'15000.00', '87320.50', '450000.00'",
            ),
            PgColumn(
                name="currency_code",
                data_type="VARCHAR(3)",
                modifiers="NOT NULL",
                llm_description="ISO 4217 currency of the PO. ~70% USD; ~30% non-USD per P2P brief.",
                llm_example_values="'USD', 'EUR', 'GBP', 'JPY'",
            ),
            PgColumn(
                name="total_amount_local",
                data_type="NUMERIC(18, 2)",
                modifiers="NOT NULL",
                llm_description="PO total in the supplier's local currency. Equals total_amount_usd when currency_code = 'USD'.",
                llm_example_values="'13800.00', '80124.50', '450000.00'",
            ),
            PgColumn(
                name="payment_terms",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Agreed payment terms between buyer and supplier.",
                llm_example_values="'Net 30', 'Net 60', 'Net 45', '2/10 Net 30'",
            ),
            PgColumn(
                name="status",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="PO lifecycle status. Expected mix: approved ~55%, pending ~25%, draft ~10%, rejected ~7%, cancelled ~3%.",
                llm_example_values="'approved', 'pending', 'draft', 'rejected', 'cancelled'",
            ),
        ],
    )


def generate_purchase_orders(
    n_samples: int,
    start_date: str = "2024-01-01",
    end_date: str = "2025-12-31",
    request_ids: np.ndarray | None = None,
    request_dates: pd.Series | None = None,
    supplier_names: np.ndarray | None = None,
) -> pd.DataFrame:
    """Generate a DataFrame of synthetic purchase order records.

    Pass request_ids/request_dates from an upstream requests stage to link POs
    to requests and enforce the date chain (po_date = request_date + 1–10 days).
    Pass supplier_names to carry the requested supplier through to the PO.
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
            "supplier_name": supplier_names
            if supplier_names is not None
            else generate_company_names(n_samples),
            "line_item_count": np.random.choice(
                np.arange(1, 11),
                p=[0.30, 0.25, 0.18, 0.12, 0.07, 0.04, 0.02, 0.01, 0.005, 0.005],
                size=n_samples,
            ),
            "total_amount_usd": fx_df["amount_usd"],
            "currency_code": fx_df["currency_code"],
            "total_amount_local": fx_df["amount_local"],
            "payment_terms": generate_payment_terms(n_samples),
            "status": np.random.choice(_PO_STATUSES, p=_PO_STATUS_WEIGHTS, size=n_samples),
        }
    )
