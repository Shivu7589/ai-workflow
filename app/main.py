"""uvicorn app.main:app --reload --port 8000"""

from __future__ import annotations

from fastapi import FastAPI

from app.src.api import charts as chart_api
from app.src.api import health as health_api

def create_app() -> FastAPI:
    app = FastAPI(
        title="Lite Chart Studio",
        description=(
            "Lightweight, stateles charting tool. Each request brings its own "
            "data file plus either a JSON chart config or a natural-language "
            "prompt. No org-specific dependencies."
        ),
        version="0.4.0",
    )
    app.include_router(health_api.router)
    app.include_router(chart_api.router)
    return app

app = create_app()