from pathlib import Path

import pandas as pd

from .invoices import generate_invoices, INVOICES_TABLE_NAME
from .payments import generate_payments, PAYMENTS_TABLE_NAME
from .purchase_orders import generate_purchase_orders, PURCHASE_ORDERS_TABLE_NAME
from .requests import generate_requests, REQUESTS_TABLE_NAME
from adorable_thunder.make.record_generators.schemas import BaseGeneratorConfig

class GeneratorConfig(BaseGeneratorConfig):
    n_samples: int = 1000
    start_date: str = "2024-01-01"
    end_date: str = "2025-12-31"

    def name(self):
        return "procure_to_pay"

    def make(self) -> dict[str, pd.DataFrame]:
        requests = generate_requests(self.n_samples, self.start_date, self.end_date)

        active_requests = requests[requests["status"] != "rejected"].reset_index(drop=True)
        purchase_orders = generate_purchase_orders(
            len(active_requests),
            start_date=self.start_date,
            end_date=self.end_date,
            request_ids=active_requests["request_id"].to_numpy(),
            request_dates=active_requests["request_date"],
        )

        active_pos = purchase_orders[
            ~purchase_orders["status"].isin(["rejected", "cancelled"])
        ].reset_index(drop=True)
        invoices = generate_invoices(
            len(active_pos),
            start_date=self.start_date,
            end_date=self.end_date,
            po_ids=active_pos["po_id"].to_numpy(),
            po_dates=active_pos["po_date"],
            po_amounts_usd=active_pos["total_amount_usd"].to_numpy(),
        )

        # active_pos and invoices share the same 0-based index, so the mask aligns both
        active_inv_mask = invoices["status"] != "cancelled"
        payments = generate_payments(
            int(active_inv_mask.sum()),
            start_date=self.start_date,
            end_date=self.end_date,
            invoice_ids=invoices.loc[active_inv_mask, "invoice_id"].to_numpy(),
            due_dates=invoices.loc[active_inv_mask, "due_date"].reset_index(drop=True),
            invoice_amounts_usd=invoices.loc[active_inv_mask, "amount_invoiced"].to_numpy(),
            currency_codes=active_pos.loc[active_inv_mask, "currency_code"].to_numpy(),
        )

        return {
            REQUESTS_TABLE_NAME: requests,
            PURCHASE_ORDERS_TABLE_NAME: purchase_orders,
            INVOICES_TABLE_NAME: invoices,
            PAYMENTS_TABLE_NAME: payments,
        }
