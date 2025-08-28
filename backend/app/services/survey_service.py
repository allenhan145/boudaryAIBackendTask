from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..llm.providers import LLMProvider
from ..models import Survey
from ..utils.idempotency import compute_hash


async def generate_or_get_survey(
    description: str, session: AsyncSession, provider: LLMProvider
) -> tuple[Survey, bool]:
    """Generate a new survey or return cached one.

    Returns (Survey, cache_hit).
    """

    _, description_hash = compute_hash(description)

    stmt = select(Survey).where(Survey.description_hash == description_hash)
    result = await session.execute(stmt)
    existing = result.scalar_one_or_none()
    if existing:
        return existing, True

    survey_json = await provider.generate(description)
    survey = Survey(
        description=description,
        description_hash=description_hash,
        model_name=provider.model_name,
        survey_json=survey_json,
    )
    session.add(survey)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        res = await session.execute(stmt)
        return res.scalar_one(), True
    await session.refresh(survey)
    return survey, False
