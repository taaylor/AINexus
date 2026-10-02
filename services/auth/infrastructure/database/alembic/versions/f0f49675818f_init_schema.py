"""init schema

Revision ID: f0f49675818f
Revises:
Create Date: 2026-10-02 18:53:04.719196

"""

from collections.abc import Sequence

from alembic import op
from auth.common.settings import settings
from sqlalchemy.schema import CreateSchema

# revision identifiers, used by Alembic.
revision: str = "f0f49675818f"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(CreateSchema(settings.postgres.dbschema, if_not_exists=True))
    pass


def downgrade() -> None:
    pass
