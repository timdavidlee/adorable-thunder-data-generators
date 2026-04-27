from typing import ClassVar

import pandas as pd

from adorable_thunder.make.record_generators.schemas import BaseGeneratorConfig

from .invoices import INVOICES_TABLE_NAME, generate_invoices
from .payments import PAYMENTS_TABLE_NAME, generate_payments
from .purchase_orders import PURCHASE_ORDERS_TABLE_NAME, generate_purchase_orders
from .requests import REQUESTS_TABLE_NAME, generate_requests

FLOW_NAME = "procure_to_pay"


class GeneratorConfig(BaseGeneratorConfig):
    name: ClassVar[str] = FLOW_NAME
    start_date: str = "2024-01-01"
    end_date: str = "2025-12-31"

    def make(self) -> dict[str, pd.DataFrame]:
        requests = generate_requests(self.n_samples, self.start_date, self.end_date)

        active_requests = requests[requests["status"] != "rejected"].reset_index(drop=True)
        purchase_orders = generate_purchase_orders(
            len(active_requests),
            start_date=self.start_date,
            end_date=self.end_date,
            request_ids=active_requests["request_id"].to_numpy(),
            request_dates=active_requests["request_date"],
            supplier_names=active_requests["supplier_name"].to_numpy(),
        )

        # Invoices are only raised against approved POs — pending/draft POs haven't
        # been signed off yet, so no supplier invoice would exist for them.
        approved_pos = purchase_orders[
            purchase_orders["status"] == "approved"
        ].reset_index(drop=True)
        invoices = generate_invoices(
            len(approved_pos),
            start_date=self.start_date,
            end_date=self.end_date,
            po_ids=approved_pos["po_id"].to_numpy(),
            po_dates=approved_pos["po_date"],
            po_amounts_usd=approved_pos["total_amount_usd"].to_numpy(),
        )

        active_inv_mask = invoices["status"] != "cancelled"
        payments = generate_payments(
            int(active_inv_mask.sum()),
            start_date=self.start_date,
            end_date=self.end_date,
            invoice_ids=invoices.loc[active_inv_mask, "invoice_id"].to_numpy(),
            due_dates=invoices.loc[active_inv_mask, "due_date"].reset_index(drop=True),
            invoice_amounts_usd=invoices.loc[active_inv_mask, "amount_invoiced"].to_numpy(),
            currency_codes=approved_pos.loc[active_inv_mask, "currency_code"].to_numpy(),
        )

        return {
            REQUESTS_TABLE_NAME: requests,
            PURCHASE_ORDERS_TABLE_NAME: purchase_orders,
            INVOICES_TABLE_NAME: invoices,
            PAYMENTS_TABLE_NAME: payments,
        }
