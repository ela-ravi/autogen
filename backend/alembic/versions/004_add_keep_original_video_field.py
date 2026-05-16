"""Add keep_original_video field to RecapJob

Revision ID: 004
Revises: 003
Create Date: 2026-05-16 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('recap_jobs', sa.Column('keep_original_video', sa.Boolean(), nullable=True, default=False))


def downgrade() -> None:
    op.drop_column('recap_jobs', 'keep_original_video')
