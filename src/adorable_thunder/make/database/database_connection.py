import psycopg

from pydantic import BaseModel


class PgConnConfig(BaseModel):
    host: str = "localhost"
    user: str = "ai_readonly_user"
    password: str = "not-a-password123!@#"
    dbname: str = "adorable_thunder"
    port: int = 5432

    async def get_psycopg_conn(self) -> psycopg.AsyncConnection:
        return await psycopg.AsyncConnection.connect(
            host=self.host,
            port=self.port,
            dbname=self.dbname,
            user=self.user,
            password=self.password,
        )