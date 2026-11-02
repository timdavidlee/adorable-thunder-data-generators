import calendar
from dataclasses import dataclass, field
from datetime import date, timedelta

import numpy as np
import pandas as pd

from adorable_thunder.make.field_generators._random_state import get_random_state
from adorable_thunder.make.field_generators.kz_business import generate_kz_ibans
from adorable_thunder.make.record_generators.schemas import CreatePgTableSql, PgColumn

from .tariff_plans import FEE_INCREASE_ON, SMART_LAUNCH_ON

_BASE_PLANS = np.array(["START", "BUSINESS", "PRO", "TRADE", "AGRO"])
_BASE_PLAN_WEIGHTS = np.array([0.42, 0.37, 0.13, 0.08, 0.0])
_INDUSTRY_PLAN: dict[str, tuple[str, float]] = {
    "agriculture": ("AGRO", 0.70),
    "wholesale_import": ("TRADE", 0.45),
}
_UPGRADE_PATH = ["START", "BUSINESS", "PRO"]

_BASE_CLOSE_RATE = {True: 0.009, False: 0.014}  # keyed by is_primary
_FEE_SHOCK_MULTIPLIER = 2.0
_FEE_SHOCK_REGION = "Karaganda"
_FEE_SHOCK_REGION_MULTIPLIER = 9.0
_FEE_DOWNGRADE_RATE = 0.05
_SMART_SWITCH_RATE = 0.07
_ORGANIC_CHANGE_RATE = 0.003
_DORMANCY_RATE = 0.005
_DORMANT_AT_START_RATE = 0.05
_DORMANT_BANK_CLOSE_RATE = 0.015
_JOINT_EXIT_RATE = 0.8

_REASONS = np.array(
    ["client_request", "business_closed", "switched_bank", "fees", "bank_initiated"]
)
_NORMAL_REASON_WEIGHTS = np.array([0.35, 0.35, 0.15, 0.05, 0.10])
_FEE_REASON_WEIGHTS = np.array([0.15, 0.05, 0.35, 0.45, 0.0])

ACCOUNTS_TABLE_NAME = "accounts"


def create_pg_sql_table_schema(pg_schema: str) -> CreatePgTableSql:
    return CreatePgTableSql(
        pg_schema=pg_schema,
        pg_table=ACCOUNTS_TABLE_NAME,
        llm_description=(
            "Current accounts. Every client has one primary KZT account; ~25% hold a second. "
            "Closing one account does not mean the client left."
        ),
        pg_columns=[
            PgColumn(
                name="account_id",
                data_type="TEXT",
                modifiers="PRIMARY KEY",
                llm_description="Account number.",
                llm_example_values="'AC-0000001'",
            ),
            PgColumn(
                name="client_id",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Owning client; FK to clients.",
                llm_example_values="'CL-000123'",
            ),
            PgColumn(
                name="iban",
                data_type="TEXT",
                modifiers="NOT NULL UNIQUE",
                llm_description="20-character KZ IBAN.",
                llm_example_values="'KZ479990000001004217'",
            ),
            PgColumn(
                name="currency",
                data_type="VARCHAR(3)",
                modifiers="NOT NULL",
                llm_description="KZT ~85%, USD ~10%, EUR ~5%.",
                llm_example_values="'KZT', 'USD', 'EUR'",
            ),
            PgColumn(
                name="plan_code",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Current tariff plan (latest plan change, else opening plan).",
                llm_example_values="'START', 'BUSINESS', 'SMART'",
            ),
            PgColumn(
                name="opened_on",
                data_type="DATE",
                modifiers="NOT NULL",
                llm_description="Date opened; on or after the client's onboarding.",
                llm_example_values="'2021-09-14'",
            ),
            PgColumn(
                name="closed_on",
                data_type="DATE",
                modifiers="",
                llm_description="Date closed; NULL while open.",
                llm_example_values="'2025-05-20', NULL",
            ),
            PgColumn(
                name="close_reason",
                data_type="TEXT",
                modifiers="",
                llm_description="Why it closed; NULL while open.",
                llm_example_values=(
                    "'client_request', 'business_closed', 'switched_bank', 'fees', "
                    "'bank_initiated', NULL"
                ),
            ),
            PgColumn(
                name="status",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="'open' or 'closed'. Dormant accounts are still 'open'.",
                llm_example_values="'open', 'closed'",
            ),
        ],
    )


