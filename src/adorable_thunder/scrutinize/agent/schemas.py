from typing import Literal

from pydantic import BaseModel


class Finding(BaseModel):
    field: str
    issue: str
    suggestion: str
    severity: Literal["low", "medium", "high"]


class ScrutinyReport(BaseModel):
    flow: str
    row_count: int
    column_count: int
    findings: list[Finding]
    summary: str
