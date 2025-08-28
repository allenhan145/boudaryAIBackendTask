from __future__ import annotations

import os
import sys

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import pytest_asyncio  # noqa: E402
from httpx import AsyncClient  # noqa: E402
from sqlalchemy.ext.asyncio import (  # noqa: E402
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.db import Base, get_session  # noqa: E402


@pytest_asyncio.fixture
async def client() -> AsyncClient:
    import app.routers.surveys as surveys_module  # noqa: E402
    from app.main import create_app  # noqa: E402

    surveys_module._request_count = 0

    app = create_app()
    engine = create_async_engine(os.environ["DATABASE_URL"], future=True)
    TestingSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async def override_get_session() -> AsyncSession:
        async with TestingSessionLocal() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    await engine.dispose()
