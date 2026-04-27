"""Generate enterprise flow data and load it into a local Postgres instance."""

import asyncio
import io

import typer
from pandas import DataFrame
from psycopg import AsyncCursor, sql

from adorable_thunder.make.database.database_connection import PgConnConfig
from adorable_thunder.make.record_generators.campaign_to_conversion import (
    FLOW_SCHEMAS as C2C_FLOW_SCHEMAS,
)
from adorable_thunder.make.record_generators.campaign_to_conversion import (
    GeneratorConfig as C2CGeneratorConfig,
)
from adorable_thunder.make.record_generators.lead_to_opportunity import (
    FLOW_SCHEMAS as L2O_FLOW_SCHEMAS,
)
from adorable_thunder.make.record_generators.lead_to_opportunity import (
    GeneratorConfig as L2OGeneratorConfig,
)
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
    (C2CGeneratorConfig, C2C_FLOW_SCHEMAS),
    (L2OGeneratorConfig, L2O_FLOW_SCHEMAS),
]

_FLOW_NAMES = [config.name for config, _ in ALL_FLOW_GENERATORS]


async def _grant_readonly_schema_access(cur: AsyncCursor, schema: str) -> None:
    await cur.execute(
        sql.SQL("GRANT USAGE ON SCHEMA {} TO ai_readonly_user").format(sql.Identifier(schema))
    )
    await cur.execute(
        sql.SQL("GRANT SELECT ON ALL TABLES IN SCHEMA {} TO ai_readonly_user").format(
            sql.Identifier(schema)
        )
    )


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

        await cur.execute(
            sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(sql.Identifier(fgc.name))
        )

        for create_sql_obj in sql_schemas:
            if drop:
                await cur.execute(
                    sql.SQL("DROP TABLE IF EXISTS {}.{} CASCADE").format(
                        sql.Identifier(create_sql_obj.pg_schema),
                        sql.Identifier(create_sql_obj.pg_table),
                    )
                )
            await cur.execute(create_sql_obj.sql_statement.encode())

        await _grant_readonly_schema_access(cur, fgc.name)

        for table, df in data.items():
            typer.echo(f"  {table}: {len(df)} rows")
            await _copy_df(cur, df, table, fgc.name)

    typer.echo("Done.")


def run_all(
    flow: str = typer.Option("procure_to_pay", help=f"Flow to generate: {_FLOW_NAMES}"),
    n_samples: int = 1000,
    drop: bool = typer.Option(False, "--drop", help="Drop and recreate tables before loading"),
) -> None:
    pg_conn_config = PgConnConfig()

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
    typer.run(run_all)
