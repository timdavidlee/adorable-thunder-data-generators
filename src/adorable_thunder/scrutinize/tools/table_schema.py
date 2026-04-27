from adorable_thunder.make.record_generators.schemas import CreatePgTableSql
from langchain_core.tools import tool  # type: ignore[reportUnknownVariableType]

_VALID_FLOWS = ["order-to-cash", "procure-to-pay"]


def _get_schemas(flow: str) -> list[CreatePgTableSql] | None:
    if flow == "procure-to-pay":
        from adorable_thunder.make.record_generators.procure_to_pay import FLOW_SCHEMAS

        return FLOW_SCHEMAS
    if flow == "order-to-cash":
        from adorable_thunder.make.record_generators.order_to_cash import FLOW_SCHEMAS

        return FLOW_SCHEMAS
    return None


def _render(schemas: list[CreatePgTableSql]) -> str:
    parts: list[str] = []
    for s in schemas:
        header = f"## {s.pg_schema}.{s.pg_table}\n{s.llm_description}"
        cols = "\n".join(f"  {c.llm_desc}" for c in s.pg_columns)
        parts.append(f"{header}\n\n### Columns\n{cols}")
    return "\n\n---\n\n".join(parts)


@tool
async def get_table_llm_annotations(flow: str) -> str:
    """Return LLM-friendly annotations for every table in a flow.

    Includes per-table description, column names, data types, what each column
    means, and representative example values. Call this alongside get_flow_brief
    before running SQL so you know what each field represents and what values to
    expect. This is author-written documentation, not the live database schema.

    Valid flow names: order-to-cash, procure-to-pay.
    """
    schemas = _get_schemas(flow)
    if schemas is None:
        return f"Unknown flow '{flow}'. Valid flows: {', '.join(_VALID_FLOWS)}"
    return _render(schemas)
