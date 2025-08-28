from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_create_surveys_table"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "surveys",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("description_hash", sa.String(length=64), nullable=False),
        sa.Column("model_name", sa.String(length=50), nullable=False),
        sa.Column("survey_json", postgresql.JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_surveys_description_hash", "surveys", ["description_hash"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_surveys_description_hash", table_name="surveys")
    op.drop_table("surveys")
