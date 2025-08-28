from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_session

router = APIRouter()


@router.get("/healthz")
async def healthz(session: AsyncSession = Depends(get_session)) -> dict:
    try:
        await session.execute(text("SELECT 1"))
    except Exception as exc:  # pragma: no cover - unexpected DB errors
        raise HTTPException(status_code=503, detail="database unavailable") from exc
    return {"status": "ok"}
