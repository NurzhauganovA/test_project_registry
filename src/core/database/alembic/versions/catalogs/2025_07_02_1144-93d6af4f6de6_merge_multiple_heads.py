"""merge multiple heads

Revision ID: 93d6af4f6de6
Revises: 71c02f268e0c, 9735cefae0ac
Create Date: 2025-07-02 11:44:08.552987

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '93d6af4f6de6'
down_revision: Union[str, None] = ('71c02f268e0c', '9735cefae0ac')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
