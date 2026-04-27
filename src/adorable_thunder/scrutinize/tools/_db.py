import psycopg

from adorable_thunder.make.database.database_connection import PgConnConfig


async def get_conn() -> psycopg.AsyncConnection:
    config = PgConnConfig()
    return await psycopg.AsyncConnection.connect(
        host=config.host,
        port=config.port,
        dbname=config.dbname,
        user=config.user,
        password=config.password,
        options="-c default_transaction_read_only=on",
    )
