"""empty message

Revision ID: d595ac36500d
Revises: 1dc3cbbf1441, 14e3f3b12bef
Create Date: 2025-07-14 12:41:07.737463

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd595ac36500d'
down_revision: Union[str, None] = ('1dc3cbbf1441', '14e3f3b12bef')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
