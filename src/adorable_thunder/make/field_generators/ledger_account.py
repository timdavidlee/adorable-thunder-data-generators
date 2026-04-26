import numpy as np
import pandas as pd

from adorable_thunder.make.field_generators._random_state import get_random_state
from adorable_thunder.make.reference_data.ledger_accounts import (
    ASSET_ACCOUNTS,
    COGS_ACCOUNTS,
    EQUITY_ACCOUNTS,
    GENERAL_LEDGER_ACCOUNTS,
    LIABILITY_ACCOUNTS,
    OPEX_ACCOUNTS,
    OTHER_INCOME_EXPENSE_ACCOUNTS,
    REVENUE_ACCOUNTS,
)

_ACCOUNT_POOLS = {
    "asset": ASSET_ACCOUNTS,
    "liability": LIABILITY_ACCOUNTS,
    "equity": EQUITY_ACCOUNTS,
    "revenue": REVENUE_ACCOUNTS,
    "cogs": COGS_ACCOUNTS,
    "opex": OPEX_ACCOUNTS,
    "other": OTHER_INCOME_EXPENSE_ACCOUNTS,
}


def generate_ledger_accounts(
    n_samples: int,
    account_type: str | None = None,
) -> pd.DataFrame:
    """Sample GL accounts. Pass account_type to restrict to 'asset', 'liability',
    'equity', 'revenue', 'cogs', 'opex', or 'other'. Returns account_code + account_name."""
    pool = (
        _ACCOUNT_POOLS.get(account_type, GENERAL_LEDGER_ACCOUNTS)
        if account_type
        else GENERAL_LEDGER_ACCOUNTS
    )
    indices: list[int] = get_random_state().randint(0, len(pool), size=n_samples).tolist()
    return pd.DataFrame([pool[i] for i in indices], columns=["account_code", "account_name"])
