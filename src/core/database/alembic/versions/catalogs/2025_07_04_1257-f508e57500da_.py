"""empty message

Revision ID: f508e57500da
Revises: 93d6af4f6de6, 0c8f868980b6
Create Date: 2025-07-04 12:57:26.662057

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f508e57500da'
down_revision: Union[str, None] = ('93d6af4f6de6', '0c8f868980b6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
