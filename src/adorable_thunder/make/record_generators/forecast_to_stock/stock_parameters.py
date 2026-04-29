import numpy as np
import pandas as pd

from adorable_thunder.make.field_generators._random_state import get_random_state
from adorable_thunder.make.field_generators.country import generate_country_codes
from adorable_thunder.make.field_generators.identifiers import generate_n_random_uuids
from adorable_thunder.make.record_generators.schemas import CreatePgTableSql, PgColumn
from adorable_thunder.make.reference_data.company_names import COMPANY_NAMES

_SUPPLIER_TYPES = np.array(["domestic", "international", "contract_manufacturer"])
_SUPPLIER_TYPE_WEIGHTS = np.array([0.60, 0.30, 0.10])

_EOQ_BUCKETS = np.array([50, 100, 250, 500, 1000, 2500])
_EOQ_WEIGHTS = np.array([0.20, 0.25, 0.20, 0.20, 0.10, 0.05])

_PRODUCT_CATEGORIES = np.array(
    [
        "Electronics",
        "Industrial",
        "Office Supplies",
        "Raw Materials",
        "Apparel",
        "Food & Beverage",
        "Tools",
        "Pharma",
        "Auto Parts",
        "Home Goods",
    ]
)
_PRODUCT_CATEGORY_WEIGHTS = np.array(
    [0.15, 0.15, 0.10, 0.12, 0.10, 0.10, 0.08, 0.08, 0.07, 0.05]
)

_ABC_CLASSES = np.array(["A", "B", "C"])
_ABC_WEIGHTS = np.array([0.20, 0.30, 0.50])

_N_SUPPLIERS = 150

STOCK_PARAMETERS_TABLE_NAME = "stock_parameters"


def create_pg_sql_table_schema(pg_schema: str) -> CreatePgTableSql:
    return CreatePgTableSql(
        pg_schema=pg_schema,
        pg_table=STOCK_PARAMETERS_TABLE_NAME,
        llm_description="Per-SKU/location replenishment parameters: safety stock, reorder point, EOQ, lead time, supplier identity, product category, ABC class, and unit cost. Drives downstream forecasts, inventory positions, and replenishment orders. Lead times split: domestic 2–14d (~60%), international 14–90d (~30%), contract manufacturer 30–120d (~10%). ABC mix ~20/30/50; unit cost scaled by class.",
        pg_columns=[
            PgColumn(
                name="param_id",
                data_type="UUID",
                modifiers="PRIMARY KEY",
                llm_description="Unique identifier for this SKU/location parameter row.",
                llm_example_values="'a1b2c3d4-e5f6-7890-abcd-ef1234567890'",
            ),
            PgColumn(
                name="sku",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Stock-keeping unit identifier with category prefix.",
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
                name="product_category",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="High-level product category for analytics segmentation.",
                llm_example_values="'Electronics', 'Industrial', 'Apparel', 'Pharma'",
            ),
            PgColumn(
                name="abc_class",
                data_type="VARCHAR(1)",
                modifiers="NOT NULL",
                llm_description="ABC inventory classification — A (~20% top value/velocity), B (~30%), C (~50%). Drives differentiated replenishment policy.",
                llm_example_values="'A', 'B', 'C'",
            ),
            PgColumn(
                name="unit_cost_usd",
                data_type="NUMERIC(10, 2)",
                modifiers="NOT NULL",
                llm_description="Unit cost in USD. Scaled by ABC class — A items higher cost, C items lower. Drives inventory_value_usd downstream.",
                llm_example_values="'1.25', '42.50', '850.00'",
            ),
            PgColumn(
                name="supplier_id",
                data_type="UUID",
                modifiers="NOT NULL",
                llm_description="Stable supplier identifier; ~150 distinct suppliers across the dataset, partitioned by supplier_type.",
                llm_example_values="'7f3e8a91-2b4c-4d5e-9f01-23456789abcd'",
            ),
            PgColumn(
                name="supplier_name",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Human-readable supplier name; deterministically paired with supplier_id.",
                llm_example_values="'Arcoven Systems', 'Vortex Industrial', 'Quorum Finance'",
            ),
            PgColumn(
                name="avg_daily_demand",
                data_type="NUMERIC(10, 2)",
                modifiers="NOT NULL",
                llm_description="Smoothed average daily demand (units/day). Drives reorder point and forecast scaling.",
                llm_example_values="'12.50', '85.00', '320.75'",
            ),
            PgColumn(
                name="safety_stock_qty",
                data_type="INTEGER",
                modifiers="NOT NULL",
                llm_description="Buffer stock units sized to cover 7–28 days of average demand.",
                llm_example_values="'150', '850', '4500'",
            ),
            PgColumn(
                name="reorder_point",
                data_type="INTEGER",
                modifiers="NOT NULL",
                llm_description="Available-qty threshold that triggers replenishment. Equals avg_daily_demand × lead_time_days + safety_stock_qty.",
                llm_example_values="'320', '1700', '9500'",
            ),
            PgColumn(
                name="economic_order_qty",
                data_type="INTEGER",
                modifiers="NOT NULL",
                llm_description="Standard pack/order multiple — 50, 100, 250, 500, 1000, or 2500 units.",
                llm_example_values="'100', '500', '1000'",
            ),
            PgColumn(
                name="lead_time_days",
                data_type="INTEGER",
                modifiers="NOT NULL",
                llm_description="Supplier lead time in days. Domestic 2–14, international 14–90, contract manufacturer 30–120.",
                llm_example_values="'7', '45', '90'",
            ),
            PgColumn(
                name="supplier_type",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Supplier sourcing tier — domestic ~60%, international ~30%, contract_manufacturer ~10%.",
                llm_example_values="'domestic', 'international', 'contract_manufacturer'",
            ),
        ],
    )


