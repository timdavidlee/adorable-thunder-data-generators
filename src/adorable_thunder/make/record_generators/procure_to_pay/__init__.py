from adorable_thunder.make.record_generators.schemas import CreatePgTableSql

from . import invoices, payments, purchase_orders, requests
from .flow import FLOW_NAME, GeneratorConfig

FLOW_SCHEMAS: list[CreatePgTableSql] = [
    requests.create_pg_sql_table_schema(FLOW_NAME),
    purchase_orders.create_pg_sql_table_schema(FLOW_NAME),
    invoices.create_pg_sql_table_schema(FLOW_NAME),
    payments.create_pg_sql_table_schema(FLOW_NAME),
]

__all__ = ["GeneratorConfig", "FLOW_SCHEMAS"]
