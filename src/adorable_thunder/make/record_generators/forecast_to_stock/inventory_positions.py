import numpy as np
import pandas as pd

from adorable_thunder.make.field_generators._random_state import get_random_state
from adorable_thunder.make.field_generators.dates import generate_random_dates
from adorable_thunder.make.field_generators.identifiers import generate_n_random_uuids
from adorable_thunder.make.record_generators.schemas import CreatePgTableSql, PgColumn

_SNAPSHOTS_PER_PAIR = 3
_TRIGGER_RATE = 0.30  # ~30% of snapshots fall at or below reorder point

INVENTORY_POSITIONS_TABLE_NAME = "inventory_positions"


def create_pg_sql_table_schema(pg_schema: str) -> CreatePgTableSql:
    return CreatePgTableSql(
        pg_schema=pg_schema,
        pg_table=INVENTORY_POSITIONS_TABLE_NAME,
        llm_description="Periodic inventory snapshots per SKU/location. available_qty = on_hand_qty + on_order_qty − committed_qty. ~30% of snapshots fall at or below reorder_point and trigger a replenishment order.",
        pg_columns=[
            PgColumn(
                name="record_id",
                data_type="UUID",
                modifiers="PRIMARY KEY",
                llm_description="Unique identifier for the inventory snapshot row.",
                llm_example_values="'c3d4e5f6-a7b8-9012-cdef-123456789012'",
            ),
            PgColumn(
                name="sku",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="SKU at this position. Joins to stock_parameters.sku.",
                llm_example_values="'PROD-0012345', 'SKU-0067890'",
            ),
            PgColumn(
                name="location",
                data_type="VARCHAR(2)",
                modifiers="NOT NULL",
                llm_description="ISO-3166-1 alpha-2 country code where stock is held.",
                llm_example_values="'US', 'DE', 'GB', 'JP'",
            ),
            PgColumn(
                name="as_of_date",
                data_type="DATE",
                modifiers="NOT NULL",
                llm_description="Snapshot date this position reflects.",
                llm_example_values="'2024-06-30', '2025-03-31'",
            ),
            PgColumn(
                name="on_hand_qty",
                data_type="INTEGER",
                modifiers="NOT NULL",
                llm_description="Physical units in stock. Always non-negative.",
                llm_example_values="'0', '450', '12500'",
            ),
            PgColumn(
                name="on_order_qty",
                data_type="INTEGER",
                modifiers="NOT NULL",
                llm_description="Units on open replenishment orders not yet received.",
                llm_example_values="'0', '500', '2500'",
            ),
            PgColumn(
                name="committed_qty",
                data_type="INTEGER",
                modifiers="NOT NULL",
                llm_description="Units allocated to open sales orders (not yet shipped).",
                llm_example_values="'0', '120', '800'",
            ),
            PgColumn(
                name="available_qty",
                data_type="INTEGER",
                modifiers="NOT NULL",
                llm_description="Derived: on_hand_qty + on_order_qty − committed_qty. Compared against reorder_point to trigger replenishment.",
                llm_example_values="'0', '830', '14200'",
            ),
            PgColumn(
                name="inventory_value_usd",
                data_type="NUMERIC(14, 2)",
                modifiers="NOT NULL",
                llm_description="On-hand inventory valuation in USD = on_hand_qty × unit_cost_usd. Drives working-capital and $-weighted overstock metrics.",
                llm_example_values="'0.00', '4250.00', '125000.00'",
            ),
        ],
    )


def generate_inventory_positions(
    skus: np.ndarray,
    locations: np.ndarray,
    reorder_points: np.ndarray,
    avg_daily_demand: np.ndarray,
    unit_cost_usd: np.ndarray,
    start_date: str = "2024-01-01",
    end_date: str = "2025-12-31",
) -> pd.DataFrame:
    rng = get_random_state()
    n_pairs = len(skus)
    n_rows = n_pairs * _SNAPSHOTS_PER_PAIR

    repeated_skus = np.repeat(skus, _SNAPSHOTS_PER_PAIR)
    repeated_locations = np.repeat(locations, _SNAPSHOTS_PER_PAIR)
    repeated_reorder = np.repeat(reorder_points, _SNAPSHOTS_PER_PAIR)
    repeated_demand = np.repeat(avg_daily_demand, _SNAPSHOTS_PER_PAIR)
    repeated_unit_cost = np.repeat(unit_cost_usd, _SNAPSHOTS_PER_PAIR)

    is_triggered = rng.random(n_rows) < _TRIGGER_RATE

    on_hand_qty = np.where(
        is_triggered,
        np.floor(repeated_reorder * rng.uniform(0.0, 0.8, size=n_rows)).astype(int),
        np.floor(repeated_reorder * rng.uniform(1.1, 2.0, size=n_rows)).astype(int),
    )
    on_hand_qty = np.maximum(on_hand_qty, 0)

    on_order_qty = np.where(
        is_triggered,
        np.floor(repeated_reorder * rng.uniform(0.0, 0.5, size=n_rows)).astype(int),
        np.where(
            rng.random(n_rows) < 0.30,
            np.floor(repeated_reorder * rng.uniform(0.0, 0.4, size=n_rows)).astype(int),
            0,
        ),
    )

    committed_qty = np.floor(repeated_demand * rng.uniform(0.0, 7.0, size=n_rows)).astype(int)
    committed_qty = np.minimum(committed_qty, on_hand_qty)

    available_qty = on_hand_qty + on_order_qty - committed_qty

    inventory_value_usd = np.round(on_hand_qty * repeated_unit_cost, 2)

    return pd.DataFrame(
        {
            "record_id": generate_n_random_uuids(n_rows),
            "sku": repeated_skus,
            "location": repeated_locations,
            "as_of_date": generate_random_dates(start_date, end_date, n_rows),
            "on_hand_qty": on_hand_qty,
            "on_order_qty": on_order_qty,
            "committed_qty": committed_qty,
            "available_qty": available_qty,
            "inventory_value_usd": inventory_value_usd,
        }
    )
