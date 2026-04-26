import inspect
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, ClassVar

import pandas as pd
from pydantic import BaseModel


class PgColumn(BaseModel):
    """
    then name will be the column name,
    and the suffix will any of the modifiers
    """

    name: str
    data_type: str
    modifiers: str
    llm_description: str = "N/A"
    llm_example_values: str = "N/A"

    @property
    def sql_row(self):
        return f"{self.name} {self.data_type} {self.modifiers}"
    
    @property
    def llm_desc(self):
        return f"{self.name} ({self.data_type}):\n\t{self.llm_description}\n\t{self.llm_example_values}"


class CreatePgTableSql(BaseModel):
    pg_schema: str
    pg_table: str
    pg_columns: list[PgColumn]
    llm_description: str = "N/A"

    @property
    def sql_statement(self) -> str:
        columns = ",\n    ".join([c.sql_row for c in self.pg_columns])
        return f"CREATE TABLE IF NOT EXISTS {self.pg_schema}.{self.pg_table} (\n    {columns}\n);"

    @property
    def copy_statement(self) -> str:
        columns = ", ".join([c.name for c in self.pg_columns])
        return f"COPY {self.pg_schema}.{self.pg_table} ({columns}) FROM stdin;"


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
