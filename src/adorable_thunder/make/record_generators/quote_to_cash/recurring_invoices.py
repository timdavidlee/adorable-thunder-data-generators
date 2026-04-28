import numpy as np
import pandas as pd

from adorable_thunder.make.field_generators.identifiers import (
    generate_n_random_uuids,
    generate_serial_numbers_with_prefix,
)
from adorable_thunder.make.record_generators.schemas import CreatePgTableSql, PgColumn

_INVOICE_STATUSES = np.array(["paid", "pending", "overdue", "void"])
_INVOICE_STATUS_WEIGHTS = np.array([0.85, 0.08, 0.05, 0.02])

RECURRING_INVOICES_TABLE_NAME = "recurring_invoices"


def create_pg_sql_table_schema(pg_schema: str) -> CreatePgTableSql:
    return CreatePgTableSql(
        pg_schema=pg_schema,
        pg_table=RECURRING_INVOICES_TABLE_NAME,
        llm_description=(
            "Recurring invoices generated on the subscription billing cycle. "
            "billing_period_end of invoice N equals billing_period_start of invoice N+1 — "
            "no gaps or overlaps. amount = mrr_usd × billing_cycle_months. No invoices "
            "with date > sub.churn_date for churned subscriptions."
        ),
        pg_columns=[
            PgColumn(
                name="invoice_id",
                data_type="UUID",
                modifiers="PRIMARY KEY",
                llm_description="Unique identifier for the recurring invoice.",
                llm_example_values="'c3d4e5f6-a7b8-9012-cdef-345678901234'",
            ),
            PgColumn(
                name="sub_id",
                data_type="UUID",
                modifiers="NOT NULL",
                llm_description="Foreign key to the subscription being billed.",
                llm_example_values="'a1b2c3d4-e5f6-7890-abcd-ef1234567890'",
            ),
            PgColumn(
                name="invoice_number",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Human-readable invoice reference number.",
                llm_example_values="'RIN-00001234', 'RIN-00009999'",
            ),
            PgColumn(
                name="invoice_date",
                data_type="DATE",
                modifiers="NOT NULL",
                llm_description=(
                    "Date the invoice was issued — equals billing_period_start "
                    "(invoice issued at start of period)."
                ),
                llm_example_values="'2024-02-01', '2024-03-01'",
            ),
            PgColumn(
                name="billing_period_start",
                data_type="DATE",
                modifiers="NOT NULL",
                llm_description=(
                    "Inclusive start of the billing period covered by this invoice. "
                    "Spaced exactly billing_cycle_months apart from prior invoice."
                ),
                llm_example_values="'2024-02-01', '2024-03-01'",
            ),
            PgColumn(
                name="billing_period_end",
                data_type="DATE",
                modifiers="NOT NULL",
                llm_description=(
                    "Exclusive end of the billing period; equals billing_period_start "
                    "of the next invoice for this subscription."
                ),
                llm_example_values="'2024-03-01', '2024-04-01'",
            ),
            PgColumn(
                name="amount",
                data_type="NUMERIC(18, 2)",
                modifiers="NOT NULL",
                llm_description="Invoice amount = mrr_usd × billing_cycle_months.",
                llm_example_values="'49.00', '850.00', '78000.00'",
            ),
            PgColumn(
                name="currency_code",
                data_type="VARCHAR(3)",
                modifiers="NOT NULL",
                llm_description="ISO 4217 currency. Inherits from the subscription.",
                llm_example_values="'USD', 'EUR', 'GBP'",
            ),
            PgColumn(
                name="status",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description=(
                    "Invoice lifecycle status. Expected mix: paid ~85%, pending ~8%, "
                    "overdue ~5%, void ~2%."
                ),
                llm_example_values="'paid', 'pending', 'overdue', 'void'",
            ),
        ],
    )


def _months_between(start: pd.Timestamp, end: pd.Timestamp) -> int:
    return (end.year - start.year) * 12 + (end.month - start.month)


def generate_recurring_invoices(
    sub_ids: np.ndarray,
    sub_start_dates: pd.Series,
    sub_end_dates: pd.Series,
    billing_cycle_months: np.ndarray,
    mrr_usd: np.ndarray,
    currency_codes: np.ndarray,
    churn_dates: pd.Series,
    dataset_end: str,
) -> pd.DataFrame:
    """One row per billing period from start_date through min(end_date, churn_date, dataset_end)."""
    dataset_end_ts = pd.Timestamp(dataset_end)
    starts = pd.to_datetime(sub_start_dates).reset_index(drop=True)
    ends = pd.to_datetime(sub_end_dates).reset_index(drop=True)
    churns = pd.to_datetime(churn_dates).reset_index(drop=True)

    rows: list[dict[str, object]] = []
    for i in range(len(sub_ids)):
        start = starts.iloc[i]
        end = ends.iloc[i]
        churn = churns.iloc[i]
        cap = min(end, dataset_end_ts)
        if pd.notna(churn):
            cap = min(cap, churn)
        if cap <= start:
            continue

        cycle = int(billing_cycle_months[i])
        max_periods = _months_between(start, cap) // cycle
        if max_periods <= 0:
            continue

        period_amount = round(float(mrr_usd[i]) * cycle, 2)

        for period_idx in range(max_periods):
            period_start = start + pd.DateOffset(months=period_idx * cycle)
            period_end = start + pd.DateOffset(months=(period_idx + 1) * cycle)
            rows.append(
                {
                    "sub_id": sub_ids[i],
                    "invoice_date": period_start,
                    "billing_period_start": period_start,
                    "billing_period_end": period_end,
                    "amount": period_amount,
                    "currency_code": currency_codes[i],
                }
            )

    df = pd.DataFrame(rows)
    n_rows = len(df)
    if n_rows == 0:
        return pd.DataFrame(
            columns=[
                "invoice_id",
                "sub_id",
                "invoice_number",
                "invoice_date",
                "billing_period_start",
                "billing_period_end",
                "amount",
                "currency_code",
                "status",
            ]
        )

    df.insert(0, "invoice_id", generate_n_random_uuids(n_rows))
    df.insert(
        2,
        "invoice_number",
        generate_serial_numbers_with_prefix(n_rows, prefix="RIN-", total_length=12),
    )
    df["status"] = np.random.choice(_INVOICE_STATUSES, p=_INVOICE_STATUS_WEIGHTS, size=n_rows)
    return df[
        [
            "invoice_id",
            "sub_id",
            "invoice_number",
            "invoice_date",
            "billing_period_start",
            "billing_period_end",
            "amount",
            "currency_code",
            "status",
        ]
    ]
