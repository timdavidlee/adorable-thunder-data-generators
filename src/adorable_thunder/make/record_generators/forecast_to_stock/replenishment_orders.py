import numpy as np
import pandas as pd

from adorable_thunder.make.field_generators._random_state import get_random_state
from adorable_thunder.make.field_generators.identifiers import (
    generate_n_random_uuids,
    generate_serial_numbers_with_prefix,
)
from adorable_thunder.make.record_generators.schemas import CreatePgTableSql, PgColumn

_STATUSES = np.array(["pending", "in_transit", "received", "cancelled"])
_STATUS_WEIGHTS = np.array([0.25, 0.35, 0.35, 0.05])

REPLENISHMENT_ORDERS_TABLE_NAME = "replenishment_orders"


def create_pg_sql_table_schema(pg_schema: str) -> CreatePgTableSql:
    return CreatePgTableSql(
        pg_schema=pg_schema,
        pg_table=REPLENISHMENT_ORDERS_TABLE_NAME,
        llm_description="Replenishment orders triggered when an inventory snapshot's available_qty ≤ reorder_point. order_qty ≥ (reorder_point − on_hand_qty + safety_stock_qty), rounded up to economic_order_qty. expected_receipt_date = trigger_date + lead_time_days.",
        pg_columns=[
            PgColumn(
                name="order_id",
                data_type="UUID",
                modifiers="PRIMARY KEY",
                llm_description="Unique identifier for the replenishment order.",
                llm_example_values="'d4e5f6a7-b8c9-0123-defa-234567890123'",
            ),
            PgColumn(
                name="order_number",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Human-readable replenishment order reference.",
                llm_example_values="'REP-000001', 'REP-009999'",
            ),
            PgColumn(
                name="sku",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="SKU being replenished. Joins to stock_parameters.sku.",
                llm_example_values="'PROD-0012345', 'SKU-0067890'",
            ),
            PgColumn(
                name="location",
                data_type="VARCHAR(2)",
                modifiers="NOT NULL",
                llm_description="ISO-3166-1 alpha-2 country code where stock will be received.",
                llm_example_values="'US', 'DE', 'GB', 'JP'",
            ),
            PgColumn(
                name="trigger_date",
                data_type="DATE",
                modifiers="NOT NULL",
                llm_description="Date the snapshot triggered replenishment. Equals the as_of_date of the source inventory_position.",
                llm_example_values="'2024-06-30', '2025-03-31'",
            ),
            PgColumn(
                name="order_qty",
                data_type="INTEGER",
                modifiers="NOT NULL",
                llm_description="Units ordered. Sized to cover reorder gap + safety stock and rounded up to a multiple of economic_order_qty.",
                llm_example_values="'500', '1000', '2500'",
            ),
            PgColumn(
                name="expected_receipt_date",
                data_type="DATE",
                modifiers="NOT NULL",
                llm_description="Expected delivery date = trigger_date + lead_time_days.",
                llm_example_values="'2024-07-14', '2025-06-30'",
            ),
            PgColumn(
                name="status",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Order lifecycle status. Mix: pending ~25%, in_transit ~35%, received ~35%, cancelled ~5%.",
                llm_example_values="'pending', 'in_transit', 'received', 'cancelled'",
            ),
            PgColumn(
                name="actual_receipt_date",
                data_type="DATE",
                modifiers="",
                llm_description="Actual goods-receipt date. Populated only when status = 'received'; NULL otherwise. Compared against expected_receipt_date for supplier OTD%.",
                llm_example_values="'2024-07-12', '2025-06-18', NULL",
            ),
        ],
    )


def generate_replenishment_orders(
    skus: np.ndarray,
    locations: np.ndarray,
    trigger_dates: pd.Series,
    on_hand_qty: np.ndarray,
    reorder_points: np.ndarray,
    safety_stock_qty: np.ndarray,
    economic_order_qty: np.ndarray,
    lead_time_days: np.ndarray,
) -> pd.DataFrame:
    rng = get_random_state()
    n = len(skus)

    needed = (reorder_points - on_hand_qty + safety_stock_qty).astype(int)
    needed = np.maximum(needed, 1)
    multiples = np.ceil(needed / economic_order_qty).astype(int)
    order_qty = (multiples * economic_order_qty).astype(int)

    expected_receipt_date = (
        trigger_dates + pd.to_timedelta(lead_time_days, unit="D")
    ).reset_index(drop=True)

    status = rng.choice(_STATUSES, p=_STATUS_WEIGHTS, size=n)

    # Skew receipt offset slightly late so OTD% lands ~80–90%; early receipts allowed.
    receipt_offset_days = rng.randint(-2, 8, size=n)
    actual_receipt_date = expected_receipt_date + pd.to_timedelta(
        receipt_offset_days, unit="D"
    )
    # Series.where with no `other` substitutes NaT for datetime-typed series.
    actual_receipt_date = actual_receipt_date.where(pd.Series(status == "received"))

    return pd.DataFrame(
        {
            "order_id": generate_n_random_uuids(n),
            "order_number": generate_serial_numbers_with_prefix(
                n, prefix="REP-", total_length=10
            ),
            "sku": skus,
            "location": locations,
            "trigger_date": trigger_dates.reset_index(drop=True),
            "order_qty": order_qty,
            "expected_receipt_date": expected_receipt_date,
            "status": status,
            "actual_receipt_date": actual_receipt_date,
        }
    )
