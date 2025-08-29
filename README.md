# AI‑Powered Survey Generator

An end‑to‑end feature that transforms a short user brief into a complete survey. The backend (FastAPI, Python 3.11) generates and caches surveys using an LLM provider and stores them in PostgreSQL. The frontend (React) calls the API and auto‑fills the survey creation form.

## Why FastAPI

- Async IO with first‑class type safety via Pydantic v2
- Clean dependency injection and auto docs (OpenAPI)
- Fast developer loop and excellent validation ergonomics

## Architecture

- Backend: FastAPI app with clear layers
  - Routes: `backend/app/routers/*`
  - Services: `backend/app/services/*`
  - LLM providers: `backend/app/llm/*` (OpenAI + deterministic mock)
  - Schemas: `backend/app/schemas.py`
  - Models/DB: `backend/app/models.py`, `backend/app/db.py` (SQLAlchemy + Alembic)
  - Utils: idempotency hash, rate limiting, logging
- Frontend: Minimal React component wiring
  - Entry: `frontend/src/component/SurveyGenerator.tsx`
  - Page: `frontend/src/pages/CreateSurveyPage.jsx`

## Features

- Idempotent generation: same description returns the cached survey (JSONB) via a normalized SHA‑256 hash
- Provider abstraction: OpenAI with retries/timeouts, plus a deterministic mock (default)
- Optional bearer auth and simple per‑IP rate limiting
- Structured logging with request ID, CORS middleware
- Dockerized stack with Postgres, plus Makefile helpers
- Tests: generation, idempotency, auth/rate limit, mock determinism

## API

- `POST /api/surveys/generate`
  - Body: `{ "description": string }` (5–300 chars)
  - Responses:
    - 201 Created + survey JSON when newly generated
    - 200 OK + header `X-Cache-Hit: 1` when returned from cache
  - Errors: 400 validation, 401 unauthorized (when token required), 429 rate limit

- `GET /api/surveys/{id}`
  - Response: survey JSON or 404

Survey JSON shape (Pydantic‑validated):

```json
{
  "id": "<uuid>",
  "title": "<string>",
  "description": "<string>",
  "questions": [
    {
      "id": "<uuid>",
      "type": "multiple_choice|rating|open_text|likert|yes_no|checkboxes|matrix",
      "text": "<string>",
      "required": true,
      "options": ["<string>", "<string>"] ,
      "scale": { "min": 1, "max": 5, "labels": ["1","2","3","4","5"] }
    }
  ],
  "createdAt": "<iso8601>"
}
```

## Quick Start

### Run with Docker (recommended)

```bash
cd backend
cp .env.example .env  # edit if needed
make up                # builds API and starts Postgres
```

API: `http://localhost:8000`

Frontend (in another terminal):

```bash
cd frontend
npm install
npm start
```

The frontend proxy (`frontend/package.json`) points to `http://localhost:8000`.

### Local development (without Docker)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL="sqlite+aiosqlite:///:memory:"  # or your DB
uvicorn app.main:app --reload
```

## Environment Variables

- `DATABASE_URL`: Postgres URL (e.g. `postgresql+psycopg://postgres:postgres@db:5432/surveys`)
- `API_TOKEN` (optional): when set, require `Authorization: Bearer <token>`
- `LLM_PROVIDER`: `mock` (default) or `openai`
- `OPENAI_API_KEY`: required when `LLM_PROVIDER=openai`
- `RATE_LIMIT_PER_MIN`: requests per minute per IP (default 20)
- `CORS_ORIGINS`: JSON array of allowed origins (default `[*]`)

Never commit real secrets. Use `backend/.env.example` as a template and keep `backend/.env` untracked (already in `.gitignore`).

## Examples

Generate a survey:

```bash
curl -X POST http://localhost:8000/api/surveys/generate \
  -H 'Content-Type: application/json' \
  -d '{"description": "customer satisfaction for an online store"}' -i
```

Retrieve by id:

```bash
curl http://localhost:8000/api/surveys/<id>
```

With auth enabled:

```bash
curl -H 'Authorization: Bearer <token>' http://localhost:8000/api/surveys/<id>
```

## Testing & Linting

```bash
cd backend
make fmt    # black + isort
make lint   # ruff
make test   # pytest (async httpx tests)
```

## Design Decisions

- Idempotency: normalized brief (trim/lower/collapse spaces) hashed with SHA‑256; unique DB index ensures single record per brief
- LLM robustness: strict normalization of provider output into our schema; OpenAI calls via `httpx` with timeouts and exponential backoff (tenacity)
- Persistence: JSONB column allows evolving question schema without costly migrations
- Security/limits: optional bearer token, per‑IP rate limiting, CORS, request ID
- DX: deterministic mock provider enables offline dev and stable tests

## Deployment

Any Docker‑capable platform works. Build and deploy the `backend` image alongside a Postgres instance, set env vars, and run Alembic migrations if using a persistent DB:

```bash
cd backend
alembic upgrade head
```

## Limitations & Next Steps

- Semantic caching (near‑duplicate briefs) via embeddings
- Per‑user quotas and audit logs
- Better survey quality heuristics and content filters
- Observability: request metrics, tracing, dashboards

---

This repository is intentionally scoped to the interview task: clear API design, robust integration, tested idempotency, and a minimal but usable frontend hook‑up.

