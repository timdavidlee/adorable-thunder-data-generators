from datetime import date

import pandas as pd
import pytest

from adorable_thunder.make.field_generators._random_state import reset_random_state
from adorable_thunder.make.record_generators.onboard_to_offboard import GeneratorConfig

Tables = dict[str, pd.DataFrame]


@pytest.fixture(scope="module")
def tables() -> Tables:
    reset_random_state()
    return GeneratorConfig(n_samples=1_500).make()


def test_make_is_reproducible_after_reset(tables: Tables) -> None:
    reset_random_state()

    again = GeneratorConfig(n_samples=1_500).make()

    assert again["accounts"].equals(tables["accounts"])


def test_every_client_has_one_primary_kzt_account_within_three_days(tables: Tables) -> None:
    accounts = tables["accounts"].merge(tables["clients"], on="client_id")
    first = accounts.sort_values("opened_on").groupby("client_id").head(1)

    lag_days = (pd.to_datetime(first["opened_on"]) - pd.to_datetime(first["onboarded_on"])).dt.days

    assert len(first) == len(tables["clients"])
    assert (first["currency"] == "KZT").all()
    assert lag_days.between(0, 3).all()


def test_closure_fields_are_set_together(tables: Tables) -> None:
    accounts = tables["accounts"]
    closed = accounts["status"] == "closed"

    assert (accounts["closed_on"].notna() == closed).all()
    assert (accounts["close_reason"].notna() == closed).all()


def test_no_activity_outside_open_window(tables: Tables) -> None:
    activity = tables["monthly_activity"].merge(tables["accounts"], on="account_id")
    month = pd.to_datetime(activity["month"])
    opened = pd.to_datetime(activity["opened_on"]).dt.to_period("M").dt.to_timestamp()
    closed = pd.to_datetime(activity["closed_on"]).dt.to_period("M").dt.to_timestamp()

    outside = (month < opened) | (closed.notna() & (month > closed))

    assert not outside.any()


def test_plan_changes_chain_to_current_plan(tables: Tables) -> None:
    changes = tables["plan_changes"].sort_values(["account_id", "changed_on", "plan_change_id"])
    last = changes.groupby("account_id").tail(1).set_index("account_id")["to_plan"]
    current = tables["accounts"].set_index("account_id")["plan_code"]

    assert (current.loc[last.index] == last).all()


def test_plan_changes_fall_inside_open_window(tables: Tables) -> None:
    changes = tables["plan_changes"].merge(tables["accounts"], on="account_id")
    after_close = changes["closed_on"].notna() & (changes["changed_on"] > changes["closed_on"])

    assert (changes["changed_on"] >= changes["opened_on"]).all()
    assert not after_close.any()


def test_smart_plan_only_appears_after_launch(tables: Tables) -> None:
    smart = tables["plan_changes"][tables["plan_changes"]["to_plan"] == "SMART"]

    assert len(smart) > 0
    assert (smart["changed_on"] >= date(2025, 12, 1)).all()


def test_business_closures_rise_after_fee_increase(tables: Tables) -> None:
    accounts = tables["accounts"]
    closed_month = pd.to_datetime(accounts["closed_on"]).dt.to_period("M")
    before = closed_month.between(pd.Period("2024-04"), pd.Period("2024-07")).sum()
    after = closed_month.between(pd.Period("2025-04"), pd.Period("2025-07")).sum()

    assert after > 1.5 * before


def test_some_open_accounts_are_dormant(tables: Tables) -> None:
    activity = tables["monthly_activity"].sort_values("month")
    open_ids = tables["accounts"].loc[tables["accounts"]["status"] == "open", "account_id"]
    last_three = activity[activity["account_id"].isin(open_ids)].groupby("account_id").tail(3)

    dormant_share = (last_three.groupby("account_id")["txn_count"].sum() == 0).mean()

    assert 0.03 < dormant_share < 0.20


def test_some_clients_close_one_account_and_keep_another(tables: Tables) -> None:
    statuses = tables["accounts"].groupby("client_id")["status"].agg(set)

    partial = statuses.apply(lambda s: s == {"open", "closed"})

    assert partial.sum() > 0


def test_closed_loans_have_a_close_date_and_active_ones_do_not(tables: Tables) -> None:
    loans = tables["loans"]

    assert (loans["closed_on"].isna() == (loans["status"] == "active")).all()
