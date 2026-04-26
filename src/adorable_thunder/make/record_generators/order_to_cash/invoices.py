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
        llm_description="Customer-facing invoices raised after shipment. subtotal_amount ≈ order net_amount ±2%; total_amount = subtotal + tax. Due date is invoice_date + 30–60 days.",
        pg_columns=[
            PgColumn(
                name="invoice_id",
                data_type="UUID",
                modifiers="PRIMARY KEY",
                llm_description="Unique identifier for the customer invoice.",
                llm_example_values="'b8c9d0e1-f2a3-4567-bcde-678901234567'",
            ),
            PgColumn(
                name="order_id",
                data_type="UUID",
                modifiers="NOT NULL",
                llm_description="Foreign key to the sales order being invoiced.",
                llm_example_values="'f6a7b8c9-d0e1-2345-fabc-456789012345'",
            ),
            PgColumn(
                name="invoice_number",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Seller-assigned invoice reference number.",
                llm_example_values="'INV-00001234', 'INV-00009999'",
            ),
            PgColumn(
                name="invoice_date",
                data_type="DATE",
                modifiers="NOT NULL",
                llm_description="Date the invoice was issued; 0–5 days after ship_date.",
                llm_example_values="'2024-02-12', '2025-03-22'",
            ),
            PgColumn(
                name="due_date",
                data_type="DATE",
                modifiers="NOT NULL",
                llm_description="Payment due date; invoice_date + 30–60 days per payment terms.",
                llm_example_values="'2024-03-12', '2025-04-21'",
            ),
            PgColumn(
                name="currency_code",
                data_type="VARCHAR(3)",
                modifiers="NOT NULL",
                llm_description="ISO 4217 currency in which the invoice is denominated.",
                llm_example_values="'USD', 'EUR', 'GBP', 'CAD'",
            ),
            PgColumn(
                name="subtotal_amount",
                data_type="NUMERIC(18, 2)",
                modifiers="NOT NULL",
                llm_description="Pre-tax invoice amount. Should be within ±2% of order net_amount_usd.",
                llm_example_values="'5100.00', '46900.00', '236000.00'",
            ),
            PgColumn(
                name="tax_amount",
                data_type="NUMERIC(18, 2)",
                modifiers="NOT NULL",
                llm_description="Tax levied on the invoice. Many B2B transactions are tax-exempt (0.00); others carry 5–25% VAT/GST.",
                llm_example_values="'0.00', '510.00', '1877.50'",
            ),
            PgColumn(
                name="total_amount",
                data_type="NUMERIC(18, 2)",
                modifiers="NOT NULL",
                llm_description="Total amount due including tax. total_amount = subtotal_amount + tax_amount.",
                llm_example_values="'5100.00', '47410.00', '237877.50'",
            ),
            PgColumn(
                name="status",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Invoice lifecycle status. Expected mix: paid ~45%, sent ~25%, pending ~15%, on_hold ~8%, cancelled ~5%, in_dispute ~2%.",
                llm_example_values="'paid', 'sent', 'pending', 'on_hold', 'cancelled', 'in_dispute'",
            ),
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
