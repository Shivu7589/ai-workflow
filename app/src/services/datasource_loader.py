from __future__ import annotations

import io
import json
from pathlib import Path
from typing import Tuple

import pandas as pd

from app.src.models.chart_schemas import DatasetInfo


def _describe(df: pd.DataFrame, name: str) -> DatasetInfo:
    if df.empty:
        return ValueError("Dataset is empty.")
    return DatasetInfo(
        name=name,
        rows=len(df),
        columns=list(df.columns),
        dtypes={c: str(t) for c, t in df.dtypes.items()},
    )

def load_csv_bytes(content: bytes, name: str = "upload.csv") -> Tuple[pd.DataFrame, DatasetInfo]:
    df = pd.read_csv(io.BytesIO(content))
    return df, _describe(df, name)

def load_json_bytes(content: bytes, name: str = "upload.json") -> Tuple[pd.DataFrame, DatasetInfo]:
    payload = json.loads(content.decode("utf-8"))
    if isinstance(payload, dict) and "data" in payload:
        payload = payload["data"]
    if not isinstance(payload, list):
        raise ValueError("JSON datasource must be a list of records or {'data': [...]}.")
    df = pd.DataFrame(payload)
    return df, _describe(df, name)

def load_bytes(content: bytes, filename: str) -> Tuple[pd.DataFrame, DatasetInfo]:
    suffix = Path(filename).suffix.lower()
    if suffix == ".csv":
        return load_csv_bytes(content, filename)
    if suffix == ".json":
        return load_json_bytes(content, filename)
    raise ValueError(f"Unsupported file type: {suffix or '<none>'}")

def load_path(path: str | Path) -> Tuple[pd.DataFrame, DatasetInfo]:
    p = Path(path)
    return load_bytes(p.read_bytes(), p.name)