"""create raw schema

Revision ID: b9f1c36fd49d
Revises: c0447e988f59
Create Date: 2026-09-24 15:15:52.499790

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b9f1c36fd49d'
down_revision: Union[str, Sequence[str], None] = 'c0447e988f59'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("create schema raw")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("drop schema raw")
