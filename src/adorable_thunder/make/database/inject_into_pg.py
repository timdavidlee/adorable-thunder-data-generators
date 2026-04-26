"""Generate enterprise flow data and load it into a local Postgres instance."""

import asyncio
import io

import typer
from pandas import DataFrame
from psycopg import AsyncCursor, sql

from adorable_thunder.make.database.database_connection import PgConnConfig
from adorable_thunder.make.record_generators.order_to_cash import (
    FLOW_SCHEMAS as O2C_FLOW_SCHEMAS,
)
from adorable_thunder.make.record_generators.order_to_cash import (
    GeneratorConfig as O2CGeneratorConfig,
)
from adorable_thunder.make.record_generators.procure_to_pay import (
    FLOW_SCHEMAS as P2P_FLOW_SCHEMAS,
)
from adorable_thunder.make.record_generators.procure_to_pay import (
    GeneratorConfig as P2PGeneratorConfig,
)
from adorable_thunder.make.record_generators.schemas import (
    BaseGeneratorConfig,
    CreatePgTableSql,
)

ALL_FLOW_GENERATORS: list[tuple[type[BaseGeneratorConfig], list[CreatePgTableSql]]] = [
    (O2CGeneratorConfig, O2C_FLOW_SCHEMAS),
    (P2PGeneratorConfig, P2P_FLOW_SCHEMAS),
]

_FLOW_NAMES = [config.name for config, _ in ALL_FLOW_GENERATORS]

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
    flow_generator_config: type[BaseGeneratorConfig],
    sql_schemas: list[CreatePgTableSql],
    pg_conn_config: PgConnConfig,
    n_samples: int = 1000,
    drop: bool = False,
) -> None:
    typer.echo(f"Generating {n_samples} {flow_generator_config.name} records...")
    fgc = flow_generator_config(n_samples=n_samples)
    data = fgc.make()

    async with await pg_conn_config.get_psycopg_conn() as conn:
        cur = conn.cursor()

        for create_sql_obj in sql_schemas:
            if drop:
                await cur.execute(
                    sql.SQL("DROP TABLE IF EXISTS {}.{} CASCADE").format(
                        sql.Identifier(create_sql_obj.pg_schema),
                        sql.Identifier(create_sql_obj.pg_table),
                    )
                )
            await cur.execute(create_sql_obj.sql_statement.encode())

        for table, df in data.items():
            typer.echo(f"  {table}: {len(df)} rows")
            await _copy_df(cur, df, table, fgc.name)

    typer.echo("Done.")


@app.command()
def run_all(
    pg_conn_config: PgConnConfig | None = None,
    flow: str = typer.Option("procure_to_pay", help=f"Flow to generate: {_FLOW_NAMES}"),
    n_samples: int = 1000,
    drop: bool = typer.Option(False, "--drop", help="Drop and recreate tables before loading"),
) -> None:
    pg_conn_config = pg_conn_config or PgConnConfig()

    for generator_config, flow_schemas in ALL_FLOW_GENERATORS:
        if flow != generator_config.name:
            continue

        asyncio.run(
            load_flow(
                flow_generator_config=generator_config,
                sql_schemas=flow_schemas,
                pg_conn_config=pg_conn_config,
                n_samples=n_samples,
                drop=drop,
            )
        )


if __name__ == "__main__":
    app()
