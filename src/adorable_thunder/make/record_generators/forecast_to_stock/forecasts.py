import numpy as np
import pandas as pd

from adorable_thunder.make.field_generators._random_state import get_random_state
from adorable_thunder.make.field_generators.dates import generate_random_dates
from adorable_thunder.make.field_generators.identifiers import generate_n_random_uuids
from adorable_thunder.make.record_generators.schemas import CreatePgTableSql, PgColumn

_MODELS = np.array(["statistical", "manual", "consensus"])
_MODEL_WEIGHTS = np.array([0.60, 0.15, 0.25])

_FORECASTS_PER_SKU = 4

FORECASTS_TABLE_NAME = "forecasts"


def create_pg_sql_table_schema(pg_schema: str) -> CreatePgTableSql:
    return CreatePgTableSql(
        pg_schema=pg_schema,
        pg_table=FORECASTS_TABLE_NAME,
        llm_description="Per-SKU monthly demand forecasts. Quantity centers on avg_daily_demand × ~30 days with realistic noise (±25%). Model mix: statistical ~60%, consensus ~25%, manual ~15%.",
        pg_columns=[
            PgColumn(
                name="forecast_id",
                data_type="UUID",
                modifiers="PRIMARY KEY",
                llm_description="Unique identifier for the forecast row.",
                llm_example_values="'b2c3d4e5-f6a7-8901-bcde-f12345678901'",
            ),
            PgColumn(
                name="sku",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="SKU this forecast covers. Joins to stock_parameters.sku.",
                llm_example_values="'PROD-0012345', 'SKU-0067890'",
            ),
            PgColumn(
                name="period",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Fiscal month period the forecast applies to.",
                llm_example_values="'FY2025-P03', 'FY2025-P11'",
            ),
            PgColumn(
                name="forecast_qty",
                data_type="INTEGER",
                modifiers="NOT NULL",
                llm_description="Forecast demand units for the period. Roughly avg_daily_demand × 30 with ±25% noise.",
                llm_example_values="'375', '2550', '9600'",
            ),
            PgColumn(
                name="uom",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Unit of measure for the forecast quantity. Count UOMs (EA, CASE, PALLET).",
                llm_example_values="'EA', 'CASE', 'PALLET'",
            ),
            PgColumn(
                name="model",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Forecast generation model. Distribution: statistical ~60%, consensus ~25%, manual ~15%.",
                llm_example_values="'statistical', 'manual', 'consensus'",
            ),
            PgColumn(
                name="created_date",
                data_type="DATE",
                modifiers="NOT NULL",
                llm_description="Date the forecast was generated.",
                llm_example_values="'2024-03-01', '2025-09-15'",
            ),
        ],
    )


def _sample_uoms_per_sku(n_skus: int) -> np.ndarray:
    rng = get_random_state()
    return rng.choice(np.array(["EA", "CASE", "PALLET"]), p=[0.70, 0.25, 0.05], size=n_skus)


def _build_periods(n_skus: int) -> np.ndarray:
    rng = get_random_state()
    years = rng.randint(2024, 2026, size=n_skus * _FORECASTS_PER_SKU)
    months = rng.randint(1, 13, size=n_skus * _FORECASTS_PER_SKU)
    return np.array([f"FY{y}-P{m:02d}" for y, m in zip(years, months)])


def generate_forecasts(
    skus: np.ndarray,
    avg_daily_demand: np.ndarray,
    start_date: str = "2024-01-01",
    end_date: str = "2025-12-31",
) -> pd.DataFrame:
    rng = get_random_state()
    n_skus = len(skus)
    n_rows = n_skus * _FORECASTS_PER_SKU

    repeated_skus = np.repeat(skus, _FORECASTS_PER_SKU)
    repeated_demand = np.repeat(avg_daily_demand, _FORECASTS_PER_SKU)
    repeated_uoms = np.repeat(_sample_uoms_per_sku(n_skus), _FORECASTS_PER_SKU)

    noise = rng.uniform(0.75, 1.25, size=n_rows)
    forecast_qty = np.ceil(repeated_demand * 30 * noise).astype(int)

    return pd.DataFrame(
        {
            "forecast_id": generate_n_random_uuids(n_rows),
            "sku": repeated_skus,
            "period": _build_periods(n_skus),
            "forecast_qty": forecast_qty,
            "uom": repeated_uoms,
            "model": rng.choice(_MODELS, p=_MODEL_WEIGHTS, size=n_rows),
            "created_date": generate_random_dates(start_date, end_date, n_rows),
        }
    )
