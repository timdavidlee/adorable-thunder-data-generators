from pydantic import BaseModel
from adorable_thunder.generators.amounts import generate_amounts
from adorable_thunder.generators.company import generate_company_names
from adorable_thunder.generators.dates import generate_random_dates
from adorable_thunder.generators.identifiers import generate_serial_numbers_with_prefix


class Request(BaseModel):
    request_system_id: str
    request_date: str


class RequestGeneratorConfig(BaseModel):
    def __init__(
        self,
        num_requests: int = 200,
        start_date: str = "2025-01-01",
        end_date: str = "2026-01-01",
    ):
        self.num_requests = num_requests

    def make(self):
        dates = generate_random_dates(
            self.num_requests,
            start_date=self.start_date,
            end_date=self.end_date,
            dist_scaling=0.5,
        )

        amounts = generate_amounts(self.num_requests)

        companies = generate_company_names(self.num_requests)
