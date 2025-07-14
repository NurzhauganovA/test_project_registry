"""merge heads

Revision ID: 8010c6108f61
Revises: 09265926cdbb, 54b47523d7ac, ff27fd4543cd
Create Date: 2025-06-20 10:35:22.044341

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "8010c6108f61"
down_revision: Union[str, None] = ("09265926cdbb", "54b47523d7ac", "ff27fd4543cd")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
