"""Chart endpoints - direct path and AI path. All multipart, all stateless."""
from __future__ import annotations

import json
from typing import Literal, Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse, HTMLResponse, Response

from app.src.models.chart_schemas import ChartConfig
from app.src.services import ai_config_generator, chart_renderer, datasource_loader

router = APIRouter(prefix="/charts", tags=["charts"])

# ---------------------------------------------------------------- #
# Helpers
# ---------------------------------------------------------------- #
async def _load_upload(file: UploadFile) -> str:
    """Load the content of an uploaded file as a string."""
    try:
        return datasource_loader.load_bytes(await file.read(), file.filename or "upload")
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to load file: {exc}") from exc

def _figure_response(fig, output: str):
    """Convert a Plotly figure to the desired output format."""
    if output == "json":
        return JSONResponse(content=json.loads(fig.to_json()))
    if output == "png":
        try:
            png = fig.to_image(format="png")
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"PNG export requries the 'kaleido' package: {exc}") from exc
        return Response(content=png, media_type="image/png")
    return HTMLResponse(content=fig.to_html(include_plotlyjs="cdn", full_html=True))

def _parse_config(raw: str) -> ChartConfig:
    """Parse a raw JSON string into a ChartConfig object."""
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail=f"Config is not valid JSON: {exc}") from exc
    try:
        return ChartConfig(**data)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Invalid ChartConfig: {exc}") from exc

# ---------------------------------------------------------------- #
# Direct chart rendering 
# ---------------------------------------------------------------- #
@router.post("/render")
async def render_chart(
    file: UploadFile = File(..., description="Data file (CSV or JSON)"),
    config: str = Form(..., description="Chart configuration as JSON string"),
):
    df, _ = await _load_upload(file)
    cfg = _parse_config(config)
    try:
        fig = chart_renderer.render(df, cfg)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _figure_response(fig, cfg.output)

# ---------------------------------------------------------------- #
# AI-generated config and rendering
# ---------------------------------------------------------------- #
@router.post("/ai-config", response_model=ChartConfig)
async def ai_config(
    file: UploadFile = File(..., description="Data file (CSV or JSON)"),
    prompt: str = Form(..., description="Natural-language description of a chart"),
    output: Optional[Literal["html", "json", "png"]] = Form(None, description="Optional override for the config's output format.")
):
    df, _ = await _load_upload(file)
    try:
        cfg = ai_config_generator.generate_config(prompt, df)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return cfg

@router.post("/ai-render")
async def ai_render(
    file: UploadFile = File(..., description="Data file (CSV or JSON)"),
    prompt: str = Form(..., description="Natural-language description of a chart"),
    output: Optional[Literal["html", "json", "png"]] = Form(None, description="Optional override for the config's output format.")
):
    df, _ = await _load_upload(file)
    try:
        cfg = ai_config_generator.generate_config(prompt, df)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"LLM COnfig generation failed: {exc}") from exc
    if output:
        cfg.output = output  # Override output if specified
    try:
        fig = chart_renderer.render_chart(df, cfg)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _figure_response(fig, cfg.output)