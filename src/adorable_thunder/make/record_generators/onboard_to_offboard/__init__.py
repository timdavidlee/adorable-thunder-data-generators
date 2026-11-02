from adorable_thunder.make.record_generators.schemas import CreatePgTableSql

from . import (
    accounts,
    branches,
    clients,
    loans,
    monthly_activity,
    plan_changes,
    tariff_plans,
)
from .flow import FLOW_NAME, GeneratorConfig

FLOW_SCHEMAS: list[CreatePgTableSql] = [
    branches.create_pg_sql_table_schema(FLOW_NAME),
    tariff_plans.create_pg_sql_table_schema(FLOW_NAME),
    clients.create_pg_sql_table_schema(FLOW_NAME),
    accounts.create_pg_sql_table_schema(FLOW_NAME),
    plan_changes.create_pg_sql_table_schema(FLOW_NAME),
    monthly_activity.create_pg_sql_table_schema(FLOW_NAME),
    loans.create_pg_sql_table_schema(FLOW_NAME),
]

__all__ = ["GeneratorConfig", "FLOW_SCHEMAS"]
