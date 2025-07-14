"""empty message

Revision ID: 14e3f3b12bef
Revises: a07c66b626f7, a1ab97209457
Create Date: 2025-07-10 16:08:05.074353

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '14e3f3b12bef'
down_revision: Union[str, None] = ('a07c66b626f7', 'a1ab97209457')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
