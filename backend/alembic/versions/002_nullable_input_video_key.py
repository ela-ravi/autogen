"""Make recap_jobs.input_video_key nullable (original may be removed after success).

Revision ID: 002
Revises: 001
Create Date: 2026-03-28
"""
from alembic import op
import sqlalchemy as sa

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "recap_jobs",
        "input_video_key",
        existing_type=sa.String(),
        nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "recap_jobs",
        "input_video_key",
        existing_type=sa.String(),
        nullable=False,
    )
