import numpy as np
import pandas as pd

from adorable_thunder.make.field_generators.dates import generate_random_dates
from adorable_thunder.make.field_generators.identifiers import (
    generate_n_random_uuids,
    generate_serial_numbers_with_prefix,
)
from adorable_thunder.make.record_generators.schemas import CreatePgTableSql, PgColumn

_RECEIPT_STATUSES = np.array(["posted", "pending", "on_hold", "reversed"])
_RECEIPT_STATUS_WEIGHTS = np.array([0.60, 0.25, 0.10, 0.05])

_PAYMENT_METHODS = np.array(["ACH", "Wire Transfer", "Check", "Credit Card", "Virtual Card"])
_PAYMENT_METHOD_WEIGHTS = np.array([0.35, 0.30, 0.10, 0.20, 0.05])

CASH_RECEIPTS_TABLE_NAME = "cash_receipts"


def create_pg_sql_table_schema(pg_schema: str) -> CreatePgTableSql:
    return CreatePgTableSql(
        pg_schema=pg_schema,
        pg_table=CASH_RECEIPTS_TABLE_NAME,
        llm_description="Incoming cash payments received from customers against outstanding invoices. ~20-25% of invoices are closed by two receipts (first partial at 85-99%, second for remainder). received_date clusters near invoice due_date: ~60% within ±3 days, ~25% 1-14 days late, ~15% >14 days late.",
        pg_columns=[
            PgColumn(
                name="receipt_id",
                data_type="UUID",
                modifiers="PRIMARY KEY",
                llm_description="Unique identifier for the cash receipt.",
                llm_example_values="'c9d0e1f2-a3b4-5678-cdef-789012345678'",
            ),
            PgColumn(
                name="invoice_id",
                data_type="UUID",
                modifiers="NOT NULL",
                llm_description="Foreign key to the invoice being paid by this receipt.",
                llm_example_values="'b8c9d0e1-f2a3-4567-bcde-678901234567'",
            ),
            PgColumn(
                name="receipt_number",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Human-readable cash receipt reference number.",
                llm_example_values="'RCP-00001234', 'RCP-00009999'",
            ),
            PgColumn(
                name="received_date",
                data_type="DATE",
                modifiers="NOT NULL",
                llm_description="Date cash was received. ~60% within ±3 days of due_date; ~25% 1-14 days late; ~15% 15-30 days late.",
                llm_example_values="'2024-03-14', '2025-04-28'",
            ),
            PgColumn(
                name="amount_received",
                data_type="NUMERIC(18, 2)",
                modifiers="NOT NULL",
                llm_description="Amount received. Full payment = invoice total_amount; first partial receipt is 85-99% of that; second partial receipt covers the remainder.",
                llm_example_values="'5100.00', '47000.00', '237877.50'",
            ),
            PgColumn(
                name="currency_code",
                data_type="VARCHAR(3)",
                modifiers="NOT NULL",
                llm_description="ISO 4217 currency in which payment was received.",
                llm_example_values="'USD', 'EUR', 'GBP'",
            ),
            PgColumn(
                name="payment_method",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Method used by customer to remit payment. ACH ~35%, Wire ~30%, Credit Card ~20%, Check ~10%, Virtual Card ~5%.",
                llm_example_values="'ACH', 'Wire Transfer', 'Credit Card', 'Check', 'Virtual Card'",
            ),
            PgColumn(
                name="status",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Receipt processing status. Expected mix: posted ~60%, pending ~25%, on_hold ~10%, reversed ~5%.",
                llm_example_values="'posted', 'pending', 'on_hold', 'reversed'",
            ),
        ],
    )


def _generate_received_dates(due_dates: pd.Series) -> pd.Series:
    """3-band payment timing: 60% on-time (±3 days), 25% moderately late (4-14), 15% very late (15-30)."""
    n = len(due_dates)
    bands = np.random.choice([0, 1, 2], size=n, p=[0.60, 0.25, 0.15])
    days_offset = np.where(
        bands == 0,
        np.random.randint(-3, 4, n),
        np.where(bands == 1, np.random.randint(4, 15, n), np.random.randint(15, 31, n)),
    )
    return pd.Series(pd.to_datetime(due_dates.values) + pd.to_timedelta(days_offset, unit="D"))


def _override_discount_dates(
    dates: pd.Series,
    invoice_dates: pd.Series,
    payment_terms: np.ndarray,
) -> pd.Series:
    """For ~20% of 2/10 Net 30 invoices, replace received_date with invoice_date + 5-10 days
    to simulate customers capturing the early-payment discount."""
    is_2_10 = payment_terms == "2/10 Net 30"
    takes_discount = is_2_10 & (np.random.random(len(dates)) < 0.20)
    if not takes_discount.any():
        return dates
    early_offsets = np.random.randint(5, 11, int(takes_discount.sum()))
    early_dates = pd.to_datetime(invoice_dates.to_numpy()[takes_discount]) + pd.to_timedelta(
        early_offsets, unit="D"
    )
    result = dates.to_numpy().copy().astype("datetime64[ns]")
    result[takes_discount] = early_dates.values
    return pd.Series(result)


