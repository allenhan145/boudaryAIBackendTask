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


async def _ensure_valid_survey_json(survey: SurveyModel, session: AsyncSession) -> dict:
    """Validate survey.survey_json against schema; normalize and persist if needed."""
    # Proactively load attributes to avoid async lazy-load in property access
    try:
        await session.refresh(survey, attribute_names=["survey_json", "description"])
    except Exception:
        pass

    data = survey.survey_json
    try:
        model = Survey.model_validate(data)
        # Return the validated dump directly to avoid lazy-loading the attribute again
        return model.model_dump()
    except Exception:
        # Normalize legacy or non-conforming payloads then validate and persist
        from ..llm.providers import _normalize_survey_dict  # local import to avoid cycles

        normalized = _normalize_survey_dict(data if isinstance(data, dict) else {}, survey.description)
        model = Survey.model_validate(normalized)
        fixed = model.model_dump()
        survey.survey_json = fixed
        try:
            await session.commit()
            # Ensure the attribute is loaded if accessed later, but we return fixed directly
            await session.refresh(survey, attribute_names=["survey_json"])
        except Exception:
            await session.rollback()
        return fixed


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
    data = await _ensure_valid_survey_json(survey, session)
    return data


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
    data = await _ensure_valid_survey_json(survey, session)
    return data
