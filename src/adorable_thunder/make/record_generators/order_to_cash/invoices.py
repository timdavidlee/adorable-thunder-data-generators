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
from adorable_thunder.make.field_generators.percentage import generate_tax_rates
from adorable_thunder.make.record_generators.schemas import CreatePgTableSql, PgColumn

_INVOICE_STATUSES = np.array(["paid", "sent", "pending", "on_hold", "cancelled", "in_dispute"])
_INVOICE_STATUS_WEIGHTS = np.array([0.45, 0.25, 0.15, 0.08, 0.05, 0.02])


INVOICES_TABLE_NAME = "invoices"


def create_pg_sql_table_schema(pg_schema: str) -> CreatePgTableSql:
    return CreatePgTableSql(
        pg_schema=pg_schema,
        pg_table=INVOICES_TABLE_NAME,
        pg_columns=[
            PgColumn(name="invoice_id", modifiers="UUID PRIMARY KEY"),
            PgColumn(name="order_id", modifiers="UUID NOT NULL"),
            PgColumn(name="invoice_number", modifiers="TEXT NOT NULL"),
            PgColumn(name="invoice_date", modifiers="DATE NOT NULL"),
            PgColumn(name="due_date", modifiers="DATE NOT NULL"),
            PgColumn(name="currency_code", modifiers="VARCHAR(3) NOT NULL"),
            PgColumn(name="subtotal_amount", modifiers="NUMERIC(18, 2) NOT NULL"),
            PgColumn(name="tax_amount", modifiers="NUMERIC(18, 2) NOT NULL"),
            PgColumn(name="total_amount", modifiers="NUMERIC(18, 2) NOT NULL"),
            PgColumn(name="status", modifiers="TEXT NOT NULL"),
        ],
    )


def generate_invoices(
    n_samples: int,
    start_date: str = "2024-01-01",
    end_date: str = "2025-12-31",
    order_ids: np.ndarray | None = None,
    ship_dates: pd.Series | None = None,
    order_net_amounts_usd: np.ndarray | None = None,
    currency_codes: np.ndarray | None = None,
) -> pd.DataFrame:
    if order_ids is None:
        order_ids = generate_n_random_uuids(n_samples)

    if ship_dates is not None:
        # Ship → invoice: 0–5 days to process and issue
        invoice_dates = extrapolate_off_dates(ship_dates, min_days=0, max_days=5)
    else:
        invoice_dates = generate_random_dates(start_date, end_date, n_samples)

    due_dates = extrapolate_off_dates(invoice_dates, min_days=30, max_days=60)

    if order_net_amounts_usd is not None:
        # Invoice subtotal ≈ order net ±2% for minor adjustments
        variation = np.random.uniform(-0.02, 0.02, n_samples)
        subtotal_amounts = np.round(order_net_amounts_usd * (1 + variation), 2)
    else:
        subtotal_amounts = generate_amounts(
            n_samples,
            min_amount=500.0,
            max_amount=500_000.0,
            mu=9.5,
            sigma=1.8,
        )

    tax_rates = generate_tax_rates(n_samples)
    tax_amounts = np.round(subtotal_amounts * tax_rates, 2)
    total_amounts = np.round(subtotal_amounts + tax_amounts, 2)

    if currency_codes is None:
        currency_codes = np.full(n_samples, "USD")

    return pd.DataFrame(
        {
            "invoice_id": generate_n_random_uuids(n_samples),
            "order_id": order_ids,
            "invoice_number": generate_serial_numbers_with_prefix(
                n_samples, prefix="INV-", total_length=12
            ),
            "invoice_date": invoice_dates,
            "due_date": due_dates,
            "currency_code": currency_codes,
            "subtotal_amount": subtotal_amounts,
            "tax_amount": tax_amounts,
            "total_amount": total_amounts,
            "status": np.random.choice(
                _INVOICE_STATUSES, p=_INVOICE_STATUS_WEIGHTS, size=n_samples
            ),
        }
    )
