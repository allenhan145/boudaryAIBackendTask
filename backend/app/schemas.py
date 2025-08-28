from __future__ import annotations

from typing import List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class Scale(BaseModel):
    min: int
    max: int
    labels: List[str] | None = None


class Question(BaseModel):
    id: UUID
    type: Literal[
        "multiple_choice",
        "rating",
        "open_text",
        "likert",
        "yes_no",
        "checkboxes",
        "matrix",
    ]
    text: str
    required: bool
    options: Optional[List[str]] = None
    scale: Optional[Scale] = None


class Survey(BaseModel):
    id: UUID
    title: str
    description: str
    questions: List[Question]
    createdAt: str


class SurveyGenerateRequest(BaseModel):
    description: str = Field(min_length=5, max_length=300)
