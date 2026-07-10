# OpenProcurementHub

**Open procurement infrastructure for Europe.**

OpenProcurementHub is a Docker-first, API-first interoperability platform for ingesting public procurement data, normalizing it into a canonical model, indexing it, and exposing it through REST APIs, SDKs, webhooks, and a professional CLI.

## Why Apache-2.0

Apache-2.0 is permissive, business-friendly, compatible with public-sector and commercial adoption, and includes an explicit patent grant. That makes it appropriate for shared European infrastructure.

## Quick start

```bash
cp .env.example .env
docker compose -f docker/docker-compose.yml up --build
```

## Repository layout

- `packages/core`: canonical domain model, configuration, events, database and observability primitives.
- `packages/api`: FastAPI application exposing `/api/v1`.
- `packages/cli`: Typer CLI (`oph`).
- `packages/connector-sdk`: plugin interface for source connectors.
- `packages/connector-belgium`: Belgian federal procurement connector.
- `packages/sdk-python`: Python SDK.
- `packages/sdk-typescript`: TypeScript SDK.
- `docs`: MkDocs Material documentation.

## Development

```bash
python -m pip install -e packages/core -e packages/connector-sdk -e packages/connector-belgium -e packages/api -e packages/cli -e packages/sdk-python
pytest
ruff check .
mypy packages
```
