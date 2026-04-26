import pandas as pd

from .cash_applications import generate_cash_applications, CASH_APPLICATION_TABLE_NAME
from .cash_receipts import generate_cash_receipts, CASH_RECEIPTS_TABLE_NAME
from .invoices import generate_invoices, INVOICES_TABLE_NAME
from .quotes import generate_quotes, QUOTES_TABLE_NAME
from .sales_orders import generate_sales_orders, SALES_ORDER_TABLE_NAME
from .shipments import generate_shipments, SHIPMENTS_TABLE_NAME
from adorable_thunder.make.record_generators.schemas import BaseGeneratorConfig

class GeneratorConfig(BaseGeneratorConfig):
    n_samples: int = 1000
    start_date: str = "2024-01-01"
    end_date: str = "2025-12-31"

    def name(self):
        return "order_to_cash"

    def make(self) -> dict[str, pd.DataFrame]:
        quotes = generate_quotes(self.n_samples, self.start_date, self.end_date)

        active_quotes = quotes[
            ~quotes["status"].isin(["rejected", "expired"])
        ].reset_index(drop=True)
        sales_orders = generate_sales_orders(
            len(active_quotes),
            start_date=self.start_date,
            end_date=self.end_date,
            quote_ids=active_quotes["quote_id"].to_numpy(),
            quote_dates=active_quotes["quote_date"],
            quote_amounts_usd=active_quotes["amount_usd"].to_numpy(),
            quote_discount_rates=active_quotes["discount_rate"].to_numpy(),
            quote_currency_codes=active_quotes["currency_code"].to_numpy(),
        )

        active_orders = sales_orders[sales_orders["status"] != "cancelled"].reset_index(
            drop=True
        )
        shipments = generate_shipments(
            len(active_orders),
            start_date=self.start_date,
            end_date=self.end_date,
            order_ids=active_orders["order_id"].to_numpy(),
            order_dates=active_orders["order_date"],
        )

        # active_orders and shipments share the same 0-based index
        active_ship_mask = shipments["status"] != "cancelled"
        invoices = generate_invoices(
            int(active_ship_mask.sum()),
            start_date=self.start_date,
            end_date=self.end_date,
            order_ids=active_orders.loc[active_ship_mask, "order_id"].to_numpy(),
            ship_dates=shipments.loc[active_ship_mask, "ship_date"].reset_index(
                drop=True
            ),
            order_net_amounts_usd=active_orders.loc[
                active_ship_mask, "net_amount_usd"
            ].to_numpy(),
            currency_codes=active_orders.loc[
                active_ship_mask, "currency_code"
            ].to_numpy(),
        )

        # invoices and the active_ship_mask subset of active_orders share the same index
        active_inv_mask = invoices["status"] != "cancelled"
        invoice_totals = invoices.loc[active_inv_mask, "total_amount"].to_numpy()
        cash_receipts = generate_cash_receipts(
            int(active_inv_mask.sum()),
            start_date=self.start_date,
            end_date=self.end_date,
            invoice_ids=invoices.loc[active_inv_mask, "invoice_id"].to_numpy(),
            due_dates=invoices.loc[active_inv_mask, "due_date"].reset_index(drop=True),
            invoice_totals_usd=invoice_totals,
            currency_codes=invoices.loc[active_inv_mask, "currency_code"].to_numpy(),
        )

        cash_applications = generate_cash_applications(
            len(cash_receipts),
            receipt_ids=cash_receipts["receipt_id"].to_numpy(),
            invoice_ids=cash_receipts["invoice_id"].to_numpy(),
            amounts_received=cash_receipts["amount_received"].to_numpy(),
            invoice_totals_usd=invoice_totals,
        )

        return {
            QUOTES_TABLE_NAME: quotes,
            SALES_ORDER_TABLE_NAME: sales_orders,
            SHIPMENTS_TABLE_NAME: shipments,
            INVOICES_TABLE_NAME: invoices,
            CASH_RECEIPTS_TABLE_NAME: cash_receipts,
            CASH_APPLICATION_TABLE_NAME: cash_applications,
        }
