import numpy as np
import pandas as pd

from adorable_thunder.make.field_generators._random_state import get_random_state
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

_INVOICE_STATUSES = np.array(["paid", "received", "pending", "on_hold", "cancelled", "in_dispute"])
_INVOICE_STATUS_WEIGHTS = np.array([0.45, 0.25, 0.15, 0.08, 0.05, 0.02])

_MATCH_STATUSES = np.array(
    ["matched", "price_variance", "qty_variance", "blocked", "unmatched"]
)
# 85% clean three-way match; remainder split across realistic AP exceptions.
_MATCH_STATUS_WEIGHTS = np.array([0.85, 0.05, 0.04, 0.04, 0.02])


INVOICES_TABLE_NAME = "invoices"


def create_pg_sql_table_schema(pg_schema: str) -> CreatePgTableSql:
    return CreatePgTableSql(
        pg_schema=pg_schema,
        pg_table=INVOICES_TABLE_NAME,
        llm_description="Supplier invoices received against a PO. Invoice amount should be within ±2% of the linked PO total. Due date is invoice_date + Net 30–60 days.",
        pg_columns=[
            PgColumn(
                name="invoice_id",
                data_type="UUID",
                modifiers="PRIMARY KEY",
                llm_description="Unique identifier for the supplier invoice.",
                llm_example_values="'c3d4e5f6-a7b8-9012-cdef-123456789012'",
            ),
            PgColumn(
                name="po_id",
                data_type="UUID",
                modifiers="NOT NULL",
                llm_description="Foreign key to the purchase order this invoice is billed against.",
                llm_example_values="'b2c3d4e5-f6a7-8901-bcde-f12345678901'",
            ),
            PgColumn(
                name="invoice_number",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Supplier-assigned invoice reference number.",
                llm_example_values="'INV-00001234', 'INV-00009999'",
            ),
            PgColumn(
                name="invoice_date",
                data_type="DATE",
                modifiers="NOT NULL",
                llm_description="Date the invoice was issued. Typically 14–90 days after po_date.",
                llm_example_values="'2024-04-18', '2025-02-10'",
            ),
            PgColumn(
                name="due_date",
                data_type="DATE",
                modifiers="NOT NULL",
                llm_description="Payment due date; typically invoice_date + 30–60 days per payment terms.",
                llm_example_values="'2024-05-18', '2025-03-12'",
            ),
            PgColumn(
                name="amount_invoiced",
                data_type="NUMERIC(18, 2)",
                modifiers="NOT NULL",
                llm_description="Pre-tax invoice amount in USD. Should be within ±2% of linked PO total_amount_usd.",
                llm_example_values="'15180.00', '87650.25', '449800.00'",
            ),
            PgColumn(
                name="tax_amount",
                data_type="NUMERIC(18, 2)",
                modifiers="NOT NULL",
                llm_description="Tax charged on the invoice. Many B2B invoices are tax-exempt (0.00); others carry 5–25% VAT/GST.",
                llm_example_values="'0.00', '1518.00', '3506.01'",
            ),
            PgColumn(
                name="status",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Invoice lifecycle status. Expected mix: paid ~45%, received ~25%, pending ~15%, on_hold ~8%, cancelled ~5%, in_dispute ~2%.",
                llm_example_values="'paid', 'received', 'pending', 'on_hold', 'cancelled', 'in_dispute'",
            ),
            PgColumn(
                name="currency_code",
                data_type="VARCHAR(3)",
                modifiers="NOT NULL",
                llm_description=(
                    "ISO 4217 currency the invoice was billed in — inherited from the PO."
                ),
                llm_example_values="'USD', 'EUR', 'GBP', 'JPY'",
            ),
            PgColumn(
                name="goods_receipt_date",
                data_type="DATE",
                modifiers="NOT NULL",
                llm_description=(
                    "Date the goods or services were received (the third leg of the "
                    "three-way match). Always between po_date and invoice_date."
                ),
                llm_example_values="'2024-04-10', '2025-02-05'",
            ),
            PgColumn(
                name="match_status",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description=(
                    "Outcome of the three-way match between PO, goods receipt, and "
                    "invoice. Expected mix: matched ~85%, price_variance ~5%, "
                    "qty_variance ~4%, blocked ~4%, unmatched ~2%."
                ),
                llm_example_values=(
                    "'matched', 'price_variance', 'qty_variance', 'blocked', 'unmatched'"
                ),
            ),
        ],
    )


def generate_invoices(
    n_samples: int,
    start_date: str = "2024-01-01",
    end_date: str = "2025-12-31",
    po_ids: np.ndarray | None = None,
    po_dates: pd.Series | None = None,
    po_amounts_usd: np.ndarray | None = None,
    po_currency_codes: np.ndarray | None = None,
) -> pd.DataFrame:
    if po_ids is None:
        po_ids = generate_n_random_uuids(n_samples)

    if po_dates is not None:
        # PO → invoice: 14–90 days per P2P cycle time benchmarks
        invoice_dates = extrapolate_off_dates(po_dates, min_days=14, max_days=90)
        # Goods receipt sits between PO issue and invoice. Sample uniformly between
        # the two so the three-way-match date chain is preserved row-by-row.
        po_dates_dt = pd.to_datetime(po_dates).reset_index(drop=True)
        invoice_dates_dt = pd.to_datetime(invoice_dates).reset_index(drop=True)
        spans = (invoice_dates_dt - po_dates_dt).dt.days.clip(lower=0).to_numpy()
        offsets = (get_random_state().random(n_samples) * spans).astype(int)
        goods_receipt_dates = po_dates_dt + pd.to_timedelta(offsets, unit="D")
    else:
        invoice_dates = generate_random_dates(start_date, end_date, n_samples)
        goods_receipt_dates = invoice_dates

    due_dates = extrapolate_off_dates(invoice_dates, min_days=30, max_days=60)

    if po_currency_codes is None:
        po_currency_codes = np.full(n_samples, "USD", dtype=object)

    if po_amounts_usd is not None:
        # Invoice ≈ PO amount ±2% for minor FX/adjustment tolerance per brief
        variation = get_random_state().uniform(-0.02, 0.02, n_samples)
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
            "status": get_random_state().choice(
                _INVOICE_STATUSES, p=_INVOICE_STATUS_WEIGHTS, size=n_samples
            ),
            "currency_code": po_currency_codes,
            "goods_receipt_date": goods_receipt_dates,
            "match_status": get_random_state().choice(
                _MATCH_STATUSES, p=_MATCH_STATUS_WEIGHTS, size=n_samples
            ),
        }
    )
