from adorable_thunder.make.record_generators.schemas import CreatePgTableSql

from . import contracts, recurring_invoices, renewals, subscriptions, usage_records
from .flow import FLOW_NAME, GeneratorConfig

FLOW_SCHEMAS: list[CreatePgTableSql] = [
    subscriptions.create_pg_sql_table_schema(FLOW_NAME),
    contracts.create_pg_sql_table_schema(FLOW_NAME),
    recurring_invoices.create_pg_sql_table_schema(FLOW_NAME),
    usage_records.create_pg_sql_table_schema(FLOW_NAME),
    renewals.create_pg_sql_table_schema(FLOW_NAME),
]

__all__ = ["GeneratorConfig", "FLOW_SCHEMAS"]
