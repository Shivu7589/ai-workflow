from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_ENV_FILE = _PROJECT_ROOT / ".env"

def _parse_env_file(path: Path) -> dict[str, str]:
    """Parse a .env file into a dictionary."""
    if not path.exists():
        return {}
    out: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        value = value.strip().strip('"').strip("'")
        out[key.strip()] = value
    return out

@dataclass
class LLMSettings:
    provider: str = "mock"
    model: str = "gpt-3.5-turbo"
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    timeout_s: int = 30
    extra_headers: dict[str, str] = field(default_factory=dict)


def load_settings(**overrides) -> LLMSettings:
    merged: dict[str, str] = {}
    merged.update(_parse_env_file(_ENV_FILE))
    merged.update({k: v for k, v in os.environ.items() if k.startswith("LLM_")})

    def pick(key: str, default: Optional[str] = None) -> Optional[str]:
        return overrides.get(key.lower()) or merged.get(key) or default

    timeout_raw = pick("LLM_TIMEOUT_S", "30")
    try:
        timeout = float(timeout_raw) if timeout_raw is not None else 60.0
    except ValueError:
        timeout = 60.0

    return LLMSettings(
        provider=(pick("LLM_PROVIDER", "mock") or "mock").lower(),
        model=pick("LLM_MODEL", "gpt-3.5-turbo") or "gpt-3.5-turbo",
        base_url=pick("LLM_BASE_URL"),
        api_key=pick("LLM_API_KEY"),
        timeout_s=int(timeout),
    )