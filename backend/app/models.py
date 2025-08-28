from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from .config import get_settings
from .db import Base

settings = get_settings()

USE_POSTGRES = settings.database_url.startswith("postgres")
UUID_TYPE = PGUUID(as_uuid=True) if USE_POSTGRES else String(36)
UUID_DEFAULT = uuid.uuid4 if USE_POSTGRES else lambda: str(uuid.uuid4())
SURVEY_JSON = JSONB if USE_POSTGRES else JSON


class Survey(Base):
    __tablename__ = "surveys"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID_TYPE, primary_key=True, default=UUID_DEFAULT
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    description_hash: Mapped[str] = mapped_column(
        String(64), nullable=False, unique=True, index=True
    )
    model_name: Mapped[str] = mapped_column(String(50), nullable=False)
    survey_json: Mapped[dict] = mapped_column(SURVEY_JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
