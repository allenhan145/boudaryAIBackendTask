from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from .config import get_settings

settings = get_settings()
engine = create_async_engine(settings.database_url, future=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

Base = declarative_base()


async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
