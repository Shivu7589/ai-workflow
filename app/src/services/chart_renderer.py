from __future__ import annotations

from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from app.src.models.chart_schemas import ChartConfig, Filter

_OPS = {
    "eq": lambda s, v: s == v,
    "ne": lambda s, v: s != v,
    "gt": lambda s, v: s > v,
    "gte": lambda s, v: s >= v,
    "lt": lambda s, v: s < v,
    "lte": lambda s, v: s <= v,
    "in": lambda s, v: s.isin(v if isinstance(v, list) else [v]),
    "contains": lambda s, v: s.astype(str).str.contains(str(v), case=False, na=False),
}

def _apply_filters(df: pd.DataFrame, filters: list[Filter]) -> pd.DataFrame:
    out = df
    for f in filters:
        if f.column not in out.columns:
            raise ValueError(f"Filter column '{f.column}' not in dataset.")
        out = out[_OPS[f.op](out[f.column], f.value)]
    return out

def _apply_aggregation(df: pd.DataFrame, cfg: ChartConfig) -> pd.DataFrame:
    agg = cfg.aggregation
    if agg is None:
        return df
    group_by = agg.group_by or [
        c for c in (cfg.mapping.x, cfg.mapping.color) if c and c != agg.column
    ]
    if not group_by:
        return df
    func = "size" if agg.func == "count" else agg.func
    grouped = df.groupby(group_by, dropna=False)[agg.column].agg(func).reset_index()
    return grouped

def _build_figure(df: pd.DataFrame, cfg: ChartConfig) -> go.Figure:
    m = cfg.mapping
    kwargs: dict[str, Any] = {"title": cfg.title}

    if cfg.chart_type == "bar":
        return px.bar(df, x=m.x, y=m.y, color=m.color, **kwargs)
    if cfg.chart_type == "line":
        return px.line(df, x=m.x, y=m.y, color=m.color, **kwargs)
    if cfg.chart_type == "scatter":
        return px.scatter(df, x=m.x, y=m.y, color=m.color, size=m.size, **kwargs)
    if cfg.chart_type == "pie":
        names = m.names or m.x
        values = m.values or m.y
        return px.pie(df, names=names, values=values, **kwargs)
    if cfg.chart_type == "histogram":
        return px.histogram(df, x=m.x, color=m.color, **kwargs)
    if cfg.chart_type == "box":
        return px.box(df, x=m.x, y=m.y, color=m.color, **kwargs)
    return ValueError(f"Unsupported chart_type: {cfg.chart_type}")

def render(df: pd.DataFrame, cfg: ChartConfig) -> go.Figure:
    shaped = _apply_filters(df, cfg.filters)
    shaped = _apply_aggregation(shaped, cfg)
    if shaped.empty:
        return ValueError("No data left after filters/aggregation.")
    return _build_figure(shaped, cfg)
