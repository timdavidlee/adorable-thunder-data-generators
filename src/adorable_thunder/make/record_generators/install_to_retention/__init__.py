from adorable_thunder.make.record_generators.schemas import CreatePgTableSql

from . import accounts, activation_events, iap_purchases, installs, retention_snapshots
from .flow import FLOW_NAME, GeneratorConfig

FLOW_SCHEMAS: list[CreatePgTableSql] = [
    installs.create_pg_sql_table_schema(FLOW_NAME),
    accounts.create_pg_sql_table_schema(FLOW_NAME),
    activation_events.create_pg_sql_table_schema(FLOW_NAME),
    iap_purchases.create_pg_sql_table_schema(FLOW_NAME),
    retention_snapshots.create_pg_sql_table_schema(FLOW_NAME),
]

__all__ = ["GeneratorConfig", "FLOW_SCHEMAS"]
