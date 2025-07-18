"""empty message

Revision ID: e950311523dd
Revises: 71f04b388f7c
Create Date: 2025-07-15 11:50:01.195890

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e950311523dd'
down_revision: Union[str, None] = '71f04b388f7c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
