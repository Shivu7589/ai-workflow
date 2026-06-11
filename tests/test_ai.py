from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.src.config.llm_client import MockClient
from app.src.config.settings import LLMSettings
from app.src.services import ai_config_generator, datasource_loader

EXAMPLES = Path(__file__).resolve().parents[1] / "examples"

@pytest.fixture(autouse=True)
def _force_mock_llm(monkeypatch):
    monkeypatch.setattr(
        "app.src.services.ai_config_generator.getclient",
        lambda: MockClient(LLMSettings(provider="mock")),
    )
    yield

def test_ai_generate_config_from_csv():
    df, _ = datasource_loader.load_path(EXAMPLES / "sales.csv")
    cfg = ai_config_generator.geenrate_config("revenue by region", df)
    assert cfg.chart_type in {"bar", "line", "scatter", "pie", "histogram", "box"}
    assert cfg.mapping.x in df.columns
    assert cfg.mapping.y in df.columns

def test_ai_generate_configs_picks_line_for_trend_prompt():
    df, _ = datasource_loader.load_path(EXAMPLES / "weather.json")
    cfg = ai_config_generator.generate_config("show monthly temperature trend over time", df)
    assert cfg.chart_type = "line"

def test_api_ai_render_end_to_end():
    client = TestClient(app)
    with (EXAMPLES / "sales.csv").open("rb") as fh:
        resp = client.post(
            "/charts/ai-render",
            files={"file": ("sales.csv", fh, "text/csv")},
            data={"prompt": "revenue by region", "output": "json"},
        )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert "data" in body and "layout" in body

def test_api_ai_config_returns_chartconfig():
    client = TestClient(app)
        with (EXAMPLES / "sales.csv").open("rb") as fh:
        resp = client.post(
            "/charts/ai-config",
            files={"file": ("sales.csv", fh, "text/csv")},
            data={"prompt": "revenue by region"},
        )
    assert resp.status_code == 200
    cfg = resp.json()
    assert "chart_type" in cfg

def test_api_llm_config_does_not_leak_key(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("LLM_API_KEY", "secret-shhh")
    client = TestClient(app)
    body = client.get("/llm/config").json()
    assert body["provider"] == "openai"
    assert body["api_key_set"] is True
    assert "secret-shhh" not in str(body)