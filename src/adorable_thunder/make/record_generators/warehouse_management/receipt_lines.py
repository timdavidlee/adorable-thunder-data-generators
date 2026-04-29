import numpy as np
import pandas as pd

from adorable_thunder.make.field_generators._random_state import get_random_state
from adorable_thunder.make.field_generators.dates import extrapolate_off_dates
from adorable_thunder.make.field_generators.identifiers import generate_n_random_uuids
from adorable_thunder.make.record_generators.schemas import CreatePgTableSql, PgColumn

RECEIPT_LINES_TABLE_NAME = "receipt_lines"

_LINES_PER_SHIPMENT_MIN = 1
_LINES_PER_SHIPMENT_MAX = 4

# Receiving accuracy benchmark: 97–99% lines exact. We pick ~98% exact.
_EXACT_RECEIVE_RATE = 0.98

_CONDITIONS = np.array(["LIKE_NEW", "GOOD", "FAIR", "DAMAGED"])
_CONDITION_WEIGHTS = np.array([0.55, 0.35, 0.07, 0.03])

_UOMS = np.array(["EA", "CASE", "PALLET"])
_UOM_WEIGHTS = np.array([0.65, 0.28, 0.07])


def create_pg_sql_table_schema(pg_schema: str) -> CreatePgTableSql:
    return CreatePgTableSql(
        pg_schema=pg_schema,
        pg_table=RECEIPT_LINES_TABLE_NAME,
        llm_description=(
            "Line-level putaway records for received shipments. ~98% of lines have "
            "received_qty equal to expected_qty; the remaining ~2% have small over/under "
            "discrepancies. put_to_location_id references storage_locations.location_id "
            "and is always a zone whose category matches the SKU prefix."
        ),
        pg_columns=[
            PgColumn(
                name="receipt_id",
                data_type="UUID",
                modifiers="PRIMARY KEY",
                llm_description="Unique identifier for the receipt line.",
                llm_example_values="'c3d4e5f6-a7b8-9012-cdef-123456789012'",
            ),
            PgColumn(
                name="shipment_id",
                data_type="UUID",
                modifiers="NOT NULL",
                llm_description="Foreign key to inbound_shipments.shipment_id.",
                llm_example_values="'b2c3d4e5-f6a7-8901-bcde-f12345678901'",
            ),
            PgColumn(
                name="sku",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description=(
                    "SKU received on this line. Prefix matches the destination zone — "
                    "PERISH- for COLD, HAZ- for HAZMAT, otherwise PROD-."
                ),
                llm_example_values="'PROD-0012345', 'PERISH-0004001', 'HAZ-0000123'",
            ),
            PgColumn(
                name="expected_qty",
                data_type="INTEGER",
                modifiers="NOT NULL",
                llm_description="Units expected per the inbound advance shipment notice.",
                llm_example_values="'50', '500', '2000'",
            ),
            PgColumn(
                name="received_qty",
                data_type="INTEGER",
                modifiers="NOT NULL",
                llm_description=(
                    "Units actually received. Equal to expected_qty for ~98% of lines; the "
                    "rest show small over/under discrepancies."
                ),
                llm_example_values="'50', '498', '2003'",
            ),
            PgColumn(
                name="uom",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description=(
                    "Unit of measure for the qty fields. EA ~65%, CASE ~28%, PALLET ~7%."
                ),
                llm_example_values="'EA', 'CASE', 'PALLET'",
            ),
            PgColumn(
                name="condition",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description=(
                    "Receiving inspection grade. Mix: LIKE_NEW ~55%, GOOD ~35%, FAIR ~7%, "
                    "DAMAGED ~3%."
                ),
                llm_example_values="'LIKE_NEW', 'GOOD', 'FAIR', 'DAMAGED'",
            ),
            PgColumn(
                name="put_to_location_id",
                data_type="UUID",
                modifiers="NOT NULL",
                llm_description=(
                    "Foreign key to storage_locations.location_id where stock was put away. "
                    "Zone of the location matches the SKU category."
                ),
                llm_example_values="'a1b2c3d4-e5f6-7890-abcd-ef1234567890'",
            ),
            PgColumn(
                name="receipt_date",
                data_type="DATE",
                modifiers="NOT NULL",
                llm_description=(
                    "Date the line was put away. Equals the shipment's actual_date "
                    "(or +0/+1 day for staggered putaway)."
                ),
                llm_example_values="'2024-06-16', '2025-10-02'",
            ),
        ],
    )


