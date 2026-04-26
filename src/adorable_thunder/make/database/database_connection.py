import os

import pandas as pd
import psycopg
from psycopg.abc import Query
from pydantic import Field
from pydantic import BaseModel


class PgConnConfig(BaseModel):
    host: str = Field(default_factory=lambda: os.environ.get("PG_HOST", "localhost"))
    user: str = Field(default_factory=lambda: os.environ.get("PG_USER", "ai_readonly_user"))
    password: str = Field(default_factory=lambda: os.environ.get("PG_PASSWORD", "not-a-password123!@#"))
    dbname: str = Field(default_factory=lambda: os.environ.get("PG_DBNAME", "adorable_thunder"))
    port: int = Field(default_factory=lambda: int(os.environ.get("PG_PORT", "5432")))

    async def get_psycopg_conn(self) -> psycopg.AsyncConnection:
        return await psycopg.AsyncConnection.connect(
            host=self.host,
            port=self.port,
            dbname=self.dbname,
            user=self.user,
            password=self.password,
        )


async def copy_serialized_csv(df: pd.DataFrame, copy_statement: Query, cursor: psycopg.AsyncCursor):
    buf = df.to_csv(index=False, header=False).encode()
    async with cursor.copy(statement=copy_statement) as copy:
        await copy.write(buf)
