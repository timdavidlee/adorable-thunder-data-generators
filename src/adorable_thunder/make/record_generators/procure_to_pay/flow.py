import pandas as pd
from pydantic import BaseModel

from .invoices import generate_invoices
from .payments import generate_payments
from .purchase_orders import generate_purchase_orders
from .requests import generate_requests


class GeneratorConfig(BaseModel):
    n_samples: int = 1000
    start_date: str = "2024-01-01"
    end_date: str = "2025-12-31"

    def make(self) -> dict[str, pd.DataFrame]:
        requests = generate_requests(self.n_samples, self.start_date, self.end_date)
        purchase_orders = generate_purchase_orders(
            self.n_samples,
            start_date=self.start_date,
            end_date=self.end_date,
            request_ids=requests["request_id"].to_numpy(),
            request_dates=requests["request_date"],
        )
        invoices = generate_invoices(
            self.n_samples,
            start_date=self.start_date,
            end_date=self.end_date,
            po_ids=purchase_orders["po_id"].to_numpy(),
            po_dates=purchase_orders["po_date"],
            po_amounts_usd=purchase_orders["total_amount_usd"].to_numpy(),
        )
        payments = generate_payments(
            self.n_samples,
            start_date=self.start_date,
            end_date=self.end_date,
            invoice_ids=invoices["invoice_id"].to_numpy(),
            due_dates=invoices["due_date"],
            invoice_amounts_usd=invoices["amount_invoiced"].to_numpy(),
            currency_codes=purchase_orders["currency_code"].to_numpy(),
        )
        return {
            "requests": requests,
            "purchase_orders": purchase_orders,
            "invoices": invoices,
            "payments": payments,
        }
