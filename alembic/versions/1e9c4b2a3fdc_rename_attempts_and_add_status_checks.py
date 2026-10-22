"""rename attempts and add status checks

Revision ID: 1e9c4b2a3fdc
Revises: 365159d43b4a
Create Date: 2026-10-21 19:12:08.605067

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1e9c4b2a3fdc'
down_revision: Union[str, Sequence[str], None] = '365159d43b4a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    for table in ("api_extraction_manifest", "dbt_manifest"):
        op.alter_column(table, "attemps", new_column_name="attempts", schema="ctl")
    op.create_check_constraint(
        "ck_extraction_manifest_status", "api_extraction_manifest",
        "ingested_status in ('pending', 'succeeded', 'failed')", schema="ctl",
    )
    op.create_check_constraint(
        "ck_dbt_manifest_status", "dbt_manifest",
        "dbt_ingested_status in ('pending', 'superseded', 'succeeded', 'failed')", schema="ctl",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("ck_dbt_manifest_status", "dbt_manifest", schema="ctl")
    op.drop_constraint("ck_extraction_manifest_status", "api_extraction_manifest", schema="ctl")
    for table in ("api_extraction_manifest", "dbt_manifest"):
        op.alter_column(table, "attempts", new_column_name="attemps", schema="ctl")
