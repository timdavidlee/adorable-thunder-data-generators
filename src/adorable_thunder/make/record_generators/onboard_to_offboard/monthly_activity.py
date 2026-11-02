from datetime import date

import pandas as pd

from adorable_thunder.make.field_generators._random_state import get_random_state
from adorable_thunder.make.record_generators.schemas import CreatePgTableSql, PgColumn

# Medians by segment: average balance (KZT), transactions per month, average ticket (KZT)
_MEDIAN_BALANCE = {"micro": 300_000, "small": 2_500_000, "medium": 20_000_000}
_MEDIAN_TXNS = {"micro": 25, "small": 80, "medium": 300}
_MEDIAN_TICKET = {"micro": 40_000, "small": 120_000, "medium": 400_000}
_AGRO_SEASON = range(4, 11)
_WIND_DOWN = {2: 0.5, 1: 0.25, 0: 0.15}  # months before closure → activity multiplier

MONTHLY_ACTIVITY_TABLE_NAME = "monthly_activity"


def create_pg_sql_table_schema(pg_schema: str) -> CreatePgTableSql:
    return CreatePgTableSql(
        pg_schema=pg_schema,
        pg_table=MONTHLY_ACTIVITY_TABLE_NAME,
        llm_description=(
            "One row per account per month it was open within the dataset window. Dormant "
            "accounts have txn_count = 0 while still open."
        ),
        pg_columns=[
            PgColumn(
                name="account_id",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="FK to accounts.",
                llm_example_values="'AC-0000042'",
            ),
            PgColumn(
                name="month",
                data_type="DATE",
                modifiers="NOT NULL",
                llm_description="First day of the month.",
                llm_example_values="'2025-04-01'",
            ),
            PgColumn(
                name="avg_balance_kzt",
                data_type="NUMERIC(18, 2)",
                modifiers="NOT NULL",
                llm_description="Average daily balance, in KZT (FX accounts converted).",
                llm_example_values="'284310.55', '21500000.00'",
            ),
            PgColumn(
                name="txn_count",
                data_type="INTEGER",
                modifiers="NOT NULL",
                llm_description="Number of debit and credit transactions in the month.",
                llm_example_values="'0', '23', '310'",
            ),
            PgColumn(
                name="txn_volume_kzt",
                data_type="NUMERIC(18, 2)",
                modifiers="NOT NULL",
                llm_description="Total transaction value in KZT; 0 when txn_count is 0.",
                llm_example_values="'0.00', '1043200.00'",
            ),
        ],
    )


def _months_between(first: date, last: date) -> int:
    return (last.year - first.year) * 12 + last.month - first.month


def generate_monthly_activity(
    accounts: pd.DataFrame, clients: pd.DataFrame, start_date: str, end_date: str
) -> pd.DataFrame:
    rng = get_random_state()
    start, end = date.fromisoformat(start_date), date.fromisoformat(end_date)
    window_months = [
        date(start.year + (start.month - 1 + i) // 12, (start.month - 1 + i) % 12 + 1, 1)
        for i in range(_months_between(start, end) + 1)
    ]
    client_info = clients.set_index("client_id")[["segment", "industry"]].to_dict("index")
    rows: list[tuple[str, date, float, int, float]] = []
    columns = ["account_id", "client_id", "currency", "opened_on", "closed_on", "_dormant_from"]
    for account_id, client_id, currency, opened, closed, dormant_from in zip(
        *(accounts[c].tolist() for c in columns), strict=True
    ):
        info = client_info[client_id]
        segment, industry = str(info["segment"]), str(info["industry"])
        if pd.isna(closed):
            closed = None
        if pd.isna(dormant_from):
            dormant_from = None
        size = float(rng.lognormal(0.0, 0.6))
        fx_factor = 0.5 if currency != "KZT" else 1.0
        balance = _MEDIAN_BALANCE[segment] * size * fx_factor
        for month in window_months:
            if month < opened.replace(day=1) or (
                closed is not None and month > closed.replace(day=1)
            ):
                continue
            if dormant_from is not None and month >= dormant_from:
                balance *= 0.98
                rows.append((account_id, month, round(balance, 2), 0, 0.0))
                continue
            factor = 1.0
            if closed is not None:
                factor = _WIND_DOWN.get(_months_between(month, closed), 1.0)
            if industry == "agriculture":
                factor *= 1.6 if month.month in _AGRO_SEASON else 0.5
            balance = _MEDIAN_BALANCE[segment] * size * fx_factor * float(rng.lognormal(0, 0.25))
            balance *= factor if closed is not None and factor < 1 else 1.0
            expected_txns = _MEDIAN_TXNS[segment] * size**0.5 * factor * fx_factor
            txns = int(rng.poisson(expected_txns, size=1)[0])
            ticket = _MEDIAN_TICKET[segment] * float(rng.lognormal(0, 0.3))
            volume = round(txns * ticket, 2)
            rows.append((account_id, month, round(balance, 2), txns, volume))
    return pd.DataFrame(
        rows, columns=["account_id", "month", "avg_balance_kzt", "txn_count", "txn_volume_kzt"]
    )
