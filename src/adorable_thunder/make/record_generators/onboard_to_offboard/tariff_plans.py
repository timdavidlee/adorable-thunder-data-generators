from datetime import date

import pandas as pd

from adorable_thunder.make.record_generators.schemas import CreatePgTableSql, PgColumn

FEE_INCREASE_ON = date(2025, 3, 1)
SMART_LAUNCH_ON = date(2025, 12, 1)

PLAN_NAMES: dict[str, str] = {
    "START": "Start",
    "BUSINESS": "Business",
    "PRO": "Pro",
    "TRADE": "Trade & FX",
    "AGRO": "Agro Seasonal",
    "SMART": "Smart",
}

# (plan_code, monthly_fee_kzt, effective_from, effective_to)
_PRICE_PERIODS: list[tuple[str, int, date, date | None]] = [
    ("START", 1_900, date(2015, 1, 1), None),
    ("BUSINESS", 4_900, date(2015, 1, 1), date(2025, 2, 28)),
    ("BUSINESS", 8_900, FEE_INCREASE_ON, None),
    ("PRO", 14_900, date(2015, 1, 1), None),
    ("TRADE", 11_900, date(2015, 1, 1), None),
    ("AGRO", 3_900, date(2018, 1, 1), None),
    ("SMART", 5_900, SMART_LAUNCH_ON, None),
]

TARIFF_PLANS_TABLE_NAME = "tariff_plans"


def create_pg_sql_table_schema(pg_schema: str) -> CreatePgTableSql:
    return CreatePgTableSql(
        pg_schema=pg_schema,
        pg_table=TARIFF_PLANS_TABLE_NAME,
        llm_description=(
            "Tariff plan price history: one row per plan per price period. BUSINESS rose from "
            "4,900 to 8,900 KZT on 2025-03-01; SMART launched 2025-12-01."
        ),
        pg_columns=[
            PgColumn(
                name="plan_code",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Plan code; repeats once per price period.",
                llm_example_values="'START', 'BUSINESS', 'PRO', 'TRADE', 'AGRO', 'SMART'",
            ),
            PgColumn(
                name="plan_name",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Customer-facing plan name.",
                llm_example_values="'Start', 'Trade & FX'",
            ),
            PgColumn(
                name="monthly_fee_kzt",
                data_type="INTEGER",
                modifiers="NOT NULL",
                llm_description="Monthly account fee in KZT during this period.",
                llm_example_values="'1900', '8900'",
            ),
            PgColumn(
                name="effective_from",
                data_type="DATE",
                modifiers="NOT NULL",
                llm_description="First day this price applies.",
                llm_example_values="'2015-01-01', '2025-03-01'",
            ),
            PgColumn(
                name="effective_to",
                data_type="DATE",
                modifiers="",
                llm_description="Last day this price applies; NULL for the current price.",
                llm_example_values="'2025-02-28', NULL",
            ),
        ],
    )


def generate_tariff_plans() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "plan_code": [code for code, _, _, _ in _PRICE_PERIODS],
            "plan_name": [PLAN_NAMES[code] for code, _, _, _ in _PRICE_PERIODS],
            "monthly_fee_kzt": [fee for _, fee, _, _ in _PRICE_PERIODS],
            "effective_from": [start for _, _, start, _ in _PRICE_PERIODS],
            "effective_to": [end for _, _, _, end in _PRICE_PERIODS],
        }
    )
