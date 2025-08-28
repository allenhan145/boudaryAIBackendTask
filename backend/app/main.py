from __future__ import annotations

import uuid

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import get_settings
from .logging import setup_logging
from .routers import health, surveys


def create_app() -> FastAPI:
    settings = get_settings()
    setup_logging()

    app = FastAPI(title="Survey Generator API")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        return JSONResponse(status_code=400, content={"detail": exc.errors()})

    @app.middleware("http")
    async def add_request_id(request: Request, call_next):
        request_id = str(uuid.uuid4())
        response = await call_next(request)
        response.headers["X-Request-Id"] = request_id
        return response

    app.include_router(health.router)
    app.include_router(surveys.router)
    return app


app = create_app()
