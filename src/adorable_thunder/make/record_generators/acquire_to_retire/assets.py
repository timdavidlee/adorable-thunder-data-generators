import numpy as np
import pandas as pd

from adorable_thunder.make.field_generators._random_state import get_random_state
from adorable_thunder.make.field_generators.cost_center import generate_cost_center_names
from adorable_thunder.make.field_generators.country import generate_country_codes
from adorable_thunder.make.field_generators.dates import generate_random_dates
from adorable_thunder.make.field_generators.identifiers import generate_n_random_uuids
from adorable_thunder.make.record_generators.schemas import CreatePgTableSql, PgColumn

ASSET_CLASSES = np.array(
    [
        "IT_EQUIPMENT",
        "OFFICE_FURNITURE",
        "VEHICLE",
        "LEASEHOLD_IMPROVEMENT",
        "BUILDING",
        "INTANGIBLE",
        "MACHINERY",
    ]
)
_CLASS_WEIGHTS = np.array([0.40, 0.15, 0.05, 0.05, 0.02, 0.13, 0.20])

# Lognormal cost params per class. mu/sigma chosen to land medians near typical
# enterprise capex tiers in the brief (laptops/servers ~$2.5k-$50k, machinery
# $50k-$2M, buildings $500k-$50M).
_CLASS_COST_PARAMS: dict[str, tuple[float, float, float, float]] = {
    "IT_EQUIPMENT": (8.5, 1.2, 2_500.0, 100_000.0),
    "OFFICE_FURNITURE": (8.0, 0.6, 2_500.0, 10_000.0),
    "VEHICLE": (10.5, 0.4, 20_000.0, 80_000.0),
    "LEASEHOLD_IMPROVEMENT": (10.5, 1.0, 10_000.0, 300_000.0),
    "BUILDING": (15.4, 1.0, 500_000.0, 50_000_000.0),
    "INTANGIBLE": (10.0, 1.3, 2_500.0, 500_000.0),
    "MACHINERY": (12.0, 1.0, 50_000.0, 2_000_000.0),
}

_CLASS_LIFE_RANGES: dict[str, tuple[int, int]] = {
    "IT_EQUIPMENT": (3, 5),
    "OFFICE_FURNITURE": (7, 10),
    "VEHICLE": (5, 5),
    "LEASEHOLD_IMPROVEMENT": (10, 10),
    "BUILDING": (30, 40),
    "INTANGIBLE": (3, 5),
    "MACHINERY": (5, 15),
}

_DESCRIPTIONS_BY_CLASS: dict[str, list[str]] = {
    "IT_EQUIPMENT": [
        "Laptop",
        "Desktop Workstation",
        "Rack Server",
        "Network Switch",
        "Storage Array",
        "Conference Room Display",
    ],
    "OFFICE_FURNITURE": [
        "Executive Desk",
        "Ergonomic Chair",
        "Conference Table",
        "Filing Cabinet",
        "Modular Workstation",
    ],
    "VEHICLE": [
        "Cargo Van",
        "Pickup Truck",
        "Sedan",
        "Forklift",
        "Service Truck",
    ],
    "LEASEHOLD_IMPROVEMENT": [
        "Office Buildout",
        "HVAC Upgrade",
        "Lab Fitout",
        "Floor Refurbishment",
    ],
    "BUILDING": [
        "Office Building",
        "Distribution Center",
        "Manufacturing Plant",
        "Lab Facility",
    ],
    "INTANGIBLE": [
        "ERP License",
        "CRM Platform License",
        "Patent Portfolio",
        "Internally Developed Software",
        "Trademark",
    ],
    "MACHINERY": [
        "CNC Machine",
        "Industrial Robot",
        "Injection Molder",
        "Packaging Line",
        "Assembly Conveyor",
    ],
}

# Methods skewed by class. Vehicles and machinery sometimes use accelerated methods;
# everything else is straight-line in practice.
_METHODS_BY_CLASS: dict[str, tuple[np.ndarray, np.ndarray]] = {
    "IT_EQUIPMENT": (np.array(["STRAIGHT_LINE"]), np.array([1.0])),
    "OFFICE_FURNITURE": (np.array(["STRAIGHT_LINE"]), np.array([1.0])),
    "VEHICLE": (
        np.array(["STRAIGHT_LINE", "DECLINING_BALANCE"]),
        np.array([0.6, 0.4]),
    ),
    "LEASEHOLD_IMPROVEMENT": (np.array(["STRAIGHT_LINE"]), np.array([1.0])),
    "BUILDING": (np.array(["STRAIGHT_LINE"]), np.array([1.0])),
    "INTANGIBLE": (np.array(["STRAIGHT_LINE"]), np.array([1.0])),
    "MACHINERY": (
        np.array(["STRAIGHT_LINE", "SUM_OF_YEARS"]),
        np.array([0.7, 0.3]),
    ),
}