def generate_cash_receipts(
    n_samples: int,
    start_date: str = "2024-01-01",
    end_date: str = "2025-12-31",
    invoice_ids: np.ndarray | None = None,
    due_dates: pd.Series | None = None,
    invoice_dates: pd.Series | None = None,
    invoice_totals_usd: np.ndarray | None = None,
    currency_codes: np.ndarray | None = None,
    payment_terms: np.ndarray | None = None,
) -> pd.DataFrame:
    """Returns one or two receipt rows per invoice. ~20-25% of invoices get two receipts.

    The returned DataFrame includes a private '_open_balance' column for use by
    generate_cash_applications. Callers should pass cash_receipts['_open_balance']
    as open_balances rather than recomputing from invoice totals.
    """
    if invoice_ids is None:
        invoice_ids = generate_n_random_uuids(n_samples)
    if currency_codes is None:
        currency_codes = np.full(n_samples, "USD")

    # Decide which invoices get partial payments (two receipts)
    is_partial = np.random.random(n_samples) < 0.225
    partial_idx = np.where(is_partial)[0]
    full_idx = np.where(~is_partial)[0]

    rows: list[dict[str, object]] = []

    # --- Full-payment invoices: one receipt each ---
    if due_dates is not None:
        full_dates = _generate_received_dates(due_dates.iloc[full_idx].reset_index(drop=True))
        if invoice_dates is not None and payment_terms is not None:
            full_dates = _override_discount_dates(
                full_dates,
                invoice_dates.iloc[full_idx].reset_index(drop=True),
                payment_terms[full_idx],
            )
    else:
        full_dates = generate_random_dates(start_date, end_date, len(full_idx))

    for i, inv_idx in enumerate(full_idx):
        inv_total = float(invoice_totals_usd[inv_idx]) if invoice_totals_usd is not None else 0.0
        rows.append(
            {
                "invoice_id": invoice_ids[inv_idx],
                "received_date": full_dates.iloc[i],
                "amount_received": round(inv_total, 2),
                "currency_code": currency_codes[inv_idx],
                "_open_balance": 0.0,
            }
        )

    # --- Partial-payment invoices: two receipts each ---
    if len(partial_idx) > 0:
        if due_dates is not None:
            first_dates = _generate_received_dates(
                due_dates.iloc[partial_idx].reset_index(drop=True)
            )
            if invoice_dates is not None and payment_terms is not None:
                first_dates = _override_discount_dates(
                    first_dates,
                    invoice_dates.iloc[partial_idx].reset_index(drop=True),
                    payment_terms[partial_idx],
                )
        else:
            first_dates = generate_random_dates(start_date, end_date, len(partial_idx))

        for i, inv_idx in enumerate(partial_idx):
            inv_total = (
                float(invoice_totals_usd[inv_idx]) if invoice_totals_usd is not None else 0.0
            )
            partial_rate = np.random.uniform(0.85, 0.99)
            first_amount = round(inv_total * partial_rate, 2)
            remainder = round(inv_total - first_amount, 2)
            first_date = first_dates.iloc[i]
            # Second receipt arrives 5-15 days after the first
            second_date = first_date + pd.Timedelta(days=int(np.random.randint(5, 16)))

            rows.append(
                {
                    "invoice_id": invoice_ids[inv_idx],
                    "received_date": first_date,
                    "amount_received": first_amount,
                    "currency_code": currency_codes[inv_idx],
                    "_open_balance": remainder,
                }
            )
            rows.append(
                {
                    "invoice_id": invoice_ids[inv_idx],
                    "received_date": second_date,
                    "amount_received": remainder,
                    "currency_code": currency_codes[inv_idx],
                    "_open_balance": 0.0,
                }
            )

    df = pd.DataFrame(rows)
    n_rows = len(df)

    df.insert(0, "receipt_id", generate_n_random_uuids(n_rows))
    df.insert(
        2,
        "receipt_number",
        generate_serial_numbers_with_prefix(n_rows, prefix="RCP-", total_length=12),
    )
    df["payment_method"] = np.random.choice(
        _PAYMENT_METHODS, p=_PAYMENT_METHOD_WEIGHTS, size=n_rows
    )
    df["status"] = np.random.choice(_RECEIPT_STATUSES, p=_RECEIPT_STATUS_WEIGHTS, size=n_rows)

    return df
