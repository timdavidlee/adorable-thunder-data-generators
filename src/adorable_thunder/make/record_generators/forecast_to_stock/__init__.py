from adorable_thunder.make.record_generators.schemas import CreatePgTableSql

from . import forecasts, inventory_positions, replenishment_orders, stock_parameters
from .flow import FLOW_NAME, GeneratorConfig

FLOW_SCHEMAS: list[CreatePgTableSql] = [
    stock_parameters.create_pg_sql_table_schema(FLOW_NAME),
    forecasts.create_pg_sql_table_schema(FLOW_NAME),
    inventory_positions.create_pg_sql_table_schema(FLOW_NAME),
    replenishment_orders.create_pg_sql_table_schema(FLOW_NAME),
]

__all__ = ["GeneratorConfig", "FLOW_SCHEMAS"]
