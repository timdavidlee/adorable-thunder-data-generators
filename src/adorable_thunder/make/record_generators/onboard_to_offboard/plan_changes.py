from datetime import date

import pandas as pd

from adorable_thunder.make.record_generators.schemas import CreatePgTableSql, PgColumn

PLAN_CHANGES_TABLE_NAME = "plan_changes"


def create_pg_sql_table_schema(pg_schema: str) -> CreatePgTableSql:
    return CreatePgTableSql(
        pg_schema=pg_schema,
        pg_table=PLAN_CHANGES_TABLE_NAME,
        llm_description=(
            "Tariff plan changes per account. Changes chain: to_plan of one is from_plan of the "
            "next, and the last to_plan is the account's current plan_code."
        ),
        pg_columns=[
            PgColumn(
                name="plan_change_id",
                data_type="TEXT",
                modifiers="PRIMARY KEY",
                llm_description="Plan change number.",
                llm_example_values="'PC-000001'",
            ),
            PgColumn(
                name="account_id",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="FK to accounts.",
                llm_example_values="'AC-0000042'",
            ),
            PgColumn(
                name="changed_on",
                data_type="DATE",
                modifiers="NOT NULL",
                llm_description="Date the new plan took effect; within the account's open window.",
                llm_example_values="'2025-04-17'",
            ),
            PgColumn(
                name="from_plan",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Plan before the change.",
                llm_example_values="'BUSINESS'",
            ),
            PgColumn(
                name="to_plan",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Plan after the change.",
                llm_example_values="'START', 'SMART'",
            ),
        ],
    )


def generate_plan_changes(accounts: pd.DataFrame) -> pd.DataFrame:
    rows: list[tuple[str, date, str, str]] = []
    for account_id, history in zip(accounts["account_id"], accounts["_plan_history"], strict=True):
        for changed_on, from_plan, to_plan in history:
            rows.append((str(account_id), changed_on, from_plan, to_plan))
    rows.sort(key=lambda row: (row[1], row[0]))
    return pd.DataFrame(
        {
            "plan_change_id": [f"PC-{i:06d}" for i in range(1, len(rows) + 1)],
            "account_id": [row[0] for row in rows],
            "changed_on": [row[1] for row in rows],
            "from_plan": [row[2] for row in rows],
            "to_plan": [row[3] for row in rows],
        }
    )
