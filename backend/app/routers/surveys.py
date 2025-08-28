from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import get_settings
from ..db import get_session
from ..llm.providers import LLMProvider, get_llm_provider
from ..models import Survey as SurveyModel
from ..schemas import Survey, SurveyGenerateRequest
from ..services.survey_service import generate_or_get_survey
from ..utils.rate_limit import rate_limit_dep

settings = get_settings()
_RATE_LIMIT = settings.rate_limit_per_min
_requests: list[float] = []
_request_count = 0

router = APIRouter(prefix="/api/surveys", tags=["surveys"])


def get_provider() -> LLMProvider:
    return get_llm_provider(settings)


def verify_token(request: Request) -> None:
    current = get_settings()
    if current.api_token:
        auth = request.headers.get("Authorization")
        if auth != f"Bearer {current.api_token}":
            raise HTTPException(status_code=401, detail="Unauthorized")


def check_rate_limit(request: Request) -> None:
    global _request_count
    _request_count += 1
    if _request_count > _RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Too many requests")


@router.post("/generate", response_model=Survey, status_code=status.HTTP_201_CREATED)
async def generate_survey(
    payload: SurveyGenerateRequest,
    response: Response,
    request: Request,
    session: AsyncSession = Depends(get_session),
    provider: LLMProvider = Depends(get_provider),
    _: None = Depends(rate_limit_dep),
) -> dict:
    verify_token(request)
    check_rate_limit(request)
    survey, cache_hit = await generate_or_get_survey(
        payload.description, session, provider
    )
    response.headers["X-Cache-Hit"] = "1" if cache_hit else "0"
    response.status_code = status.HTTP_200_OK if cache_hit else status.HTTP_201_CREATED
    return survey.survey_json


@router.get("/{survey_id}", response_model=Survey)
async def get_survey(
    survey_id: UUID,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> dict:
    verify_token(request)
    check_rate_limit(request)
    survey = await session.get(SurveyModel, survey_id)
    if not survey:
        raise HTTPException(status_code=404, detail="Not found")
    return survey.survey_json
