import os

import psycopg


async def get_conn() -> psycopg.AsyncConnection:
    return await psycopg.AsyncConnection.connect(
        host=os.environ.get("PG_HOST", "localhost"),
        port=int(os.environ.get("PG_PORT", "5432")),
        dbname=os.environ.get("PG_DBNAME", "adorable_thunder"),
        user=os.environ.get("PG_USER", "ai_readonly_user"),
        password=os.environ.get("PG_PASSWORD", "not-a-password123!@#"),
        options="-c default_transaction_read_only=on",
    )
