from adorable_thunder.make.record_generators.schemas import CreatePgTableSql

from . import (
    cash_applications,
    cash_receipts,
    invoices,
    quotes,
    sales_orders,
    shipments,
)
from .flow import FLOW_NAME, GeneratorConfig

FLOW_SCHEMAS: list[CreatePgTableSql] = [
    quotes.create_pg_sql_table_schema(FLOW_NAME),
    sales_orders.create_pg_sql_table_schema(FLOW_NAME),
    shipments.create_pg_sql_table_schema(FLOW_NAME),
    invoices.create_pg_sql_table_schema(FLOW_NAME),
    cash_receipts.create_pg_sql_table_schema(FLOW_NAME),
    cash_applications.create_pg_sql_table_schema(FLOW_NAME),
]

__all__ = ["GeneratorConfig", "FLOW_SCHEMAS"]
