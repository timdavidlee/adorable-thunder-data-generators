from adorable_thunder.make.record_generators.schemas import CreatePgTableSql

from . import contacts, contracts, leads, opportunities, quotes
from .flow import FLOW_NAME, GeneratorConfig

FLOW_SCHEMAS: list[CreatePgTableSql] = [
    leads.create_pg_sql_table_schema(FLOW_NAME),
    contacts.create_pg_sql_table_schema(FLOW_NAME),
    opportunities.create_pg_sql_table_schema(FLOW_NAME),
    quotes.create_pg_sql_table_schema(FLOW_NAME),
    contracts.create_pg_sql_table_schema(FLOW_NAME),
]

__all__ = ["GeneratorConfig", "FLOW_SCHEMAS"]