# Salvage value as a fraction of cost. Most assets depreciate to zero; a minority
# carry a 10% floor (vehicles, machinery, buildings).
_SALVAGE_ZERO_RATE = 0.7

ASSETS_TABLE_NAME = "assets"


def create_pg_sql_table_schema(pg_schema: str) -> CreatePgTableSql:
    return CreatePgTableSql(
        pg_schema=pg_schema,
        pg_table=ASSETS_TABLE_NAME,
        llm_description=(
            "Asset master records — every capitalized fixed asset on the books. "
            "Cost is at or above the $2,500 capitalization threshold. useful_life_years "
            "depends on asset_class (IT 3-5, vehicles 5, buildings 30-40). status "
            "follows planned -> in_service -> fully_depreciated/disposed."
        ),
        pg_columns=[
            PgColumn(
                name="asset_id",
                data_type="UUID",
                modifiers="PRIMARY KEY",
                llm_description="Unique identifier for the asset.",
                llm_example_values="'a1b2c3d4-e5f6-7890-abcd-ef1234567890'",
            ),
            PgColumn(
                name="asset_class",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description=(
                    "Category determining useful life and depreciation method. "
                    "Distribution skews toward IT_EQUIPMENT (~40%) and MACHINERY (~20%)."
                ),
                llm_example_values=(
                    "'IT_EQUIPMENT', 'OFFICE_FURNITURE', 'VEHICLE', "
                    "'LEASEHOLD_IMPROVEMENT', 'BUILDING', 'INTANGIBLE', 'MACHINERY'"
                ),
            ),
            PgColumn(
                name="description",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Short human-readable description sampled per asset class.",
                llm_example_values="'Laptop', 'Rack Server', 'Industrial Robot'",
            ),
            PgColumn(
                name="acquisition_date",
                data_type="DATE",
                modifiers="NOT NULL",
                llm_description=(
                    "Date the asset was acquired. Spans up to ~15 years prior to dataset_end "
                    "so the portfolio includes a mix of fresh and aging assets."
                ),
                llm_example_values="'2018-04-15', '2024-10-01'",
            ),
            PgColumn(
                name="cost",
                data_type="NUMERIC(18, 2)",
                modifiers="NOT NULL",
                llm_description=(
                    "Acquisition cost in USD. Lognormal per asset_class; floored at the "
                    "$2,500 capitalization threshold."
                ),
                llm_example_values="'3500.00', '85000.00', '4200000.00'",
            ),
            PgColumn(
                name="useful_life_years",
                data_type="INTEGER",
                modifiers="NOT NULL",
                llm_description=(
                    "Expected useful life. IT 3-5; office furniture 7-10; vehicles 5; "
                    "leasehold improvements 10; buildings 30-40; intangibles 3-5; machinery 5-15."
                ),
                llm_example_values="'3', '10', '35'",
            ),
            PgColumn(
                name="depreciation_method",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description=(
                    "Depreciation method. STRAIGHT_LINE dominates; vehicles and machinery "
                    "occasionally use accelerated methods."
                ),
                llm_example_values="'STRAIGHT_LINE', 'DECLINING_BALANCE', 'SUM_OF_YEARS'",
            ),
            PgColumn(
                name="salvage_value",
                data_type="NUMERIC(18, 2)",
                modifiers="NOT NULL",
                llm_description=(
                    "Residual value at end of useful life. ~70% of assets depreciate to "
                    "$0; the rest carry a 10% salvage floor."
                ),
                llm_example_values="'0.00', '8500.00'",
            ),
            PgColumn(
                name="status",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description=(
                    "Lifecycle stage. planned (just acquired, not yet in service), "
                    "in_service (active and depreciating), fully_depreciated (reached "
                    "salvage but still active), disposed (retired)."
                ),
                llm_example_values="'planned', 'in_service', 'fully_depreciated', 'disposed'",
            ),
            PgColumn(
                name="location_country",
                data_type="VARCHAR(2)",
                modifiers="NOT NULL",
                llm_description=(
                    "ISO 3166-1 alpha-2 country code for the asset's physical location."
                ),
                llm_example_values="'US', 'DE', 'JP'",
            ),
            PgColumn(
                name="cost_center",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Cost center the asset is assigned to.",
                llm_example_values="'CC-1023 - Sales - North America SMB'",
            ),
        ],
    )


