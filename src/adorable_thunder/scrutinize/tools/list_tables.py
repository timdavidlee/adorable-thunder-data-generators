from collections import defaultdict

from langchain_core.tools import tool  # type: ignore[reportUnknownVariableType]

from adorable_thunder.scrutinize.tools._db import get_conn


@tool
async def list_tables() -> str:
    """List all schemas and tables in the database with their columns and data types.

    Call this first to discover what data is available before running queries.
    """
    async with await get_conn() as conn:
        async with conn.cursor() as cur:
            await cur.execute("""
                SELECT table_schema, table_name, column_name, data_type
                FROM information_schema.columns
                WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
                ORDER BY table_schema, table_name, ordinal_position
            """)
            rows = await cur.fetchall()

    if not rows:
        return "No tables found."

    tables: dict[str, list[str]] = defaultdict(list)
    for schema, table, column, dtype in rows:
        tables[f"{schema}.{table}"].append(f"{column} ({dtype})")

    lines: list[str] = []
    for table_name, columns in sorted(tables.items()):
        lines.append(table_name)
        for col in columns:
            lines.append(f"  - {col}")
    return "\n".join(lines)
