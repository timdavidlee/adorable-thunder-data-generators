from typing import ClassVar

import pandas as pd

from adorable_thunder.make.record_generators.schemas import BaseGeneratorConfig

from .assets import ASSETS_TABLE_NAME, generate_assets
from .depreciation_runs import DEPRECIATION_RUNS_TABLE_NAME, generate_depreciation_runs
from .disposals import DISPOSALS_TABLE_NAME, generate_disposals

FLOW_NAME = "acquire_to_retire"


class GeneratorConfig(BaseGeneratorConfig):
    name: ClassVar[str] = FLOW_NAME
    start_date: str = "2024-01-01"
    end_date: str = "2025-12-31"

    def make(self) -> dict[str, pd.DataFrame]:
        assets = generate_assets(self.n_samples, self.start_date, self.end_date)
        disposals = generate_disposals(assets, self.end_date)
        runs = generate_depreciation_runs(assets, self.end_date, disposals=disposals)

        return {
            ASSETS_TABLE_NAME: assets,
            DEPRECIATION_RUNS_TABLE_NAME: runs,
            DISPOSALS_TABLE_NAME: disposals,
        }
