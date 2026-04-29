from typing import ClassVar

import pandas as pd

from adorable_thunder.make.field_generators._random_state import get_random_state
from adorable_thunder.make.field_generators.dates import extrapolate_off_dates
from adorable_thunder.make.record_generators.schemas import BaseGeneratorConfig

from .contacts import CONTACTS_TABLE_NAME, generate_contacts
from .contracts import CONTRACTS_TABLE_NAME, generate_contracts
from .leads import LEADS_TABLE_NAME, generate_leads
from .opportunities import OPPORTUNITIES_TABLE_NAME, generate_opportunities
from .quotes import QUOTES_TABLE_NAME, generate_quotes

FLOW_NAME = "lead_to_opportunity"

_LEAD_TO_CONTACT_RATE = 0.20  # 20% of leads are converted to contacts
_CONTACT_TO_OPP_RATE = 0.20  # 20% of contacts generate opportunities (~4% lead-to-opp total)

_QUOTE_STAGES = frozenset(["Proposal", "Negotiation", "Closed Won", "Closed Lost"])


class GeneratorConfig(BaseGeneratorConfig):
    name: ClassVar[str] = FLOW_NAME
    start_date: str = "2024-01-01"
    end_date: str = "2025-12-31"

    def make(self) -> dict[str, pd.DataFrame]:
        n_contacts = max(1, int(self.n_samples * _LEAD_TO_CONTACT_RATE))
        leads = generate_leads(
            self.n_samples, self.start_date, self.end_date, n_converted=n_contacts
        )

        # Contacts sourced from converted leads; creation date is 1–14 days after lead capture
        converted = leads[leads["status"] == "converted"].reset_index(drop=True)
        contact_dates = extrapolate_off_dates(converted["created_date"], min_days=1, max_days=14)
        contacts = generate_contacts(
            len(converted),
            lead_ids=converted["lead_id"].to_numpy(),
            lead_companies=converted["company"].to_numpy(),
            lead_first_names=converted["first_name"].to_numpy(),
            lead_last_names=converted["last_name"].to_numpy(),
        )

        # Opportunities from a random subset of contacts
        n_opps = max(1, int(len(contacts) * _CONTACT_TO_OPP_RATE))
        opp_idx = get_random_state().choice(len(contacts), size=n_opps, replace=False)
        opp_contacts = contacts.iloc[opp_idx].reset_index(drop=True)
        opp_contact_dates = contact_dates.iloc[opp_idx].reset_index(drop=True)

        opportunities = generate_opportunities(
            n_opps,
            contact_ids=opp_contacts["contact_id"].to_numpy(),
            companies=opp_contacts["company"].to_numpy(),
            contact_dates=opp_contact_dates,
            end_date=self.end_date,
        )

        # Quotes for Proposal-stage and later opportunities
        quote_mask = opportunities["stage"].isin(_QUOTE_STAGES)
        quote_opps = opportunities[quote_mask].reset_index(drop=True)
        quotes = generate_quotes(
            len(quote_opps),
            opp_ids=quote_opps["opp_id"].to_numpy(),
            deal_values=quote_opps["deal_value"].to_numpy(),
            opp_dates=quote_opps["created_date"],
        )

        # Contracts for Closed Won opportunities only (matched via their quote)
        won_opp_ids = set(opportunities.loc[opportunities["stage"] == "Closed Won", "opp_id"])
        won_quotes = quotes[quotes["opp_id"].isin(won_opp_ids)].reset_index(drop=True)
        contracts = generate_contracts(
            len(won_quotes),
            opp_ids=won_quotes["opp_id"].to_numpy(),
            quote_totals=won_quotes["total_amount"].to_numpy(),
            quote_dates=won_quotes["quote_date"],
        )

        return {
            LEADS_TABLE_NAME: leads,
            CONTACTS_TABLE_NAME: contacts,
            OPPORTUNITIES_TABLE_NAME: opportunities,
            QUOTES_TABLE_NAME: quotes,
            CONTRACTS_TABLE_NAME: contracts,
        }
