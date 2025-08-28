# AI-powered Survey Generator

This project provides a small FastAPI service and a minimal React frontend that can generate surveys using an LLM provider. The backend stores generated surveys in PostgreSQL with idempotent lookup based on a normalized description hash. A deterministic mock provider is included so the stack works without API keys.

## Why FastAPI

FastAPI offers async support, type hints with Pydantic v2, and very fast development experience compared to traditional Flask. Validation, automatic docs and dependency injection simplify building reliable APIs.

## Backend features

* FastAPI 3.11 application with structured logging (structlog)
* Idempotent survey generation – repeated descriptions return cached surveys
* Provider abstraction for OpenAI/OpenRouter/Together with a mock fallback
* SQLAlchemy ORM + Alembic migrations storing surveys in PostgreSQL JSONB
* Optional bearer token auth and simple in-memory rate limiting
* Pydantic schemas guaranteeing valid survey JSON
* Dockerised with Postgres and Makefile helpers
* Comprehensive tests using pytest & httpx

## Setup

### Docker

```bash
cd backend
cp .env.example .env
make up  # starts api and postgres
```

API will be available at `http://localhost:8000`.

### Local development

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Tests & Lint

```bash
cd backend
make fmt   # format
make lint  # ruff
make test  # pytest
```

## API Examples

Generate a survey:

```bash
curl -X POST http://localhost:8000/api/surveys/generate \
  -H 'Content-Type: application/json' \
  -d '{"description": "customer satisfaction"}'
```

Retrieve a survey:

```bash
curl http://localhost:8000/api/surveys/<id>
```

## Notes

* To require authentication set `API_TOKEN` in `.env` and send `Authorization: Bearer <token>` header.
* Rate limiting defaults to 20 req/min/IP; adjust via `RATE_LIMIT_PER_MIN`.
* The mock provider ensures predictable output for testing and offline use.

## Deployment

Any platform that supports Docker can run the stack. Build the image using the provided Dockerfile and deploy alongside a PostgreSQL instance.
