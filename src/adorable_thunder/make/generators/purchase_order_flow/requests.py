import numpy as np
import pandas as pd
from pydantic import BaseModel
from adorable_thunder.generators.amounts import (
    generate_amounts,
    generate_local_currency_amounts,
)
from adorable_thunder.generators.currency import CurrencyGenerator
from adorable_thunder.generators.company import generate_company_names
from adorable_thunder.generators.dates import (
    generate_random_dates,
    extrapolate_off_dates,
)
from adorable_thunder.generators.identifiers import (
    generate_serial_numbers_with_prefix,
    generate_n_random_uuids,
)
from adorable_thunder.generators.users import generate_user_emails
from adorable_thunder.generators.purchase_order_flow.config_def import (
    RequestStatusStates,
)
from adorable_thunder.common.math import generate_weighted_enum_choices


class Request(BaseModel):
    request_system_id: str
    request_document_number: str
    request_date: str
    description: str | None = None
    price_usd: float
    price_local: float | None = None
    currency_code: str | None = None
    request_status: str | None = None
    requester_email: str | None = None
    owner_email: str | None = None
    creator_email: str | None = None
    supplier_name: str | None = None
    cost_center: str | None = None
    created_date: str | None = None
    completed_date: str | None = None


class RequestGeneratorConfig(BaseModel):
    num_requests: int = 200
    start_date: str = "2025-01-01"
    end_date: str = "2026-01-01"

    def make(self) -> pd.DataFrame:
        n_records = self.num_requests

        data_df = pd.DataFrame(index=np.arange(n_records))

        data_df["request_system_id"] = generate_n_random_uuids(n_records)
        data_df["request_document_number"] = generate_serial_numbers_with_prefix(
            prefix="REQ", n=n_records
        )

        data_df["start_date"] = generate_random_dates(
            n_samples=n_records,
            start_date=self.start_date,
            end_date=self.end_date,
            dist_scaling=0.5,
        )

        data_df["completed_date"] = extrapolate_off_dates(
            data_df["start_date"], min_days=1, max_days=30
        )

        data_df["supplier_name"] = generate_company_names(n_records)
        data_df["request_status"] = generate_weighted_enum_choices(
            RequestStatusStates, n_records, power_scale=1.5
        )
        data_df["requester_email"] = generate_user_emails(n_records)
        data_df["owner_email"] = generate_user_emails(n_records)
        data_df["creator_email"] = generate_user_emails(n_records)

        amounts = generate_amounts(n_records)
        currency_gen = CurrencyGenerator()
        currency_codes = currency_gen.generate_currency_entries(n_records)
        local_amounts_df = generate_local_currency_amounts(amounts, currency_codes)

        data_df = pd.concat([data_df, local_amounts_df], axis=1)
        return data_df