@dataclass
class _Account:
    client_id: str
    is_primary: bool
    currency: str
    plan: str
    opened_on: date
    region: str
    plan_history: list[tuple[date, str, str]] = field(default_factory=lambda: [])
    dormant_from: date | None = None
    closed_on: date | None = None
    close_reason: str | None = None


def _add_months(day: date, months: int) -> date:
    month_index = day.month - 1 + months
    return date(day.year + month_index // 12, month_index % 12 + 1, 1)


def _day_in_month(month: date, not_before: date) -> date:
    last_day = calendar.monthrange(month.year, month.month)[1]
    first = (
        not_before.day + 1
        if (not_before.year, not_before.month) == (month.year, month.month)
        else 1
    )
    if first > last_day:
        return date(month.year, month.month, last_day)
    return date(month.year, month.month, int(get_random_state().randint(first, last_day + 1)))


def _opening_plan(industry: str) -> str:
    rng = get_random_state()
    if industry in _INDUSTRY_PLAN:
        plan, share = _INDUSTRY_PLAN[industry]
        if rng.random_sample() < share:
            return plan
    return str(rng.choice(_BASE_PLANS, p=_BASE_PLAN_WEIGHTS))


def _open_accounts(clients: pd.DataFrame, end: date) -> list[_Account]:
    rng = get_random_state()
    accounts: list[_Account] = []
    for client in clients.itertuples(index=False):
        onboarded: date = client.onboarded_on  # type: ignore[assignment]
        primary_open = min(onboarded + timedelta(days=int(rng.randint(0, 4))), end)
        primary = _Account(
            client_id=str(client.client_id),
            is_primary=True,
            currency="KZT",
            plan=_opening_plan(str(client.industry)),
            opened_on=primary_open,
            region=str(client.region),
        )
        accounts.append(primary)
        if rng.random_sample() < 0.25:
            second_open = primary_open + timedelta(days=int(rng.randint(30, 700)))
            if second_open <= end:
                currency = str(rng.choice(["USD", "EUR", "KZT"], p=[0.5, 0.25, 0.25]))
                plan = "TRADE" if currency != "KZT" and rng.random_sample() < 0.5 else primary.plan
                accounts.append(
                    _Account(
                        client_id=primary.client_id,
                        is_primary=False,
                        currency=currency,
                        plan=plan,
                        opened_on=second_open,
                        region=primary.region,
                    )
                )
    return accounts


def _change_plan(account: _Account, month: date, to_plan: str) -> None:
    last_event = account.plan_history[-1][0] if account.plan_history else account.opened_on
    changed_on = _day_in_month(month, max(last_event, account.opened_on))
    account.plan_history.append((changed_on, account.plan, to_plan))
    account.plan = to_plan


def _close(account: _Account, month: date, reason: str) -> None:
    last_event = account.plan_history[-1][0] if account.plan_history else account.opened_on
    account.closed_on = _day_in_month(month, last_event)
    account.close_reason = reason


def _close_rate(account: _Account, month: date) -> tuple[float, bool]:
    """Monthly closure probability, and whether it's inflated by the fee increase."""
    rate = _BASE_CLOSE_RATE[account.is_primary]
    shock_start = _add_months(FEE_INCREASE_ON, 1)
    in_shock = account.plan == "BUSINESS" and shock_start <= month < _add_months(shock_start, 4)
    if not in_shock:
        return rate, False
    if account.region == _FEE_SHOCK_REGION:
        return rate * _FEE_SHOCK_REGION_MULTIPLIER, True
    return rate * _FEE_SHOCK_MULTIPLIER, True


def _step_month(account: _Account, month: date) -> None:
    rng = get_random_state()
    if account.dormant_from is not None:
        dormant_months = (month.year - account.dormant_from.year) * 12 + (
            month.month - account.dormant_from.month
        )
        if dormant_months >= 6 and rng.random_sample() < _DORMANT_BANK_CLOSE_RATE:
            _close(account, month, "bank_initiated")
        return

    rate, fee_driven = _close_rate(account, month)
    if rng.random_sample() < rate:
        weights = (
            _FEE_REASON_WEIGHTS
            if fee_driven and rng.random_sample() < 0.7
            else _NORMAL_REASON_WEIGHTS
        )
        _close(account, month, str(rng.choice(_REASONS, p=weights)))
        return

    if account.plan == "BUSINESS" and FEE_INCREASE_ON <= month < _add_months(FEE_INCREASE_ON, 6):
        if rng.random_sample() < _FEE_DOWNGRADE_RATE:
            _change_plan(account, month, "START")
    elif month == SMART_LAUNCH_ON and account.plan in ("START", "BUSINESS"):
        if rng.random_sample() < _SMART_SWITCH_RATE:
            _change_plan(account, month, "SMART")
    elif account.plan in _UPGRADE_PATH and rng.random_sample() < _ORGANIC_CHANGE_RATE:
        index = _UPGRADE_PATH.index(account.plan)
        step = 1 if index == 0 or (index == 1 and rng.random_sample() < 0.6) else -1
        _change_plan(account, month, _UPGRADE_PATH[index + step])

    if rng.random_sample() < _DORMANCY_RATE:
        account.dormant_from = month


def _simulate(accounts: list[_Account], start: date, end: date) -> None:
    rng = get_random_state()
    for account in accounts:
        if account.opened_on < start and rng.random_sample() < _DORMANT_AT_START_RATE:
            account.dormant_from = start

    by_client: dict[str, list[_Account]] = {}
    for account in accounts:
        by_client.setdefault(account.client_id, []).append(account)

    month = start
    while month <= end:
        for client_accounts in by_client.values():
            for account in client_accounts:
                opened_month = date(account.opened_on.year, account.opened_on.month, 1)
                if account.closed_on is None and opened_month <= month:
                    _step_month(account, month)
            primary = client_accounts[0]
            if primary.closed_on is not None and primary.closed_on.replace(day=1) == month:
                for other in client_accounts[1:]:
                    if other.closed_on is None and rng.random_sample() < _JOINT_EXIT_RATE:
                        last_change = other.plan_history[-1][0] if other.plan_history else None
                        other.closed_on = max(
                            primary.closed_on, other.opened_on, last_change or other.opened_on
                        )
                        other.close_reason = primary.close_reason
        month = _add_months(month, 1)


def generate_accounts(clients: pd.DataFrame, start_date: str, end_date: str) -> pd.DataFrame:
    start, end = date.fromisoformat(start_date), date.fromisoformat(end_date)
    accounts = _open_accounts(clients, end)
    _simulate(accounts, start, end)
    primary_closed = {a.client_id: a.closed_on for a in accounts if a.is_primary}
    accounts = [
        a
        for a in accounts
        if a.is_primary or (closed := primary_closed[a.client_id]) is None or a.opened_on <= closed
    ]
    n_accounts = len(accounts)
    return pd.DataFrame(
        {
            "account_id": [f"AC-{i:07d}" for i in range(1, n_accounts + 1)],
            "client_id": [a.client_id for a in accounts],
            "iban": generate_kz_ibans(n_accounts),
            "currency": [a.currency for a in accounts],
            "plan_code": [a.plan for a in accounts],
            "opened_on": [a.opened_on for a in accounts],
            "closed_on": [a.closed_on for a in accounts],
            "close_reason": [a.close_reason for a in accounts],
            "status": ["closed" if a.closed_on else "open" for a in accounts],
            "_is_primary": [a.is_primary for a in accounts],
            "_plan_history": [a.plan_history for a in accounts],
            "_dormant_from": [a.dormant_from for a in accounts],
        }
    )
