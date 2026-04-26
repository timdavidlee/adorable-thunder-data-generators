from . import invoices, payments, purchase_orders, requests
from .flow import GeneratorConfig

_PG_SCHEMA = "procure_to_pay"

FLOW_SCHEMAS = [
    requests.create_pg_sql_table_schema(_PG_SCHEMA),
    purchase_orders.create_pg_sql_table_schema(_PG_SCHEMA),
    invoices.create_pg_sql_table_schema(_PG_SCHEMA),
    payments.create_pg_sql_table_schema(_PG_SCHEMA),
]

__all__ = ["GeneratorConfig", "FLOW_SCHEMAS"]
