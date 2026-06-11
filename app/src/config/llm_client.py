"""Pluggable LLM Client

Supported providers:

* ``openai``: OpenAI's API (GPT-3.5, GPT-4, etc.)
* ``azure``: Azure OpenAI Service (GPT-3.5, GPT-4

All providers share one interface:
   client.complete(system: str, user: str) -> str

We intentially talk HTTP directly via ``httpx`` instead of using provider SDKs, to keep the client lightweight and avoid unnecessary dependencies.
"""
from __future__ import annotations
import json
from typing import Protocol

import httpx

from app.src.config.settings import LLMSettings, load_settings

class LLMClient(Protocol):
    def complete(self, system: str, user: str) -> str: ...

class OpenAICompatibleClient:
    def __init__(self, settings: LLMSettings, default_base: str):
        self._settings = settings
        self._base = (settings.base_url or default_base).rstrip("/")

    def complete(self, system: str, user: str) -> str:
        headers = {"Content-Type": "application/json"}
        if self._settings.api_key:
            headers["Authorization"] = f"Bearer {self._settings.api_key}"

        payload = {
            "model": self._settings.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
        }

        with httpx.Client(timeout=self._settings.timeout_s) as client:
            response = client.post(f"{self._base}/chat/completions", headers=headers, json=payload)
        if response.status_code >= 400:
            raise RuntimeError(f"LLM API error {response.status_code}: {response.text}")
        data = response.json()
        return data["choices"][0]["message"]["content"]


class MockClient:
    """Returns a heuristic ChartCounting JSON Based on dataset hints in the prompt.
    """
    def __init__(self, settings: LLMSettings):
        self._settings = settings

    def complete(self, system: str, user: str) -> str:
        cols_raw = _extract(user, "COLUMNS:") or "[]"
        try:
            cols = json.loads(cols_raw)
        except Exception:
            cols = []
        text = user.lower()
        chart_type = "line" if any(k in text for k in ["trend", "over time", "line"]) else "bar"
        x = cols[0] if cols else "x"
        y = cols[1] if len(cols) > 1 else "y"
        color = cols[2] if len(cols) > 2 else None
        cfg = {
            "chart_type": chart_type,
            "title": "Mock Chart",
            "mappings": {"x": x, "y": y, **({"color": color} if color else {})},
            "aggregation": {"column": y, "func": "sum"},
            "filters": [],
            "output": "html",
        }
        return json.dumps(cfg)

def _extract(text: str, prefix: str) -> str | None:
    """Extracts the substring following a prefix, if present."""
    idx = text.find(prefix)
    if idx < 0:
        return None
    return text[idx + len(prefix):].splitlines()[0].strip()

def get_client(settings: LLMSettings | None = None) -> LLMClient:
    s = settings or load_settings()
    provider = s.provider.lower()
    if provider == "openai":
        return OpenAICompatibleClient(s, default_base="https://api.openai.com/v1")
    if provider == "mock":
        return MockClient(s)
    raise ValueError(f"Unsupported LLM provider: {provider}")