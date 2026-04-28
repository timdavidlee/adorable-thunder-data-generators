from typing import ClassVar

import pandas as pd

from adorable_thunder.make.record_generators.schemas import BaseGeneratorConfig

from .contracts import CONTRACTS_TABLE_NAME, generate_contracts
from .recurring_invoices import RECURRING_INVOICES_TABLE_NAME, generate_recurring_invoices
from .renewals import RENEWALS_TABLE_NAME, generate_renewals
from .subscriptions import SUBSCRIPTIONS_TABLE_NAME, generate_subscriptions
from .usage_records import USAGE_RECORDS_TABLE_NAME, generate_usage_records

FLOW_NAME = "quote_to_cash"


class GeneratorConfig(BaseGeneratorConfig):
    name: ClassVar[str] = FLOW_NAME
    start_date: str = "2024-01-01"
    end_date: str = "2025-12-31"

    def make(self) -> dict[str, pd.DataFrame]:
        subs = generate_subscriptions(self.n_samples, self.start_date, self.end_date)

        sub_ids = subs["sub_id"].to_numpy()
        sub_starts = subs["start_date"]
        sub_ends = subs["end_date"]
        churn_dates = subs["churn_date"]
        cycles = subs["billing_cycle_months"].to_numpy()
        mrr = subs["mrr_usd"].to_numpy()
        currencies = subs["currency_code"].to_numpy()
        term_months = subs["_term_months"].to_numpy()
        statuses = subs["status"].to_numpy()
        auto_renew = subs["auto_renew"].to_numpy()

        contracts = generate_contracts(
            n_samples=self.n_samples,
            sub_ids=sub_ids,
            sub_start_dates=sub_starts,
            term_months=term_months,
            mrr_usd=mrr,
            auto_renew=auto_renew,
            sub_statuses=statuses,
        )

        invoices = generate_recurring_invoices(
            sub_ids=sub_ids,
            sub_start_dates=sub_starts,
            sub_end_dates=sub_ends,
            billing_cycle_months=cycles,
            mrr_usd=mrr,
            currency_codes=currencies,
            churn_dates=churn_dates,
            dataset_end=self.end_date,
        )

        usage = generate_usage_records(
            sub_ids=sub_ids,
            sub_start_dates=sub_starts,
            sub_end_dates=sub_ends,
            billing_cycle_months=cycles,
            churn_dates=churn_dates,
            dataset_end=self.end_date,
        )

        renewals = generate_renewals(
            sub_ids=sub_ids,
            sub_end_dates=sub_ends,
            sub_statuses=statuses,
            auto_renew=auto_renew,
            mrr_usd=mrr,
            term_months=term_months,
            dataset_end=self.end_date,
        )

        # Active subs whose term ended without renewing must transition to churned
        # at end_date — leaving them "active" past end_date is flagged as a hard bug
        # by the scrutiny brief.
        dataset_end_ts = pd.Timestamp(self.end_date)
        renewed_ids: set[str] = (
            set(renewals["sub_id"].astype(str).tolist()) if len(renewals) else set()
        )
        ended_no_renew = (
            (subs["status"] == "active")
            & (pd.to_datetime(subs["end_date"]) <= dataset_end_ts)
            & (~subs["sub_id"].isin(renewed_ids))
        )
        if ended_no_renew.any():
            subs.loc[ended_no_renew, "status"] = "churned"
            subs.loc[ended_no_renew, "churn_date"] = pd.to_datetime(
                subs.loc[ended_no_renew, "end_date"]
            )

        return {
            SUBSCRIPTIONS_TABLE_NAME: subs.drop(columns=["_term_months"]),
            CONTRACTS_TABLE_NAME: contracts,
            RECURRING_INVOICES_TABLE_NAME: invoices,
            USAGE_RECORDS_TABLE_NAME: usage,
            RENEWALS_TABLE_NAME: renewals,
        }
