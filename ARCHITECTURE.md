# Lite Chart Studio Architecture

## Purpose

Lite Chart Studio is a lightweight, stateless chart generation toolkit that transforms tabular CSV/JSON data into Plotly-based visualizations. It supports:
- direct rendering from a JSON chart configuration,
- AI-assisted config generation from natural-language prompts,
- HTTP API access and CLI usage.

## Core principles

- Stateless request handling: each request is self-contained with its own data payload and chart specification.
- Minimal external dependencies: uses FastAPI, Plotly, Pandas, and HTTPX only when an LLM provider is enabled.
- Clear separation between data ingestion, configuration, rendering, and optional AI assistance.

## High-level architecture

### 1. Entry points

- `app/cli.py`
  - CLI commands: `render`, `ai-render`, `ai-config`.
  - Loads data from a file path, optionally uses the LLM generator, then renders or outputs a chart.

- `app/main.py`
  - FastAPI application factory.
  - Registers API routes for health checks and chart operations.

### 2. API layer

- `app/src/api/charts.py`
  - `POST /charts/render`: upload a dataset and a JSON config string, then render a chart.
  - `POST /charts/ai-config`: upload a dataset and a prompt, then return an LLM-generated `ChartConfig`.
  - `POST /charts/ai-render`: upload a dataset and prompt, then generate config and render a chart.
  - Supports output types: HTML, JSON, PNG.

- `app/src/api/health.py`
  - `GET /health`: simple status endpoint.
  - `GET /llm/config`: returns current LLM provider settings without exposing raw secrets.

### 3. Data ingestion

- `app/src/services/datasource_loader.py`
  - Loads CSV and JSON files from bytes or filesystem paths.
  - Converts the payload into a Pandas `DataFrame`.
  - Normalizes JSON payloads that are either a list of records or `{ "data": [...] }`.
  - Provides dataset metadata through `DatasetInfo`.

### 4. Chart configuration schema

- `app/src/models/chart_schemas.py`
  - Defines `ChartConfig` with:
    - `chart_type`,
    - `title`,
    - `mapping`,
    - optional `aggregation`,
    - optional `filters`,
    - output format.
  - Includes typed schema elements for aggregation, filtering, and supported chart types.

### 5. Rendering pipeline

- `app/src/services/chart_renderer.py`
  - Applies filters and aggregation to the dataset.
  - Builds Plotly figures for `bar`, `line`, `scatter`, `pie`, `histogram`, and `box`.
  - Validates dataset columns and raises clear errors for invalid filters or unsupported chart types.

### 6. AI-assisted config generation

- `app/src/services/ai_config_generator.py`
  - Summarizes dataset columns, dtypes, and sample rows.
  - Sends a structured prompt to an LLM.
  - Extracts JSON from the LLM response and parses it into `ChartConfig`.

- `app/src/config/llm_client.py`
  - Defines the pluggable `LLMClient` interface.
  - Implements `OpenAICompatibleClient` for OpenAI-style HTTP chat completions.
  - Implements `MockClient` for offline testing and development.
  - Chooses provider based on environment configuration.

### 7. Configuration and settings

- `app/src/config/settings.py`
  - Loads settings from a `.env` file and environment variables.
  - Recognizes `LLM_PROVIDER`, `LLM_MODEL`, `LLM_BASE_URL`, `LLM_API_KEY`, and `LLM_TIMEOUT_S`.
  - Defaults to the `mock` provider when no provider is configured.

## Request flow

### Direct render flow

1. Receive dataset upload and JSON chart config.
2. Parse the dataset into a DataFrame.
3. Validate the config against `ChartConfig`.
4. Apply optional filters and aggregation.
5. Render a Plotly figure.
6. Return HTML/JSON/PNG output.

### AI render flow

1. Receive dataset upload and natural-language prompt.
2. Parse the dataset into a DataFrame.
3. Summarize dataset schema and sample rows.
4. Send prompt to the configured LLM provider.
5. Extract a JSON chart config from the LLM response.
6. Render the chart and return the requested output format.

## Repository structure

- `app/`
  - `cli.py`: command-line interface.
  - `main.py`: FastAPI app factory.
  - `serve.py`: optional Uvicorn launcher.

- `app/src/api/`
  - `charts.py`: chart endpoints.
  - `health.py`: health and LLM config endpoints.

- `app/src/config/`
  - `llm_client.py`: LLM provider integration.
  - `settings.py`: environment-based settings loader.

- `app/src/models/`
  - `chart_schemas.py`: Pydantic chart and dataset schemas.

- `app/src/services/`
  - `ai_config_generator.py`: natural-language config generation.
  - `chart_renderer.py`: data-to-Plotly rendering.
  - `datasource_loader.py`: CSV/JSON loading.

- `app/src/utils/`
  - `json_utils.py`: JSON extraction helpers.

- `examples/`
  - sample data and configuration artifacts.

- `tests/`
  - integration and functional tests.

## Deployment notes

- Run as CLI for local chart generation.
- Run as API server with Uvicorn for remote ingestion.
- Use the `mock` provider for offline testing.
- For real LLM usage, configure `LLM_PROVIDER=openai` and set `LLM_API_KEY`.
