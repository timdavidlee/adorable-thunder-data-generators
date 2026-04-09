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
from adorable_thunder.generators.identifiers import generate_serial_numbers_with_prefix


class Request(BaseModel):
    request_system_id: str
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
    def __init__(
        self,
        num_requests: int = 200,
        start_date: str = "2025-01-01",
        end_date: str = "2026-01-01",
    ):
        self.num_requests = num_requests

    def make(self):
        n_records = self.num_requests
        start_dates = generate_random_dates(
            n_records,
            start_date=self.start_date,
            end_date=self.end_date,
            dist_scaling=0.5,
        )
        completed_dates = extrapolate_off_dates(start_dates, min_days=1, max_days=30)

        amounts = generate_amounts(n_records)
        currency_gen = CurrencyGenerator()
        currency_codes = currency_gen.generate_currency_entries(n_records)
        local_amounts_df = generate_local_currency_amounts(amounts, currency_codes)

        companies = generate_company_names(n_records)
