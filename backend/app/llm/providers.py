from __future__ import annotations

import json
import uuid
from datetime import datetime
from typing import Protocol

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from ..config import Settings, get_settings
from ..utils.hashing import normalize_description
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
    model_name = "gpt-3.5-turbo"

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
            return json.loads(content)


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
