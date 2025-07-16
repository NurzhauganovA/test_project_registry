"""empty message

Revision ID: 71f04b388f7c
Revises: d8e3d0dd8da2, 91d030781a7d
Create Date: 2025-07-15 10:19:48.288196

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '71f04b388f7c'
down_revision: Union[str, None] = ('d8e3d0dd8da2', '91d030781a7d')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
