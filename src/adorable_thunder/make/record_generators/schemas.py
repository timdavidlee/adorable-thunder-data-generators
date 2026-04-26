import inspect
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, ClassVar

import pandas as pd
from pydantic import BaseModel


class CreatePgTableSql(BaseModel):
    pg_schema: str
    pg_table: str
    pg_columns: list[str]

    @property
    def sql_statement(self) -> str:
        columns = ",\n    ".join(self.pg_columns)
        return f"CREATE TABLE IF NOT EXISTS {self.pg_schema}.{self.pg_table} (\n    {columns}\n);"


class BaseGeneratorConfig(ABC, BaseModel):
    name: ClassVar[str]
    n_samples: int = 1000

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        if not inspect.isabstract(cls) and "name" not in cls.__dict__:
            raise TypeError(f"{cls.__name__} must define class attribute 'name'")

    @abstractmethod
    def make(self) -> dict[str, pd.DataFrame]:
        """primary construction function of data"""
        pass

    def make_in_dir(self) -> None:
        out_dir = Path(self.name)
        out_dir.mkdir(parents=True, exist_ok=True)
        for table_name, df in self.make().items():
            df.to_parquet(out_dir / f"{table_name}.parquet", index=False)
