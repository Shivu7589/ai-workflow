from __future__ import annotations

import json
from typing import Optional

import pandas as pd

from app.src.config.llm_client import LLMClient, get_client
from app.src.models.chart_schemas import ChartConfig
from app.src.utils.json_utils import extract_json

SYSTEM_PROMPT = """You translate analytics requests into JSON chart configs.

Return a single JSON object - no prose, no markdown fences - matching this schema:

{
    "chart_type": "bar"|"line"|"scatter"|"pie"|"histogram"|"box",
    "title": string,  // optional
    "mapping": {
        "x": string?,       // column name for x-axis
        "y": string?,       // column name for y-axis
        "color": string?,   // optional column name for color grouping
        "size": string?,    // optional column name for point size (scatter only)
        "names": string?,   // optional column name for category names (pie only)
        "values": string?,  // optional column name for values (pie only)
    },
    "aggregation": {      // optional aggregation instruction
        "column": string,  // column to aggregate
        "func": "sum"|"mean"|"min"|"max"|"count"|"median",
        "group_by": [string]? // optional list of columns to group by (defaults to x and color)
    } | null,
    "filters": [         // optional list of filters to apply before plotting
        {
            "column": string, // column name to filter on
            "op": "eq"|"ne"|"gt"|"gte"|"lt"|"lte"|"in"|"contains",
            "value": any       // value to compare against (type depends on column)
        },
    ],
    "output": "html"|"json"|"png"
}

Rules:
- Use only column names listed under COLUMNS.
- Choose chart_type based on the question: distributions -> histogram/box, parts of a
whole -> pie, trends over an ordered axis -> line, comparisons across categories -> bar,
relationships between two numeric columns -> scatter.
- Aggregate when the x-axis has duplicate values (e.g. summing revenue per region).
- Default `output` to `html` unless the user explicitly asks for a different format.
- If the request is ambiguous, use your best judgement to choose a reasonable config based on the dataset and question.
"""

def _summarise_dataset(df: pd.DataFrame, sample_rows: int = 5) -> str:
    cols = list(df.columns)
    dtypes = { c: str(t) for c, t in df.dtypes.items() }
    sample = df.head(sample_rows).to_dict(orient="records")
    return (
        f"COLUMNS: {json.dumps(cols)}\n"
        f"DTYPES: {json.dumps(dtypes)}\n"
        f"SAMPLE_ROWS: {json.dumps(sample, default=str)}\n"
    )

def generate_config(
    prompt: str,
    df: pd.DataFrame,
    *,
    client: Optional[LLMClient] = None,
) -> ChartConfig:
    llm = client or get_client()
    user_message = (
        f"{_summarise_dataset(df)}"
        f"USER_REQUEST: {prompt.strip()}\n"
    )
    raw = llm.complete(SYSTEM_PROMPT, user_message)
    data = extract_json(raw)
    return ChartConfig(**data)