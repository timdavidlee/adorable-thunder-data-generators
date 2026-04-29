import numpy as np
import pandas as pd

from adorable_thunder.make.field_generators._random_state import get_random_state
from adorable_thunder.make.field_generators.carrier import generate_carriers
from adorable_thunder.make.field_generators.country import generate_country_codes
from adorable_thunder.make.field_generators.identifiers import (
    generate_n_random_uuids,
    generate_serial_numbers_with_prefix,
)
from adorable_thunder.make.record_generators.schemas import CreatePgTableSql, PgColumn

OUTBOUND_SHIPMENTS_TABLE_NAME = "outbound_shipments"

_DELIVERED_RATE = 0.65  # share of fully-complete orders marked as delivered (rest are shipped)


def create_pg_sql_table_schema(pg_schema: str) -> CreatePgTableSql:
    return CreatePgTableSql(
        pg_schema=pg_schema,
        pg_table=OUTBOUND_SHIPMENTS_TABLE_NAME,
        llm_description=(
            "Shipments leaving the warehouse to fulfill customer orders. One row per "
            "order_id. status reflects the aggregate state of the order's pick lines: "
            "shipped/delivered only when every pick line for the order has status picked "
            "or packed. Orders with any pending picks stay in pending or picking; orders "
            "with any exception line are marked exception."
        ),
        pg_columns=[
            PgColumn(
                name="shipment_id",
                data_type="UUID",
                modifiers="PRIMARY KEY",
                llm_description="Unique identifier for the outbound shipment.",
                llm_example_values="'e5f6a7b8-c9d0-1234-efab-345678901234'",
            ),
            PgColumn(
                name="shipment_number",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Human-readable outbound shipment reference.",
                llm_example_values="'OUT-000123', 'OUT-009999'",
            ),
            PgColumn(
                name="order_id",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description=(
                    "Customer order this shipment fulfills. Joins to pick_lists.order_id."
                ),
                llm_example_values="'ORD-000123', 'ORD-009999'",
            ),
            PgColumn(
                name="carrier_scac",
                data_type="VARCHAR(4)",
                modifiers="NOT NULL",
                llm_description="Carrier SCAC code for the outbound move.",
                llm_example_values="'FDEG', 'UPSN', 'USPS'",
            ),
            PgColumn(
                name="carrier_name",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Carrier company name.",
                llm_example_values="'FedEx Ground', 'UPS', 'USPS'",
            ),
            PgColumn(
                name="tracking_number",
                data_type="TEXT",
                modifiers="",
                llm_description=(
                    "Carrier-issued tracking reference. NULL when status is pending, "
                    "picking, or exception (no carrier handoff yet)."
                ),
                llm_example_values="'TRK-0000001234567', NULL",
            ),
            PgColumn(
                name="ship_date",
                data_type="DATE",
                modifiers="",
                llm_description=(
                    "Date the shipment left the warehouse. NULL until status reaches "
                    "shipped or delivered. Falls 0–2 days after the latest pick_date."
                ),
                llm_example_values="'2024-07-02', '2025-11-14', NULL",
            ),
            PgColumn(
                name="destination_country",
                data_type="VARCHAR(2)",
                modifiers="NOT NULL",
                llm_description="ISO-3166-1 alpha-2 destination country code.",
                llm_example_values="'US', 'DE', 'JP'",
            ),
            PgColumn(
                name="weight_kg",
                data_type="NUMERIC(10, 2)",
                modifiers="NOT NULL",
                llm_description="Total shipment weight in kilograms (lognormal distribution).",
                llm_example_values="'1.20', '8.50', '142.30'",
            ),
            PgColumn(
                name="status",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description=(
                    "Outbound lifecycle status derived from pick line statuses. "
                    "exception: any pick is in exception. pending: every pick is pending. "
                    "picking: mix of pending and complete picks. shipped/delivered: all "
                    "picks complete (picked or packed)."
                ),
                llm_example_values="'pending', 'picking', 'shipped', 'delivered', 'exception'",
            ),
        ],
    )


def _rollup_pick_state(pick_lists: pd.DataFrame) -> pd.DataFrame:
    pl = pick_lists[["order_id", "status", "pick_date"]].copy()
    pl["is_exception"] = pl["status"] == "exception"
    pl["is_pending"] = pl["status"] == "pending"
    pl["is_complete"] = (pl["status"] == "picked") | (pl["status"] == "packed")
    grouped = pl.groupby("order_id", sort=False)
    rollup = grouped.agg(
        any_exception=("is_exception", "any"),
        any_pending=("is_pending", "any"),
        all_pending=("is_pending", "all"),
        all_complete=("is_complete", "all"),
        max_pick_date=("pick_date", "max"),
    )
    return rollup.reset_index()


def _assign_status(
    rollup: pd.DataFrame, rng: np.random.RandomState
) -> tuple[np.ndarray, np.ndarray]:
    n = len(rollup)
    any_exception = rollup["any_exception"].to_numpy()
    all_pending = rollup["all_pending"].to_numpy()
    all_complete = rollup["all_complete"].to_numpy() & ~any_exception
    delivered_roll = rng.random(n) < _DELIVERED_RATE

    statuses = np.where(
        any_exception,
        "exception",
        np.where(
            all_pending,
            "pending",
            np.where(
                all_complete,
                np.where(delivered_roll, "delivered", "shipped"),
                "picking",
            ),
        ),
    )
    has_ship_date = (statuses == "shipped") | (statuses == "delivered")
    return statuses, has_ship_date


def generate_outbound_shipments(pick_lists: pd.DataFrame) -> pd.DataFrame:
    rng = get_random_state()

    rollup = _rollup_pick_state(pick_lists)
    n = len(rollup)

    statuses, has_ship_date = _assign_status(rollup, rng)

    ship_offset = rng.randint(0, 3, size=n)
    base_ship_dates = pd.to_datetime(rollup["max_pick_date"]).to_numpy()
    ship_date_arr = base_ship_dates + np.array(ship_offset, dtype="timedelta64[D]").astype(
        "timedelta64[ns]"
    )
    ship_date_with_nulls = pd.Series(
        np.where(has_ship_date, ship_date_arr, np.datetime64("NaT"))
    )

    carriers = generate_carriers(n, mode="parcel")
    tracking_numbers = generate_serial_numbers_with_prefix(
        n, prefix="TRK-", total_length=18
    )
    tracking_with_nulls = np.array(tracking_numbers, dtype=object)
    tracking_with_nulls[~has_ship_date] = None

    return pd.DataFrame(
        {
            "shipment_id": generate_n_random_uuids(n),
            "shipment_number": generate_serial_numbers_with_prefix(
                n, prefix="OUT-", total_length=10
            ),
            "order_id": rollup["order_id"].to_numpy(),
            "carrier_scac": carriers["carrier_scac"].to_numpy(),
            "carrier_name": carriers["carrier_name"].to_numpy(),
            "tracking_number": tracking_with_nulls,
            "ship_date": ship_date_with_nulls,
            "destination_country": generate_country_codes(n),
            "weight_kg": np.round(np.exp(rng.normal(loc=1.5, scale=1.3, size=n)), 2),
            "status": statuses,
        }
    )
