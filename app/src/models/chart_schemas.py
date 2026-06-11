from __future__ import annotations

from typing import Any, List, Literal, Optional

from pydantic import BaseModel, Field

ChartType = Literal["bar", "line", "scatter", "pie", "histogram", "box"]
AggFunc = Literal["sum", "mean", "min", "max", "count", "median"]
FilterOp = Literal["eq", "ne", "gt", "gte", "lt", "lte", "in", "contains"]
OutputFormat = Literal["html", "json", "png"]

class Mapping(BaseModel):
    x: Optional[str] = None
    y: Optional[str] = None
    color: Optional[str] = None
    size: Optional[str] = None
    names: Optional[str] = None
    values: Optional[str] = None

class Aggregation(BaseModel):
    column: str
    func: AggFunc = "sum"
    group_by: Optional[List[str]] = None

class Filter(BaseModel):
    column: str
    op: FilterOp = "eq"
    value: Any

class ChartConfig(BaseModel):
    chart_type: ChartType
    title: Optional[str] = None
    mapping: Mapping = Field(default_factory=Mapping)
    aggregation: Optional[Aggregation] = None
    filters: List[Filter] = Field(default_factory=list)
    output: OutputFormat = "html"

class DatasetInfo(BaseModel):
    name: str
    rows: int
    columns: List[str]
    dtypes: dict