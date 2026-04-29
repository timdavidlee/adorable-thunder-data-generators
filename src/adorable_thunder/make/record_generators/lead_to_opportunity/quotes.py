import numpy as np
import pandas as pd

from adorable_thunder.make.field_generators._random_state import get_random_state
from adorable_thunder.make.field_generators.dates import extrapolate_off_dates
from adorable_thunder.make.field_generators.identifiers import (
    generate_n_random_uuids,
    generate_serial_numbers_with_prefix,
)
from adorable_thunder.make.field_generators.percentage import generate_discount_rates
from adorable_thunder.make.record_generators.schemas import CreatePgTableSql, PgColumn

QUOTES_TABLE_NAME = "quotes"


def create_pg_sql_table_schema(pg_schema: str) -> CreatePgTableSql:
    return CreatePgTableSql(
        pg_schema=pg_schema,
        pg_table=QUOTES_TABLE_NAME,
        llm_description="Formal price quotes issued for opportunities in Proposal stage or later. total_amount = deal_value × (1 − discount_rate). Contract values should closely match quote totals (within 5%).",
        pg_columns=[
            PgColumn(
                name="quote_id",
                data_type="UUID",
                modifiers="PRIMARY KEY",
                llm_description="Unique identifier for the quote.",
                llm_example_values="'d4e5f6a7-b8c9-0123-defa-234567890123'",
            ),
            PgColumn(
                name="quote_number",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Human-readable quote reference.",
                llm_example_values="'QTE-000001', 'QTE-009999'",
            ),
            PgColumn(
                name="opp_id",
                data_type="UUID",
                modifiers="NOT NULL",
                llm_description="FK to the opportunity this quote covers.",
                llm_example_values="'c3d4e5f6-a7b8-9012-cdef-123456789012'",
            ),
            PgColumn(
                name="quote_date",
                data_type="DATE",
                modifiers="NOT NULL",
                llm_description="Date the quote was issued. Must be ≥ the opportunity's created_date.",
                llm_example_values="'2024-05-10', '2025-02-15'",
            ),
            PgColumn(
                name="line_item_count",
                data_type="INTEGER",
                modifiers="NOT NULL",
                llm_description="Number of line items on the quote. Typically 1–8.",
                llm_example_values="'1', '3', '5'",
            ),
            PgColumn(
                name="discount_rate",
                data_type="NUMERIC(5, 4)",
                modifiers="NOT NULL",
                llm_description="Discount applied as a fraction (0.0–0.30). Most quotes 0–15%; large deals may reach 25–30%.",
                llm_example_values="'0.0000', '0.1000', '0.1500'",
            ),
            PgColumn(
                name="total_amount",
                data_type="NUMERIC(18, 2)",
                modifiers="NOT NULL",
                llm_description="Quote total after discount = deal_value × (1 − discount_rate).",
                llm_example_values="'22500.00', '162000.00', '1350000.00'",
            ),
            PgColumn(
                name="expiry_date",
                data_type="DATE",
                modifiers="NOT NULL",
                llm_description="Date the quote offer expires. Typically 30–90 days after quote_date.",
                llm_example_values="'2024-06-10', '2025-05-15'",
            ),
        ],
    )


def generate_quotes(
    n_samples: int,
    opp_ids: np.ndarray,
    deal_values: np.ndarray,
    opp_dates: pd.Series,
) -> pd.DataFrame:
    discount_rates = generate_discount_rates(n_samples)
    total_amounts = np.round(deal_values * (1 - discount_rates), 2)

    # Quote issued 0–14 days after opportunity created_date
    quote_dates = extrapolate_off_dates(opp_dates, min_days=0, max_days=14)
    expiry_dates = extrapolate_off_dates(quote_dates, min_days=30, max_days=90)

    line_item_counts = get_random_state().choice(
        np.arange(1, 9),
        p=[0.30, 0.25, 0.20, 0.12, 0.07, 0.03, 0.02, 0.01],
        size=n_samples,
    )

    return pd.DataFrame(
        {
            "quote_id": generate_n_random_uuids(n_samples),
            "quote_number": generate_serial_numbers_with_prefix(
                n_samples, prefix="QTE-", total_length=10
            ),
            "opp_id": opp_ids,
            "quote_date": quote_dates,
            "line_item_count": line_item_counts,
            "discount_rate": discount_rates,
            "total_amount": total_amounts,
            "expiry_date": expiry_dates,
        }
    )
