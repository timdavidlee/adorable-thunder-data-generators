from typing import ClassVar

import pandas as pd

from adorable_thunder.make.record_generators.schemas import BaseGeneratorConfig

from .accounts import ACCOUNTS_TABLE_NAME, generate_accounts
from .activation_events import ACTIVATION_EVENTS_TABLE_NAME, generate_activation_events
from .iap_purchases import IAP_PURCHASES_TABLE_NAME, generate_iap_purchases
from .installs import INSTALLS_TABLE_NAME, generate_installs
from .retention_snapshots import (
    RETENTION_SNAPSHOTS_TABLE_NAME,
    generate_retention_snapshots,
)

FLOW_NAME = "install_to_retention"

_INTERNAL_INSTALL_COLS = [
    "_has_first_open",
    "_tutorial_completed",
    "_has_account",
    "_retained_d1",
    "_retained_d7",
    "_retained_d30",
    "_is_payer",
]


class GeneratorConfig(BaseGeneratorConfig):
    name: ClassVar[str] = FLOW_NAME
    start_date: str = "2024-01-01"
    end_date: str = "2025-12-31"

    def make(self) -> dict[str, pd.DataFrame]:
        installs = generate_installs(self.n_samples, self.start_date, self.end_date)
        accounts = generate_accounts(installs)
        events = generate_activation_events(installs)
        iaps = generate_iap_purchases(installs, self.end_date)
        snapshots = generate_retention_snapshots(installs)

        return {
            INSTALLS_TABLE_NAME: installs.drop(columns=_INTERNAL_INSTALL_COLS),
            ACCOUNTS_TABLE_NAME: accounts,
            ACTIVATION_EVENTS_TABLE_NAME: events,
            IAP_PURCHASES_TABLE_NAME: iaps,
            RETENTION_SNAPSHOTS_TABLE_NAME: snapshots,
        }
