from adorable_thunder.make.record_generators.schemas import CreatePgTableSql

from . import campaigns, conversions, engagement_events, impressions, lead_captures
from .flow import FLOW_NAME, GeneratorConfig

FLOW_SCHEMAS: list[CreatePgTableSql] = [
    campaigns.create_pg_sql_table_schema(FLOW_NAME),
    impressions.create_pg_sql_table_schema(FLOW_NAME),
    engagement_events.create_pg_sql_table_schema(FLOW_NAME),
    lead_captures.create_pg_sql_table_schema(FLOW_NAME),
    conversions.create_pg_sql_table_schema(FLOW_NAME),
]

__all__ = ["GeneratorConfig", "FLOW_SCHEMAS"]
