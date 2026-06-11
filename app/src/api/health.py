from __future__ import annotations

from fastapi import APIRouter

from app.src.config.settings import load_settings

router = APIRouter(tags=["meta"])

@router.get("/health")
def health() -> dict:
    return {"status": "ok"}

@router.get("/llm/config")
def llm_config() -> dict:
    settings = load_settings()
    return {
        "provider": settings.provider,
        "model": settings.model,
        "base_url": settings.base_url,
        "api_key_set": bool(settings.api_key),
    }