def _sample_costs(asset_classes: np.ndarray) -> np.ndarray:
    n = len(asset_classes)
    costs = np.empty(n, dtype=float)
    for cls, (mu, sigma, lo, hi) in _CLASS_COST_PARAMS.items():
        mask = asset_classes == cls
        if not mask.any():
            continue
        sample = get_random_state().lognormal(mean=mu, sigma=sigma, size=int(mask.sum()))
        costs[mask] = np.clip(sample, lo, hi)
    return np.round(costs, 2)


def _sample_useful_lives(asset_classes: np.ndarray) -> np.ndarray:
    n = len(asset_classes)
    lives = np.empty(n, dtype=int)
    for cls, (lo, hi) in _CLASS_LIFE_RANGES.items():
        mask = asset_classes == cls
        if not mask.any():
            continue
        if lo == hi:
            lives[mask] = lo
        else:
            lives[mask] = get_random_state().randint(lo, hi + 1, size=int(mask.sum()))
    return lives


def _sample_descriptions(asset_classes: np.ndarray) -> np.ndarray:
    descriptions = np.empty(len(asset_classes), dtype=object)
    for cls, options in _DESCRIPTIONS_BY_CLASS.items():
        mask = asset_classes == cls
        if not mask.any():
            continue
        descriptions[mask] = get_random_state().choice(options, size=int(mask.sum()))
    return descriptions


def _sample_methods(asset_classes: np.ndarray) -> np.ndarray:
    methods = np.empty(len(asset_classes), dtype=object)
    for cls, (options, weights) in _METHODS_BY_CLASS.items():
        mask = asset_classes == cls
        if not mask.any():
            continue
        methods[mask] = get_random_state().choice(options, p=weights, size=int(mask.sum()))
    return methods


def _assign_status(
    acquisition_dates: pd.Series, useful_life_years: np.ndarray, dataset_end: pd.Timestamp
) -> np.ndarray:
    """Status assignment driven by asset age vs. useful life so the distribution
    naturally yields the brief's expected mix."""
    age_days = (dataset_end - pd.to_datetime(acquisition_dates)).dt.days.to_numpy()
    life_days = useful_life_years * 365
    n = len(age_days)
    statuses = np.empty(n, dtype=object)

    very_recent = age_days < 60
    past_life = age_days > life_days

    # Recent acquisitions: 50% planned (still being commissioned), 50% in_service.
    statuses[very_recent] = np.where(
        get_random_state().random(int(very_recent.sum())) < 0.5, "planned", "in_service"
    )

    # Past-useful-life: most are still in use but with book value at salvage floor.
    # Brief target: ~15% fully_depreciated and ~7% disposed across the whole portfolio.
    past_count = int(past_life.sum())
    if past_count:
        statuses[past_life] = get_random_state().choice(
            ["in_service", "fully_depreciated", "disposed"],
            p=[0.65, 0.25, 0.10],
            size=past_count,
        )

    middle = ~very_recent & ~past_life
    middle_count = int(middle.sum())
    if middle_count:
        statuses[middle] = get_random_state().choice(
            ["in_service", "disposed"], p=[0.95, 0.05], size=middle_count
        )

    return statuses


def generate_assets(
    n_samples: int,
    start_date: str = "2024-01-01",
    end_date: str = "2025-12-31",
) -> pd.DataFrame:
    asset_classes = get_random_state().choice(ASSET_CLASSES, p=_CLASS_WEIGHTS, size=n_samples)
    descriptions = _sample_descriptions(asset_classes)
    costs = _sample_costs(asset_classes)
    useful_lives = _sample_useful_lives(asset_classes)
    methods = _sample_methods(asset_classes)

    salvage_zero = get_random_state().random(n_samples) < _SALVAGE_ZERO_RATE
    salvage_values = np.where(salvage_zero, 0.0, np.round(costs * 0.10, 2))

    # Wide acquisition window — buildings and intangibles need decade-old origins
    # to produce a realistic mix of fully-depreciated and active portfolios.
    acquisition_window_start = (
        pd.Timestamp(end_date) - pd.Timedelta(days=15 * 365)
    ).strftime("%Y-%m-%d")
    acquisition_dates = generate_random_dates(acquisition_window_start, end_date, n_samples)

    statuses = _assign_status(acquisition_dates, useful_lives, pd.Timestamp(end_date))

    return pd.DataFrame(
        {
            "asset_id": generate_n_random_uuids(n_samples),
            "asset_class": asset_classes,
            "description": descriptions,
            "acquisition_date": acquisition_dates.dt.date,
            "cost": costs,
            "useful_life_years": useful_lives,
            "depreciation_method": methods,
            "salvage_value": salvage_values,
            "status": statuses,
            "location_country": generate_country_codes(n_samples),
            "cost_center": generate_cost_center_names(n_samples),
        }
    )
