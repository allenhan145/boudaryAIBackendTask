import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.db import Base, get_session
from app.llm.providers import MockProvider


async def _build_client(monkeypatch, **env):
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    import importlib

    import app.routers.surveys as surveys_module

    importlib.reload(surveys_module)
    surveys_module._request_count = 0
    import app.main as main

    importlib.reload(main)
    app = main.create_app()
    engine = create_async_engine(
        env.get("DATABASE_URL", "sqlite+aiosqlite:///:memory:"), future=True
    )
    TestingSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async def override_get_session():
        async with TestingSessionLocal() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    client = AsyncClient(app=app, base_url="http://test")
    return client, engine


@pytest.mark.asyncio
async def test_auth_required_when_token_set(monkeypatch):
    client, engine = await _build_client(monkeypatch, API_TOKEN="secret")
    async with client:
        resp = await client.post(
            "/api/surveys/generate", json={"description": "customer satisfaction"}
        )
        assert resp.status_code == 401
    await engine.dispose()


@pytest.mark.asyncio
async def test_rate_limit_429(monkeypatch):
    client, engine = await _build_client(monkeypatch, RATE_LIMIT_PER_MIN="2")
    async with client:
        for _ in range(2):
            r = await client.post(
                "/api/surveys/generate", json={"description": "rate limit"}
            )
            assert r.status_code in (201, 200)
        r = await client.post("/api/surveys/generate", json={"description": "another"})
        assert r.status_code == 429
    await engine.dispose()


@pytest.mark.asyncio
async def test_mock_provider_is_deterministic():
    provider = MockProvider()
    s1 = await provider.generate("alpha")
    s2 = await provider.generate("alpha")
    assert s1 == s2
