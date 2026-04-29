import numpy as np
import pandas as pd

from adorable_thunder.make.field_generators._random_state import get_random_state
from adorable_thunder.make.field_generators.identifiers import generate_n_random_uuids
from adorable_thunder.make.record_generators.schemas import CreatePgTableSql, PgColumn

STORAGE_LOCATIONS_TABLE_NAME = "storage_locations"

_WAREHOUSES = np.array(["WH1", "WH2", "WH3"])
_WAREHOUSE_WEIGHTS = np.array([0.45, 0.35, 0.20])

_ZONES = np.array(["BULK", "PICK", "STAGING", "COLD", "HAZMAT", "RETURNS", "QUARANTINE"])
_ZONE_WEIGHTS = np.array([0.40, 0.30, 0.10, 0.08, 0.05, 0.04, 0.03])

# Capacity ranges per zone (min, max). Bulk locations hold pallets; pick faces hold cases.
_ZONE_CAPACITY_RANGES = {
    "BULK": (500, 2000),
    "PICK": (50, 200),
    "STAGING": (200, 800),
    "COLD": (100, 500),
    "HAZMAT": (100, 400),
    "RETURNS": (50, 300),
    "QUARANTINE": (50, 300),
}

# Empty-location share by zone — STAGING and RETURNS turn over fast and are often empty.
# Tuned so overall fill rate lands in the 70–85% realism band.
_ZONE_EMPTY_RATE = {
    "BULK": 0.08,
    "PICK": 0.04,
    "STAGING": 0.30,
    "COLD": 0.10,
    "HAZMAT": 0.15,
    "RETURNS": 0.35,
    "QUARANTINE": 0.40,
}


def create_pg_sql_table_schema(pg_schema: str) -> CreatePgTableSql:
    return CreatePgTableSql(
        pg_schema=pg_schema,
        pg_table=STORAGE_LOCATIONS_TABLE_NAME,
        llm_description=(
            "Master list of physical bin locations. location_code follows "
            "WH{n}-{ZONE}-{AISLE}{RACK}-L{LEVEL}-B{BIN}. Zone constrains which SKU "
            "categories can be stored: COLD holds PERISH-prefixed SKUs only, HAZMAT "
            "holds HAZ-prefixed SKUs only, all other zones hold generic PROD SKUs. "
            "current_qty ≤ capacity always; overall utilization centers on 70–85%."
        ),
        pg_columns=[
            PgColumn(
                name="location_id",
                data_type="UUID",
                modifiers="PRIMARY KEY",
                llm_description="Unique identifier for the storage location.",
                llm_example_values="'a1b2c3d4-e5f6-7890-abcd-ef1234567890'",
            ),
            PgColumn(
                name="location_code",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description=(
                    "Human-readable bin code in WH{n}-{ZONE}-{AISLE}{RACK}-L{LEVEL}-B{BIN} "
                    "format. Not guaranteed unique across the table — multiple bins may "
                    "share components in a sparsely-sampled dataset."
                ),
                llm_example_values="'WH1-BULK-A01-L2-B04', 'WH2-COLD-C12-L1-B07'",
            ),
            PgColumn(
                name="warehouse",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Warehouse identifier. WH1 is the largest DC.",
                llm_example_values="'WH1', 'WH2', 'WH3'",
            ),
            PgColumn(
                name="zone",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description=(
                    "Storage zone. BULK ~40%, PICK ~30%, STAGING ~10%, COLD ~8%, "
                    "HAZMAT ~5%, RETURNS ~4%, QUARANTINE ~3%."
                ),
                llm_example_values="'BULK', 'PICK', 'COLD', 'HAZMAT'",
            ),
            PgColumn(
                name="aisle",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Aisle letter+number within the zone.",
                llm_example_values="'A01', 'C12', 'M07'",
            ),
            PgColumn(
                name="rack",
                data_type="INTEGER",
                modifiers="NOT NULL",
                llm_description="Rack position along the aisle.",
                llm_example_values="'1', '8', '15'",
            ),
            PgColumn(
                name="level",
                data_type="INTEGER",
                modifiers="NOT NULL",
                llm_description="Vertical level on the rack (1 = floor).",
                llm_example_values="'1', '2', '4'",
            ),
            PgColumn(
                name="bin",
                data_type="INTEGER",
                modifiers="NOT NULL",
                llm_description="Bin position on the level.",
                llm_example_values="'1', '6', '12'",
            ),
            PgColumn(
                name="sku",
                data_type="TEXT",
                modifiers="",
                llm_description=(
                    "SKU currently stored at this location, or NULL when empty. "
                    "Prefix matches zone: PERISH- for COLD, HAZ- for HAZMAT, otherwise PROD-."
                ),
                llm_example_values="'PROD-0012345', 'PERISH-0004001', 'HAZ-0000123', NULL",
            ),
            PgColumn(
                name="current_qty",
                data_type="INTEGER",
                modifiers="NOT NULL",
                llm_description="Units currently stored. 0 when sku IS NULL. Always ≤ capacity.",
                llm_example_values="'0', '180', '1450'",
            ),
            PgColumn(
                name="capacity",
                data_type="INTEGER",
                modifiers="NOT NULL",
                llm_description=(
                    "Maximum units this location can hold. Larger for BULK; smaller for PICK."
                ),
                llm_example_values="'150', '500', '1800'",
            ),
        ],
    )


