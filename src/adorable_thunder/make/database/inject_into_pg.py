"""Generate enterprise flow data and load it into a local Postgres instance."""

import asyncio
import io
from typing import Callable

import typer
from psycopg import AsyncCursor, sql
from pandas import DataFrame

from adorable_thunder.make.database.database_connection import PgConnConfig
from adorable_thunder.make.record_generators.order_to_cash import FLOW_SCHEMAS as O2C_FLOW_SCHEMAS, GeneratorConfig as O2CGeneratorConfig
from adorable_thunder.make.record_generators.procure_to_pay import FLOW_SCHEMAS as P2P_FLOW_SCHEMAS, GeneratorConfig as P2PGeneratorConfig

app = typer.Typer()


async def _copy_df(cur: AsyncCursor, df: DataFrame, table: str, pg_schema: str) -> None:
    buf = io.StringIO()
    df.to_csv(buf, index=False, header=False)
    buf.seek(0)
    stmt = sql.SQL("COPY {}.{} FROM STDIN WITH CSV").format(
        sql.Identifier(pg_schema), sql.Identifier(table)
    )
    async with cur.copy(stmt) as copy:
        await copy.write(buf.getvalue().encode())


async def load_flow(
    flow: str,
    pg_schema: str,
    pg_conn_config: PgConnConfig,
    
    n_samples: int = 1000,
    drop: bool = False,
) -> None:
    typer.echo(f"Generating {n_samples} {flow} records...")
    data = _FLOW_GENERATORS[flow](n_samples=n_samples).make()
    schemas = _FLOW_SCHEMAS[flow]

    async with await pg_conn_config.get_psycopg_conn() as conn:
        cur = conn.cursor()

        for table, ddl_fn in schemas.items():
            if drop:
                await cur.execute(
                    sql.SQL("DROP TABLE IF EXISTS {}.{} CASCADE").format(
                        sql.Identifier(pg_schema), sql.Identifier(table)
                    )
                )
            await cur.execute(ddl_fn(pg_schema).encode())

        for table, df in data.items():
            typer.echo(f"  {table}: {len(df)} rows")
            await _copy_df(cur, df, table, pg_schema)

    typer.echo("Done.")


@app.command()
def run(
    pg_schema: str,
    pg_conn_config: PgConnConfig,
    flow: str = typer.Option("procure_to_pay", help=f"Flow to generate: {list(_FLOW_SCHEMAS)}"),
    n_samples: int = 1000,
    drop: bool = typer.Option(False, "--drop", help="Drop and recreate tables before loading"),
) -> None:
    if flow not in _FLOW_SCHEMAS:
        typer.echo(f"Unknown flow '{flow}'. Choose from: {list(_FLOW_SCHEMAS)}", err=True)
        raise typer.Exit(1)
    asyncio.run(load_flow(flow, pg_schema, pg_conn_config, n_samples, drop))


if __name__ == "__main__":
    app()
