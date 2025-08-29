from __future__ import annotations

import json
import uuid
from datetime import datetime
from typing import Protocol

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from ..config import Settings, get_settings
from ..utils.hashing import normalize_description
from ..schemas import Survey as SurveySchema
from .prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE


class LLMProvider(Protocol):
    model_name: str

    async def generate(self, description: str) -> dict: ...


class MockProvider:
    model_name = "mock-v1"

    async def generate(self, description: str) -> dict:
        norm = normalize_description(description)
        base_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, norm)

        def qid(i: int) -> str:
            return str(uuid.uuid5(base_uuid, f"q{i}"))

        question_types = [
            "multiple_choice",
            "rating",
            "open_text",
            "likert",
            "yes_no",
            "checkboxes",
            "matrix",
            "multiple_choice",
        ]
        questions = []
        for idx, qtype in enumerate(question_types, start=1):
            q = {
                "id": qid(idx),
                "type": qtype,
                "text": f"Question {idx} about {description}?",
                "required": True,
            }
            if qtype in {"multiple_choice", "checkboxes"}:
                q["options"] = ["Option A", "Option B", "Option C"]
            if qtype in {"rating", "likert"}:
                q["scale"] = {"min": 1, "max": 5, "labels": ["1", "2", "3", "4", "5"]}
            questions.append(q)

        survey = {
            "id": str(base_uuid),
            "title": f"{description.title()} Survey",
            "description": description,
            "questions": questions,
            "createdAt": datetime(2020, 1, 1).isoformat(),
        }
        return survey


class OpenAIProvider:
    model_name = "gpt-4o-mini"

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    @retry(
        wait=wait_exponential(multiplier=1, min=1, max=10), stop=stop_after_attempt(3)
    )
    async def generate(self, description: str) -> dict:
        prompt = USER_PROMPT_TEMPLATE.format(description=description)
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model_name,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.2,
                },
            )
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"]

        raw = json.loads(content)
        normalized = _normalize_survey_dict(raw, description)
        # Validate and prune extras
        model = SurveySchema.model_validate(normalized)
        return model.model_dump()


def _normalize_survey_dict(data: dict, description: str) -> dict:
    """Coerce arbitrary survey-shaped data from an LLM into our schema."""
    out: dict = {}

    # Top-level fields
    out["description"] = description
    out["title"] = data.get("title") or f"{description.title()} Survey"
    out["createdAt"] = data.get("createdAt") or datetime.utcnow().isoformat()

    # id: accept if valid UUID string, else derive a stable one from description
    id_value = data.get("id")
    out["id"] = _safe_uuid_str(id_value) or str(
        uuid.uuid5(uuid.NAMESPACE_DNS, normalize_description(description))
    )

    # Questions
    questions = data.get("questions") or []
    norm_questions = []
    for idx, q in enumerate(questions, start=1):
        if not isinstance(q, dict):
            continue
        qq: dict = {}

        # id
        qq["id"] = _safe_uuid_str(q.get("id")) or str(
            uuid.uuid5(uuid.uuid4(), f"q{idx}")
        )

        # type normalization
        qtype = (q.get("type") or "open_text").lower().replace("-", "_")
        alias_map = {
            "yesno": "yes_no",
            "yes_no": "yes_no",
            "multiple_choice": "multiple_choice",
            "multiplechoice": "multiple_choice",
            "checkbox": "checkboxes",
            "checkboxes": "checkboxes",
            "rating": "rating",
            "likert": "likert",
            "open_text": "open_text",
            "open": "open_text",
            "text": "open_text",
            "matrix": "matrix",
        }
        qtype = alias_map.get(qtype, "open_text")
        qq["type"] = qtype

        # text / question alias
        text = q.get("text") or q.get("question") or ""
        qq["text"] = str(text)

        # required default True
        req = q.get("required")
        qq["required"] = bool(True if req is None else req)

        # options (only keep list of strings if present)
        opts = q.get("options")
        if isinstance(opts, list):
            qq["options"] = [str(o) for o in opts]

        # scale: accept object or int like 5
        scale = q.get("scale")
        if isinstance(scale, int):
            qq["scale"] = {
                "min": 1,
                "max": int(scale),
                "labels": [str(i) for i in range(1, int(scale) + 1)],
            }
        elif isinstance(scale, dict):
            mn = int(scale.get("min", 1))
            mx = int(scale.get("max", 5))
            labels = scale.get("labels")
            if not isinstance(labels, list):
                labels = None
            qq["scale"] = {"min": mn, "max": mx, "labels": labels}
        elif qtype in {"rating", "likert"}:
            qq["scale"] = {
                "min": 1,
                "max": 5,
                "labels": ["1", "2", "3", "4", "5"],
            }

        norm_questions.append(qq)

    out["questions"] = norm_questions
    return out


def _safe_uuid_str(value: object | None) -> str | None:
    """Return a valid UUID string or None if parsing fails."""
    if not value:
        return None
    try:
        return str(uuid.UUID(str(value)))
    except Exception:
        return None


class NotImplementedProvider(MockProvider):
    """Fallback provider for unimplemented integrations."""


PROVIDER_MAP = {
    "openai": OpenAIProvider,
    "openrouter": NotImplementedProvider,
    "together": NotImplementedProvider,
    "mock": MockProvider,
}


def get_llm_provider(settings: Settings | None = None) -> LLMProvider:
    settings = settings or get_settings()
    provider_name = settings.llm_provider.lower()
    provider_cls = PROVIDER_MAP.get(provider_name, MockProvider)

    if provider_cls is OpenAIProvider and settings.openai_api_key:
        return OpenAIProvider(settings.openai_api_key)
    if provider_cls is NotImplementedProvider:
        return MockProvider()
    return provider_cls()
