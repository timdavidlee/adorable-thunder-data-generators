from adorable_thunder.make.record_generators.schemas import CreatePgTableSql

from . import assets, depreciation_runs, disposals
from .flow import FLOW_NAME, GeneratorConfig

FLOW_SCHEMAS: list[CreatePgTableSql] = [
    assets.create_pg_sql_table_schema(FLOW_NAME),
    depreciation_runs.create_pg_sql_table_schema(FLOW_NAME),
    disposals.create_pg_sql_table_schema(FLOW_NAME),
]

__all__ = ["GeneratorConfig", "FLOW_SCHEMAS"]
