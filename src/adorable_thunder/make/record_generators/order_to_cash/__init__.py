from . import cash_applications, cash_receipts, invoices, quotes, sales_orders, shipments
from .flow import GeneratorConfig

_PG_SCHEMA = "order_to_cash"

FLOW_SCHEMAS = [
    quotes.create_pg_sql_table_schema(_PG_SCHEMA),
    sales_orders.create_pg_sql_table_schema(_PG_SCHEMA),
    shipments.create_pg_sql_table_schema(_PG_SCHEMA),
    invoices.create_pg_sql_table_schema(_PG_SCHEMA),
    cash_receipts.create_pg_sql_table_schema(_PG_SCHEMA),
    cash_applications.create_pg_sql_table_schema(_PG_SCHEMA),
]

__all__ = ["GeneratorConfig", "FLOW_SCHEMAS"]
