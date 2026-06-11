# Lite Chart Studio

Lite Chart Studio is a lightweight, stateless charting tool that converts CSV or JSON datasets into Plotly visualizations.
It supports direct chart rendering from a JSON config, AI-assisted chart config generation from natural-language prompts, and both CLI and HTTP API access.

## Features

- Direct chart rendering from data + JSON `ChartConfig`
- AI prompt → config generation using an LLM-compatible provider
- HTML, JSON, and PNG output formats
- CSV and JSON datasource support
- FastAPI-based REST API plus CLI commands for local use
- Minimal external dependencies and stateless execution

## Quick start

### Install

```bash
python -m pip install -r requirements.txt
```

### Run CLI commands

Render with a chart config file:

```bash
python -m app.cli render --data examples/sales.csv --config examples/config_bar.json --out chart.html
```

Generate an AI chart config and render it:

```bash
python -m app.cli ai-render --data examples/sales.csv --prompt "revenue by region" --out chart.html
```

Generate an AI chart config only:

```bash
python -m app.cli ai-config --data examples/sales.csv --prompt "revenue by region" --out ai-config.json
```

### Run the web API

```bash
uvicorn app.main:app --reload --port 8000
```

Then browse the interactive Swagger docs at:

```
http://127.0.0.1:8000/docs
```

## API endpoints

- `GET /health` — service status check
- `GET /llm/config` — current LLM provider settings (non-sensitive)
- `POST /charts/render` — upload `file` and `config` to render a chart
- `POST /charts/ai-config` — upload `file` and `prompt` to receive generated chart config
- `POST /charts/ai-render` — upload `file` and `prompt` to render a chart using the generated config

## Configuration

Lite Chart Studio uses `app/src/config/settings.py` to load LLM settings from environment variables or an optional `.env` file.

Supported environment variables:

- `LLM_PROVIDER` — `mock` (default) or `openai`
- `LLM_MODEL` — model name, e.g. `gpt-3.5-turbo`
- `LLM_BASE_URL` — custom base URL for API-compatible providers
- `LLM_API_KEY` — API key for the chosen provider
- `LLM_TIMEOUT_S` — request timeout in seconds

### Example `.env`

```text
LLM_PROVIDER=openai
LLM_MODEL=gpt-3.5-turbo
LLM_API_KEY=your_api_key_here
LLM_TIMEOUT_S=30
```

## Project structure

- `app/cli.py` — command-line interface
- `app/main.py` — FastAPI app factory
- `app/src/api/` — REST API routes
- `app/src/services/` — data loading, rendering, and AI config generation
- `app/src/models/` — Pydantic chart schemas
- `app/src/config/` — LLM client and settings
- `examples/` — sample dataset and config files
- `tests/` — automated tests

## Examples

- `examples/sales.csv`
- `examples/weather.json`
- `examples/config_bar.json`
- `examples/config_line.json`

## Notes

- `png` output requires the optional `kaleido` package. Install it with `pip install "kaleido>=0.2.1"` or `pip install .[png]` if packaging is configured.
- The default LLM provider is `mock`, which returns heuristic chart configs for offline development.

## Running tests

```bash
pytest -v
```
