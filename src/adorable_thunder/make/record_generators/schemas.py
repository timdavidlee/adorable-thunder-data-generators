import pandas as pd
from abc import ABC, abstractmethod
from pathlib import Path
from pydantic import BaseModel
    

class CreatePgTableSql(BaseModel):
    pg_schema: str
    pg_table: str
    pg_columns: list[str]

    @property
    def sql_statement(self) -> str:
        columns = ",\n    ".join(self.pg_columns)
        return f"CREATE TABLE {self.pg_schema}.{self.pg_table} (\n    {columns}\n);"
    

class BaseGeneratorConfig(ABC, BaseModel):
    @abstractmethod
    def name(self) -> str:
        """
        should fill in a of the flow such as `procure_to_pay`
        - should be compatible for dirname
        - should be compatible for SQL schema name
        """
        pass

    @abstractmethod
    def make(self) -> dict[str, pd.DataFrame]:
        """primary construction function of data"""
        pass

    
    def make_in_dir(self) -> None:
        out_dir = Path(self.name())
        out_dir.mkdir(parents=True, exist_ok=True)
        for name, df in self.make().items():
            df.to_parquet(out_dir / f"{name}.parquet", index=False)