def _sku_for_zone(zone: str, sku_index: int) -> str:
    if zone == "COLD":
        return f"PERISH-{sku_index:07d}"
    if zone == "HAZMAT":
        return f"HAZ-{sku_index:07d}"
    return f"PROD-{sku_index:07d}"


def _build_location_codes(
    warehouses: np.ndarray,
    zones: np.ndarray,
    aisles: np.ndarray,
    racks: np.ndarray,
    levels: np.ndarray,
    bins: np.ndarray,
) -> np.ndarray:
    return np.array(
        [
            f"{wh}-{z}-{a}{r:02d}-L{lv}-B{b:02d}"
            for wh, z, a, r, lv, b in zip(warehouses, zones, aisles, racks, levels, bins)
        ]
    )


def generate_storage_locations(n_samples: int) -> pd.DataFrame:
    rng = get_random_state()

    warehouses = rng.choice(_WAREHOUSES, p=_WAREHOUSE_WEIGHTS, size=n_samples)
    zones = rng.choice(_ZONES, p=_ZONE_WEIGHTS, size=n_samples)

    aisle_letters = np.array(list("ABCDEFGHJKLMNPQR"))
    aisles = rng.choice(aisle_letters, size=n_samples)
    racks = rng.randint(1, 16, size=n_samples)
    levels = rng.randint(1, 5, size=n_samples)
    bins = rng.randint(1, 13, size=n_samples)

    location_codes = _build_location_codes(warehouses, zones, aisles, racks, levels, bins)

    capacity = np.empty(n_samples, dtype=int)
    for zone, (lo, hi) in _ZONE_CAPACITY_RANGES.items():
        mask = zones == zone
        if mask.any():
            capacity[mask] = rng.randint(lo, hi + 1, size=int(mask.sum()))

    is_empty = np.zeros(n_samples, dtype=bool)
    for zone, empty_rate in _ZONE_EMPTY_RATE.items():
        mask = zones == zone
        if mask.any():
            is_empty[mask] = rng.random(size=int(mask.sum())) < empty_rate

    # Non-empty locations sit at 75–95% of capacity (mean ~85%); combined with empty-rate
    # mix this lands overall fill rate inside the 70–85% benchmark.
    utilization = rng.uniform(0.75, 0.95, size=n_samples)
    current_qty = np.floor(capacity * utilization).astype(int)
    current_qty[is_empty] = 0

    sku_indices = rng.randint(1, 50_000, size=n_samples)
    skus = np.array(
        [_sku_for_zone(z, idx) for z, idx in zip(zones, sku_indices)],
        dtype=object,
    )
    skus[is_empty] = None

    return pd.DataFrame(
        {
            "location_id": generate_n_random_uuids(n_samples),
            "location_code": location_codes,
            "warehouse": warehouses,
            "zone": zones,
            "aisle": aisles,
            "rack": racks,
            "level": levels,
            "bin": bins,
            "sku": skus,
            "current_qty": current_qty,
            "capacity": capacity,
        }
    )
