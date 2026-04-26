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
from adorable_thunder.make.record_generators.schemas import CreatePgTableSql

_INVOICE_STATUSES = np.array(["paid", "received", "pending", "on_hold", "cancelled", "in_dispute"])
_INVOICE_STATUS_WEIGHTS = np.array([0.45, 0.25, 0.15, 0.08, 0.05, 0.02])


INVOICES_TABLE_NAME = "invoices"


def create_pg_sql_table_schema(pg_schema: str) -> CreatePgTableSql:
    return CreatePgTableSql(
        pg_schema=pg_schema,
        pg_table=INVOICES_TABLE_NAME,
        pg_columns=[
            "invoice_id      UUID           PRIMARY KEY",
            "po_id           UUID           NOT NULL",
            "invoice_number  TEXT           NOT NULL",
            "invoice_date    DATE           NOT NULL",
            "due_date        DATE           NOT NULL",
            "amount_invoiced NUMERIC(18, 2) NOT NULL",
            "tax_amount      NUMERIC(18, 2) NOT NULL",
            "status          TEXT           NOT NULL",
        ],
    )


def generate_invoices(
    n_samples: int,
    start_date: str = "2024-01-01",
    end_date: str = "2025-12-31",
    po_ids: np.ndarray | None = None,
    po_dates: pd.Series | None = None,
    po_amounts_usd: np.ndarray | None = None,
) -> pd.DataFrame:
    if po_ids is None:
        po_ids = generate_n_random_uuids(n_samples)

    if po_dates is not None:
        # PO → invoice: 14–90 days per P2P cycle time benchmarks
        invoice_dates = extrapolate_off_dates(po_dates, min_days=14, max_days=90)
    else:
        invoice_dates = generate_random_dates(start_date, end_date, n_samples)

    due_dates = extrapolate_off_dates(invoice_dates, min_days=30, max_days=60)

    if po_amounts_usd is not None:
        # Invoice ≈ PO amount ±2% for minor FX/adjustment tolerance per brief
        variation = np.random.uniform(-0.02, 0.02, n_samples)
        amounts_invoiced = np.round(po_amounts_usd * (1 + variation), 2)
    else:
        amounts_invoiced = generate_amounts(
            n_samples,
            min_amount=1_000.0,
            max_amount=500_000.0,
            mu=10.0,
            sigma=1.8,
        )

    tax_rates = generate_tax_rates(n_samples)
    tax_amounts = np.round(amounts_invoiced * tax_rates, 2)

    return pd.DataFrame(
        {
            "invoice_id": generate_n_random_uuids(n_samples),
            "po_id": po_ids,
            "invoice_number": generate_serial_numbers_with_prefix(
                n_samples, prefix="INV-", total_length=12
            ),
            "invoice_date": invoice_dates,
            "due_date": due_dates,
            "amount_invoiced": amounts_invoiced,
            "tax_amount": tax_amounts,
            "status": np.random.choice(
                _INVOICE_STATUSES, p=_INVOICE_STATUS_WEIGHTS, size=n_samples
            ),
        }
    )
