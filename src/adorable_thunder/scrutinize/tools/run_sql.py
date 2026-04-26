import json

from langchain_core.tools import tool  # type: ignore[reportUnknownVariableType]
from psycopg import sql

from adorable_thunder.scrutinize.tools._db import get_conn

_MAX_ROWS = 200


@tool
async def run_sql(query: str) -> str:
    """Run a read-only SQL SELECT query and return results as JSON.

    Use this to sample rows, profile value distributions, check status ratios,
    validate date chains, or run any analytical query against the generated data.
    Results are capped at 200 rows. Only SELECT statements are permitted.

    Examples:
        SELECT status, COUNT(*) FROM procure_to_pay.requests GROUP BY status
        SELECT * FROM procure_to_pay.requests ORDER BY RANDOM() LIMIT 50
        SELECT MIN(request_date), MAX(request_date) FROM procure_to_pay.requests
    """
    if not query.strip().upper().startswith("SELECT"):
        return "Error: only SELECT queries are permitted."

    try:
        async with await get_conn() as conn:
            async with conn.cursor() as cur:
                await cur.execute(sql.SQL(query))  # type: ignore[arg-type]
                rows = await cur.fetchmany(_MAX_ROWS)
                cols = [desc[0] for desc in cur.description] if cur.description else []
    except Exception as e:
        return f"Error: {e}"

    records = [dict(zip(cols, row)) for row in rows]
    result: dict[str, object] = {"rows": records, "count": len(records)}
    if len(rows) == _MAX_ROWS:
        result["note"] = f"Results truncated at {_MAX_ROWS} rows."
    return json.dumps(result, default=str)
