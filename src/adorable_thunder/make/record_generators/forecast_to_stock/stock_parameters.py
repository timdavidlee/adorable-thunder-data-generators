import numpy as np
import pandas as pd

from adorable_thunder.make.field_generators._random_state import get_random_state
from adorable_thunder.make.field_generators.country import generate_country_codes
from adorable_thunder.make.field_generators.identifiers import generate_n_random_uuids
from adorable_thunder.make.record_generators.schemas import CreatePgTableSql, PgColumn

_SUPPLIER_TYPES = np.array(["domestic", "international", "contract_manufacturer"])
_SUPPLIER_TYPE_WEIGHTS = np.array([0.60, 0.30, 0.10])

_EOQ_BUCKETS = np.array([50, 100, 250, 500, 1000, 2500])
_EOQ_WEIGHTS = np.array([0.20, 0.25, 0.20, 0.20, 0.10, 0.05])

STOCK_PARAMETERS_TABLE_NAME = "stock_parameters"


def create_pg_sql_table_schema(pg_schema: str) -> CreatePgTableSql:
    return CreatePgTableSql(
        pg_schema=pg_schema,
        pg_table=STOCK_PARAMETERS_TABLE_NAME,
        llm_description="Per-SKU/location replenishment parameters: safety stock, reorder point, EOQ, and lead time. Drives downstream forecasts, inventory positions, and replenishment orders. Lead times split: domestic 2–14d (~60%), international 14–90d (~30%), contract manufacturer 30–120d (~10%).",
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


def generate_stock_parameters(n_samples: int) -> pd.DataFrame:
    rng = get_random_state()

    avg_daily_demand = np.round(np.exp(rng.normal(loc=2.5, scale=1.2, size=n_samples)), 2)
    avg_daily_demand = np.clip(avg_daily_demand, 0.5, 2000.0)

    supplier_types = rng.choice(_SUPPLIER_TYPES, p=_SUPPLIER_TYPE_WEIGHTS, size=n_samples)
    lead_time_days = _sample_lead_time_days(supplier_types)

    safety_days = rng.randint(7, 29, size=n_samples)
    safety_stock_qty = np.ceil(avg_daily_demand * safety_days).astype(int)

    reorder_point = (np.ceil(avg_daily_demand * lead_time_days).astype(int) + safety_stock_qty).astype(int)
    economic_order_qty = rng.choice(_EOQ_BUCKETS, p=_EOQ_WEIGHTS, size=n_samples)

    skus = np.array([f"PROD-{i:07d}" for i in range(1, n_samples + 1)])

    return pd.DataFrame(
        {
            "param_id": generate_n_random_uuids(n_samples),
            "sku": skus,
            "location": generate_country_codes(n_samples),
            "avg_daily_demand": avg_daily_demand,
            "safety_stock_qty": safety_stock_qty,
            "reorder_point": reorder_point,
            "economic_order_qty": economic_order_qty,
            "lead_time_days": lead_time_days,
            "supplier_type": supplier_types,
        }
    )
