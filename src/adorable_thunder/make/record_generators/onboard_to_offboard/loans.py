from datetime import date, timedelta

import pandas as pd

from adorable_thunder.make.field_generators._random_state import get_random_state
from adorable_thunder.make.record_generators.schemas import CreatePgTableSql, PgColumn

_LOAN_SHARE = 0.25
_FX_SHARE = 0.12
_DEFAULT_RATE = 0.04
_EARLY_REPAY_RATE = 0.15
_KZT_PER_USD = 470.0
_MEDIAN_PRINCIPAL_KZT = {"micro": 3_000_000, "small": 15_000_000, "medium": 80_000_000}
_TERMS = [12, 24, 36]
_TERM_WEIGHTS = [0.40, 0.35, 0.25]
_LOAN_BOOK_START = date(2022, 1, 1)

LOANS_TABLE_NAME = "loans"


def create_pg_sql_table_schema(pg_schema: str) -> CreatePgTableSql:
    return CreatePgTableSql(
        pg_schema=pg_schema,
        pg_table=LOANS_TABLE_NAME,
        llm_description=(
            "Business loans to clients. ~12% are in USD at lower rates than KZT loans. Loans of "
            "clients who leave the bank are repaid on exit."
        ),
        pg_columns=[
            PgColumn(
                name="loan_id",
                data_type="TEXT",
                modifiers="PRIMARY KEY",
                llm_description="Loan number.",
                llm_example_values="'LN-00001'",
            ),
            PgColumn(
                name="client_id",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Borrowing client; FK to clients.",
                llm_example_values="'CL-000123'",
            ),
            PgColumn(
                name="currency",
                data_type="VARCHAR(3)",
                modifiers="NOT NULL",
                llm_description="Loan currency: KZT ~88%, USD ~12%.",
                llm_example_values="'KZT', 'USD'",
            ),
            PgColumn(
                name="principal",
                data_type="NUMERIC(18, 2)",
                modifiers="NOT NULL",
                llm_description="Amount lent, in the loan's currency.",
                llm_example_values="'4500000.00', '38000.00'",
            ),
            PgColumn(
                name="rate_pct",
                data_type="NUMERIC(5, 2)",
                modifiers="NOT NULL",
                llm_description="Annual interest rate: KZT 16–22%, USD 7–10%.",
                llm_example_values="'18.50', '8.25'",
            ),
            PgColumn(
                name="term_months",
                data_type="INTEGER",
                modifiers="NOT NULL",
                llm_description="Loan term.",
                llm_example_values="'12', '24', '36'",
            ),
            PgColumn(
                name="issued_on",
                data_type="DATE",
                modifiers="NOT NULL",
                llm_description="Disbursement date; on or after onboarding.",
                llm_example_values="'2023-05-10'",
            ),
            PgColumn(
                name="maturity_on",
                data_type="DATE",
                modifiers="NOT NULL",
                llm_description="Scheduled final repayment date.",
                llm_example_values="'2025-05-10'",
            ),
            PgColumn(
                name="closed_on",
                data_type="DATE",
                modifiers="",
                llm_description="Date repaid or written off; NULL while active.",
                llm_example_values="'2025-05-10', NULL",
            ),
            PgColumn(
                name="status",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="'active', 'repaid', or 'defaulted' (~4%).",
                llm_example_values="'active', 'repaid', 'defaulted'",
            ),
        ],
    )


def _add_months(day: date, months: int) -> date:
    month_index = day.month - 1 + months
    year, month = day.year + month_index // 12, month_index % 12 + 1
    return date(year, month, min(day.day, 28))


def _random_date(first: date, last: date) -> date:
    span = max((last - first).days, 0)
    return first + timedelta(days=int(get_random_state().randint(0, span + 1)))


def generate_loans(clients: pd.DataFrame, accounts: pd.DataFrame, end_date: str) -> pd.DataFrame:
    rng = get_random_state()
    end = date.fromisoformat(end_date)
    # A client has left when every account is closed; their exit is the last closure.
    exits: dict[str, date] = {}
    for client_id, group in accounts.groupby("client_id"):
        if group["closed_on"].notna().all():
            exits[str(client_id)] = max(group["closed_on"])
    rows: list[tuple[str, str, float, float, int, date, date, date | None, str]] = []
    for client in clients.itertuples(index=False):
        if rng.random_sample() >= _LOAN_SHARE:
            continue
        client_id = str(client.client_id)
        onboarded: date = client.onboarded_on  # type: ignore[assignment]
        last_issue = exits.get(client_id, end)
        issued = _random_date(max(onboarded, _LOAN_BOOK_START), last_issue)
        term = int(rng.choice(_TERMS, p=_TERM_WEIGHTS))
        maturity = _add_months(issued, term)
        is_fx = rng.random_sample() < _FX_SHARE
        principal = _MEDIAN_PRINCIPAL_KZT[str(client.segment)] * float(rng.lognormal(0, 0.5))
        if is_fx:
            principal /= _KZT_PER_USD
            rate = float(rng.uniform(7, 10))
        else:
            rate = float(rng.uniform(16, 22))

        status, closed = "active", None
        if rng.random_sample() < _DEFAULT_RATE:
            default_from = _add_months(issued, 3)
            if default_from <= min(maturity, end):
                status, closed = "defaulted", _random_date(default_from, min(maturity, end))
        if status == "active":
            exit_on = exits.get(client_id)
            if exit_on is not None and exit_on < maturity:
                status, closed = "repaid", max(exit_on, issued)
            elif maturity <= end:
                early = rng.random_sample() < _EARLY_REPAY_RATE
                closed = _random_date(issued, maturity) if early else maturity
                status = "repaid"
        rows.append(
            (client_id, "USD" if is_fx else "KZT", round(principal, 2), round(rate, 2), term,
             issued, maturity, closed, status)
        )  # fmt: skip
    rows.sort(key=lambda row: row[5])
    return pd.DataFrame(
        {
            "loan_id": [f"LN-{i:05d}" for i in range(1, len(rows) + 1)],
            "client_id": [r[0] for r in rows],
            "currency": [r[1] for r in rows],
            "principal": [r[2] for r in rows],
            "rate_pct": [r[3] for r in rows],
            "term_months": [r[4] for r in rows],
            "issued_on": [r[5] for r in rows],
            "maturity_on": [r[6] for r in rows],
            "closed_on": [r[7] for r in rows],
            "status": [r[8] for r in rows],
        }
    )
