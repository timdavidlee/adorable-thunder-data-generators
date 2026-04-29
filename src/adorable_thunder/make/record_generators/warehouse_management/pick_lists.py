import numpy as np
import pandas as pd

from adorable_thunder.make.field_generators._random_state import get_random_state
from adorable_thunder.make.field_generators.dates import generate_random_dates
from adorable_thunder.make.field_generators.identifiers import (
    generate_n_random_uuids,
    generate_serial_numbers_with_prefix,
)
from adorable_thunder.make.field_generators.users import generate_user_emails
from adorable_thunder.make.record_generators.schemas import CreatePgTableSql, PgColumn

PICK_LISTS_TABLE_NAME = "pick_lists"

_LINES_PER_ORDER_MIN = 1
_LINES_PER_ORDER_MAX = 4

# Pickable zones — a picker would not normally source from QUARANTINE or RETURNS.
_PICKABLE_ZONES = {"BULK", "PICK", "STAGING", "COLD", "HAZMAT"}

# Pick accuracy benchmark: 99.5–99.9% of picks succeed without exception.
_STATUSES = np.array(["pending", "picked", "packed", "exception"])
_STATUS_WEIGHTS = np.array([0.10, 0.59, 0.305, 0.005])


def create_pg_sql_table_schema(pg_schema: str) -> CreatePgTableSql:
    return CreatePgTableSql(
        pg_schema=pg_schema,
        pg_table=PICK_LISTS_TABLE_NAME,
        llm_description=(
            "Line-level pick instructions for outbound orders. Each row is one SKU pulled "
            "from one location for one order. Multiple lines share an order_id when an "
            "order has multiple SKUs. from_location_id always references a location in a "
            "pickable zone (BULK, PICK, STAGING, COLD, HAZMAT) whose zone matches the SKU "
            "category. ~5% of lines end in exception."
        ),
        pg_columns=[
            PgColumn(
                name="picklist_id",
                data_type="UUID",
                modifiers="PRIMARY KEY",
                llm_description="Unique identifier for the pick line.",
                llm_example_values="'d4e5f6a7-b8c9-0123-defa-234567890123'",
            ),
            PgColumn(
                name="picklist_number",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Human-readable pick line reference.",
                llm_example_values="'PCK-000123', 'PCK-009999'",
            ),
            PgColumn(
                name="order_id",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description=(
                    "Customer order this pick is for. Joins to outbound_shipments.order_id; "
                    "shared across all pick lines for the same order."
                ),
                llm_example_values="'ORD-000123', 'ORD-009999'",
            ),
            PgColumn(
                name="sku",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="SKU being picked.",
                llm_example_values="'PROD-0012345', 'PERISH-0004001', 'HAZ-0000123'",
            ),
            PgColumn(
                name="pick_qty",
                data_type="INTEGER",
                modifiers="NOT NULL",
                llm_description="Units to pick for this line.",
                llm_example_values="'1', '12', '120'",
            ),
            PgColumn(
                name="from_location_id",
                data_type="UUID",
                modifiers="NOT NULL",
                llm_description=(
                    "Foreign key to storage_locations.location_id sourced for the pick. "
                    "Always a location in a pickable zone matching the SKU category."
                ),
                llm_example_values="'a1b2c3d4-e5f6-7890-abcd-ef1234567890'",
            ),
            PgColumn(
                name="assigned_to",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Email of the warehouse worker assigned to the pick.",
                llm_example_values="'jane.doe@example.com'",
            ),
            PgColumn(
                name="pick_date",
                data_type="DATE",
                modifiers="NOT NULL",
                llm_description="Date the pick was performed (or scheduled, for pending lines).",
                llm_example_values="'2024-07-01', '2025-11-12'",
            ),
            PgColumn(
                name="status",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description=(
                    "Pick line status. Mix: pending ~10%, picked ~55%, packed ~30%, "
                    "exception ~5%."
                ),
                llm_example_values="'pending', 'picked', 'packed', 'exception'",
            ),
        ],
    )


def _sku_for_zone(zone: str, sku_index: int) -> str:
    if zone == "COLD":
        return f"PERISH-{sku_index:07d}"
    if zone == "HAZMAT":
        return f"HAZ-{sku_index:07d}"
    return f"PROD-{sku_index:07d}"


def generate_pick_lists(
    n_orders: int,
    storage_locations: pd.DataFrame,
    start_date: str = "2024-01-01",
    end_date: str = "2025-12-31",
) -> pd.DataFrame:
    rng = get_random_state()

    pickable_locations = storage_locations[
        storage_locations["zone"].isin(_PICKABLE_ZONES)
    ].reset_index(drop=True)

    order_ids = generate_serial_numbers_with_prefix(n_orders, prefix="ORD-", total_length=10)
    order_dates = generate_random_dates(start_date, end_date, n_orders)

    lines_per_order = rng.randint(
        _LINES_PER_ORDER_MIN, _LINES_PER_ORDER_MAX + 1, size=n_orders
    )
    n_rows = int(lines_per_order.sum())

    repeated_order_ids = np.repeat(order_ids, lines_per_order)
    repeated_order_dates = pd.Series(np.repeat(order_dates.to_numpy(), lines_per_order))

    location_indices = rng.randint(0, len(pickable_locations), size=n_rows)
    chosen_locations = pickable_locations.iloc[location_indices].reset_index(drop=True)

    sku_indices = rng.randint(1, 50_000, size=n_rows)
    skus = np.array(
        [_sku_for_zone(z, idx) for z, idx in zip(chosen_locations["zone"], sku_indices)],
        dtype=object,
    )

    pick_qty = rng.randint(1, 200, size=n_rows)

    statuses = rng.choice(_STATUSES, p=_STATUS_WEIGHTS, size=n_rows)

    return pd.DataFrame(
        {
            "picklist_id": generate_n_random_uuids(n_rows),
            "picklist_number": generate_serial_numbers_with_prefix(
                n_rows, prefix="PCK-", total_length=10
            ),
            "order_id": repeated_order_ids,
            "sku": skus,
            "pick_qty": pick_qty,
            "from_location_id": chosen_locations["location_id"].to_numpy(),
            "assigned_to": generate_user_emails(n_rows),
            "pick_date": repeated_order_dates,
            "status": statuses,
        }
    )
