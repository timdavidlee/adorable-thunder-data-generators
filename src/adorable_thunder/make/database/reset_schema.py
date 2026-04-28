"""Drop and recreate a Postgres schema, re-creating the ai_readonly_user and grants."""

import asyncio
import os

import typer
from psycopg import AsyncCursor, sql

from adorable_thunder.make.database.database_connection import PgConnConfig

_AI_READONLY_USER = "ai_readonly_user"


async def _ensure_readonly_user(cur: AsyncCursor, dbname: str) -> None:
    await cur.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (_AI_READONLY_USER,))
    if not await cur.fetchone():
        password = os.environ.get("AI_READONLY_PASSWORD", "not-a-password123!@#")
        await cur.execute(
            sql.SQL("CREATE USER {} WITH PASSWORD %s").format(sql.Identifier(_AI_READONLY_USER)),
            (password,),
        )
    await cur.execute(
        sql.SQL("GRANT CONNECT ON DATABASE {} TO {}").format(
            sql.Identifier(dbname), sql.Identifier(_AI_READONLY_USER)
        )
    )


async def _grant_readonly_schema_access(cur: AsyncCursor, schema: str) -> None:
    await cur.execute(
        sql.SQL("GRANT USAGE ON SCHEMA {} TO {}").format(
            sql.Identifier(schema), sql.Identifier(_AI_READONLY_USER)
        )
    )
    await cur.execute(
        sql.SQL("GRANT SELECT ON ALL TABLES IN SCHEMA {} TO {}").format(
            sql.Identifier(schema), sql.Identifier(_AI_READONLY_USER)
        )
    )


async def reset_schema(schema: str, pg_conn_config: PgConnConfig) -> None:
    async with await pg_conn_config.get_psycopg_conn() as conn:
        cur = conn.cursor()

        typer.echo(f"Dropping schema '{schema}' CASCADE...")
        await cur.execute(
            sql.SQL("DROP SCHEMA IF EXISTS {} CASCADE").format(sql.Identifier(schema))
        )

        typer.echo(f"Creating schema '{schema}'...")
        await cur.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(schema)))

        typer.echo(f"Ensuring '{_AI_READONLY_USER}' exists with correct grants...")
        await _ensure_readonly_user(cur, pg_conn_config.dbname)
        await _grant_readonly_schema_access(cur, schema)

    typer.echo("Done.")


def run(
    schema: str = typer.Argument(..., help="Schema to drop and recreate"),
) -> None:
    asyncio.run(reset_schema(schema, PgConnConfig()))


if __name__ == "__main__":
    typer.run(run)
