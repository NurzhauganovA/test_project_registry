"""empty message

Revision ID: 2bacd903c59f
Revises: 14e3f3b12bef
Create Date: 2025-07-14 14:10:13.079341

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2bacd903c59f'
down_revision: Union[str, None] = '14e3f3b12bef'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
