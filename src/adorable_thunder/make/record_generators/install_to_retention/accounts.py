import numpy as np
import pandas as pd

from adorable_thunder.make.field_generators._random_state import get_random_state
from adorable_thunder.make.field_generators.identifiers import generate_n_random_uuids
from adorable_thunder.make.record_generators.schemas import CreatePgTableSql, PgColumn

_SIGNUP_METHODS = np.array(["email", "google", "apple", "phone"])
_SIGNUP_METHOD_WEIGHTS = np.array([0.45, 0.30, 0.20, 0.05])

ACCOUNTS_TABLE_NAME = "accounts"


def create_pg_sql_table_schema(pg_schema: str) -> CreatePgTableSql:
    return CreatePgTableSql(
        pg_schema=pg_schema,
        pg_table=ACCOUNTS_TABLE_NAME,
        llm_description=(
            "User accounts created after install. Generated only for installs that opened "
            "the app and chose to register (~70% of first-opens). created_at is on or after "
            "first_open_at — accounts cannot be created before the app is opened."
        ),
        pg_columns=[
            PgColumn(
                name="account_id",
                data_type="UUID",
                modifiers="PRIMARY KEY",
                llm_description="Unique identifier for the account.",
                llm_example_values="'b2c3d4e5-f6a7-8901-bcde-f23456789012'",
            ),
            PgColumn(
                name="install_id",
                data_type="UUID",
                modifiers="NOT NULL",
                llm_description="Foreign key to the originating install.",
                llm_example_values="'a1b2c3d4-e5f6-7890-abcd-ef1234567890'",
            ),
            PgColumn(
                name="user_id",
                data_type="UUID",
                modifiers="NOT NULL",
                llm_description="Stable user identifier; persists across reinstalls.",
                llm_example_values="'c3d4e5f6-a7b8-9012-cdef-345678901234'",
            ),
            PgColumn(
                name="signup_method",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description=(
                    "Authentication method used at signup. email ~45%, google ~30%, "
                    "apple ~20%, phone ~5%."
                ),
                llm_example_values="'email', 'google', 'apple', 'phone'",
            ),
            PgColumn(
                name="created_at",
                data_type="DATE",
                modifiers="NOT NULL",
                llm_description="Date the account was created. Within 0–2 days of first_open_at.",
                llm_example_values="'2024-02-02', '2025-06-15'",
            ),
        ],
    )


def generate_accounts(installs: pd.DataFrame) -> pd.DataFrame:
    acct_installs = installs[installs["_has_account"]].reset_index(drop=True)
    n = len(acct_installs)
    if n == 0:
        return pd.DataFrame(
            columns=["account_id", "install_id", "user_id", "signup_method", "created_at"]
        )

    first_open = pd.to_datetime(acct_installs["first_open_at"])
    offsets = get_random_state().randint(0, 3, size=n)
    created_at = first_open + pd.to_timedelta(offsets, unit="D")

    return pd.DataFrame(
        {
            "account_id": generate_n_random_uuids(n),
            "install_id": acct_installs["install_id"].to_numpy(),
            "user_id": generate_n_random_uuids(n),
            "signup_method": get_random_state().choice(
                _SIGNUP_METHODS, p=_SIGNUP_METHOD_WEIGHTS, size=n
            ),
            "created_at": created_at,
        }
    )