def _sample_lead_time_days(supplier_types: np.ndarray) -> np.ndarray:
    rng = get_random_state()
    n = len(supplier_types)
    out = np.empty(n, dtype=int)
    domestic = supplier_types == "domestic"
    international = supplier_types == "international"
    contract = supplier_types == "contract_manufacturer"
    out[domestic] = rng.randint(2, 15, size=domestic.sum())
    out[international] = rng.randint(14, 91, size=international.sum())
    out[contract] = rng.randint(30, 121, size=contract.sum())
    return out


def _build_supplier_pool() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rng = get_random_state()
    names = rng.choice(np.array(COMPANY_NAMES), size=_N_SUPPLIERS, replace=False)
    types = rng.choice(_SUPPLIER_TYPES, p=_SUPPLIER_TYPE_WEIGHTS, size=_N_SUPPLIERS)
    ids = generate_n_random_uuids(_N_SUPPLIERS)
    return ids, names, types


def _assign_suppliers(supplier_types: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    rng = get_random_state()
    pool_ids, pool_names, pool_types = _build_supplier_pool()
    n = len(supplier_types)
    ids_out = np.empty(n, dtype=object)
    names_out = np.empty(n, dtype=object)
    for stype in _SUPPLIER_TYPES:
        mask = supplier_types == stype
        if not mask.any():
            continue
        cand_mask = pool_types == stype
        if not cand_mask.any():
            cand_mask = np.ones_like(pool_types, dtype=bool)
        cand_ids = pool_ids[cand_mask]
        cand_names = pool_names[cand_mask]
        picks = rng.randint(0, len(cand_ids), size=int(mask.sum()))
        ids_out[mask] = cand_ids[picks]
        names_out[mask] = cand_names[picks]
    return ids_out, names_out


def _sample_unit_cost_by_abc(abc_class: np.ndarray) -> np.ndarray:
    rng = get_random_state()
    n = len(abc_class)
    out = np.empty(n, dtype=float)
    a_mask = abc_class == "A"
    b_mask = abc_class == "B"
    c_mask = abc_class == "C"
    out[a_mask] = np.clip(rng.lognormal(mean=5.0, sigma=0.8, size=int(a_mask.sum())), 20.0, 5000.0)
    out[b_mask] = np.clip(rng.lognormal(mean=3.0, sigma=1.0, size=int(b_mask.sum())), 2.0, 500.0)
    out[c_mask] = np.clip(rng.lognormal(mean=1.0, sigma=1.0, size=int(c_mask.sum())), 0.10, 50.0)
    return np.round(out, 2)


def generate_stock_parameters(n_samples: int) -> pd.DataFrame:
    rng = get_random_state()

    avg_daily_demand = np.round(np.exp(rng.normal(loc=2.5, scale=1.2, size=n_samples)), 2)
    avg_daily_demand = np.clip(avg_daily_demand, 0.5, 2000.0)

    supplier_types = rng.choice(_SUPPLIER_TYPES, p=_SUPPLIER_TYPE_WEIGHTS, size=n_samples)
    lead_time_days = _sample_lead_time_days(supplier_types)

    safety_days = rng.randint(7, 29, size=n_samples)
    safety_stock_qty = np.ceil(avg_daily_demand * safety_days).astype(int)

    reorder_point = (
        np.ceil(avg_daily_demand * lead_time_days).astype(int) + safety_stock_qty
    ).astype(int)
    economic_order_qty = rng.choice(_EOQ_BUCKETS, p=_EOQ_WEIGHTS, size=n_samples)

    skus = np.array([f"PROD-{i:07d}" for i in range(1, n_samples + 1)])

    abc_class = rng.choice(_ABC_CLASSES, p=_ABC_WEIGHTS, size=n_samples)
    unit_cost_usd = _sample_unit_cost_by_abc(abc_class)
    product_category = rng.choice(
        _PRODUCT_CATEGORIES, p=_PRODUCT_CATEGORY_WEIGHTS, size=n_samples
    )

    supplier_ids, supplier_names = _assign_suppliers(supplier_types)

    return pd.DataFrame(
        {
            "param_id": generate_n_random_uuids(n_samples),
            "sku": skus,
            "location": generate_country_codes(n_samples),
            "product_category": product_category,
            "abc_class": abc_class,
            "unit_cost_usd": unit_cost_usd,
            "supplier_id": supplier_ids,
            "supplier_name": supplier_names,
            "avg_daily_demand": avg_daily_demand,
            "safety_stock_qty": safety_stock_qty,
            "reorder_point": reorder_point,
            "economic_order_qty": economic_order_qty,
            "lead_time_days": lead_time_days,
            "supplier_type": supplier_types,
        }
    )
