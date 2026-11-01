from typing import ClassVar

import pandas as pd

from adorable_thunder.make.record_generators.schemas import BaseGeneratorConfig

from .accounts import ACCOUNTS_TABLE_NAME, generate_accounts
from .branches import BRANCHES_TABLE_NAME, generate_branches
from .clients import CLIENTS_TABLE_NAME, generate_clients
from .loans import LOANS_TABLE_NAME, generate_loans
from .monthly_activity import MONTHLY_ACTIVITY_TABLE_NAME, generate_monthly_activity
from .plan_changes import PLAN_CHANGES_TABLE_NAME, generate_plan_changes
from .tariff_plans import TARIFF_PLANS_TABLE_NAME, generate_tariff_plans

FLOW_NAME = "onboard_to_offboard"


class GeneratorConfig(BaseGeneratorConfig):
    """n_samples is the number of clients."""

    name: ClassVar[str] = FLOW_NAME
    start_date: str = "2024-01-01"
    end_date: str = "2025-12-31"

    def make(self) -> dict[str, pd.DataFrame]:
        branches = generate_branches()
        tariff_plans = generate_tariff_plans()
        clients = generate_clients(self.n_samples, branches, self.end_date)
        accounts = generate_accounts(clients, self.start_date, self.end_date)
        plan_changes = generate_plan_changes(accounts)
        activity = generate_monthly_activity(accounts, clients, self.start_date, self.end_date)
        loans = generate_loans(clients, accounts, self.end_date)

        return {
            BRANCHES_TABLE_NAME: branches,
            TARIFF_PLANS_TABLE_NAME: tariff_plans,
            CLIENTS_TABLE_NAME: clients,
            ACCOUNTS_TABLE_NAME: accounts.drop(
                columns=["_is_primary", "_plan_history", "_dormant_from"]
            ),
            PLAN_CHANGES_TABLE_NAME: plan_changes,
            MONTHLY_ACTIVITY_TABLE_NAME: activity,
            LOANS_TABLE_NAME: loans,
        }
