from adorable_thunder.make.record_generators.schemas import CreatePgTableSql

from . import (
    cycle_counts,
    inbound_shipments,
    outbound_shipments,
    pick_lists,
    receipt_lines,
    storage_locations,
)
from .flow import FLOW_NAME, GeneratorConfig

FLOW_SCHEMAS: list[CreatePgTableSql] = [
    storage_locations.create_pg_sql_table_schema(FLOW_NAME),
    inbound_shipments.create_pg_sql_table_schema(FLOW_NAME),
    receipt_lines.create_pg_sql_table_schema(FLOW_NAME),
    pick_lists.create_pg_sql_table_schema(FLOW_NAME),
    outbound_shipments.create_pg_sql_table_schema(FLOW_NAME),
    cycle_counts.create_pg_sql_table_schema(FLOW_NAME),
]

__all__ = ["GeneratorConfig", "FLOW_SCHEMAS"]