def _sku_for_zone(zone: str, sku_index: int) -> str:
    if zone == "COLD":
        return f"PERISH-{sku_index:07d}"
    if zone == "HAZMAT":
        return f"HAZ-{sku_index:07d}"
    return f"PROD-{sku_index:07d}"


def generate_receipt_lines(
    shipment_ids: np.ndarray,
    shipment_actual_dates: pd.Series,
    shipment_statuses: np.ndarray,
    storage_locations: pd.DataFrame,
) -> pd.DataFrame:
    rng = get_random_state()

    received_mask = shipment_statuses == "received"
    eligible_shipments = shipment_ids[received_mask]
    eligible_dates = shipment_actual_dates[received_mask].reset_index(drop=True)
    n_shipments = len(eligible_shipments)
    if n_shipments == 0:
        return pd.DataFrame(
            {
                "receipt_id": np.array([], dtype=object),
                "shipment_id": np.array([], dtype=object),
                "sku": np.array([], dtype=object),
                "expected_qty": np.array([], dtype=int),
                "received_qty": np.array([], dtype=int),
                "uom": np.array([], dtype=object),
                "condition": np.array([], dtype=object),
                "put_to_location_id": np.array([], dtype=object),
                "receipt_date": pd.Series([], dtype="datetime64[ns]"),
            }
        )

    lines_per_shipment = rng.randint(
        _LINES_PER_SHIPMENT_MIN, _LINES_PER_SHIPMENT_MAX + 1, size=n_shipments
    )
    n_rows = int(lines_per_shipment.sum())

    repeated_shipment_ids = np.repeat(eligible_shipments, lines_per_shipment)
    repeated_dates = pd.Series(np.repeat(eligible_dates.to_numpy(), lines_per_shipment))

    location_indices = rng.randint(0, len(storage_locations), size=n_rows)
    chosen_locations = storage_locations.iloc[location_indices].reset_index(drop=True)

    sku_indices = rng.randint(1, 50_000, size=n_rows)
    skus = np.array(
        [_sku_for_zone(z, idx) for z, idx in zip(chosen_locations["zone"], sku_indices)],
        dtype=object,
    )

    expected_qty = rng.randint(10, 2001, size=n_rows)
    is_exact = rng.random(n_rows) < _EXACT_RECEIVE_RATE
    discrepancy = rng.randint(-10, 11, size=n_rows)
    discrepancy[discrepancy == 0] = 1  # ensure non-zero when not is_exact
    received_qty = np.where(is_exact, expected_qty, expected_qty + discrepancy)
    received_qty = np.maximum(received_qty, 0)

    receipt_dates = extrapolate_off_dates(repeated_dates, min_days=0, max_days=1)

    return pd.DataFrame(
        {
            "receipt_id": generate_n_random_uuids(n_rows),
            "shipment_id": repeated_shipment_ids,
            "sku": skus,
            "expected_qty": expected_qty,
            "received_qty": received_qty,
            "uom": rng.choice(_UOMS, p=_UOM_WEIGHTS, size=n_rows),
            "condition": rng.choice(_CONDITIONS, p=_CONDITION_WEIGHTS, size=n_rows),
            "put_to_location_id": chosen_locations["location_id"].to_numpy(),
            "receipt_date": receipt_dates,
        }
    )
