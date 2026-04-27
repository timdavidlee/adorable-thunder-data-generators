import asyncio
import os

import asyncpg
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("postgres")

DB_CONFIG = {
    "host": os.environ.get("PG_HOST", "localhost"),
    "port": int(os.environ.get("PG_PORT", "5432")),
    "user": os.environ["PG_USER"],
    "password": os.environ["PG_PASSWORD"],
    "database": os.environ["PG_DBNAME"],
}


async def _get_conn() -> asyncpg.Connection:
    return await asyncpg.connect(**DB_CONFIG)


@mcp.tool()
async def list_tables() -> list[str]:
    """List all tables in the public schema."""
    conn = await _get_conn()
    try:
        rows = await conn.fetch(
            "SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename"
        )
        return [row["tablename"] for row in rows]
    finally:
        await conn.close()


@mcp.tool()
async def run_sql(query: str) -> list[dict]:
    """Run a read-only SQL query and return results as a list of dicts."""
    conn = await _get_conn()
    try:
        rows = await conn.fetch(query)
        return [dict(row) for row in rows]
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(mcp.run_async())
