"""merge heads into one

Revision ID: 54b47523d7ac
Revises: 029c941f52eb, 4381bd754142, 9b87365dca87
Create Date: 2025-06-18 16:50:02.212807

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "54b47523d7ac"
down_revision: Union[str, None] = ("029c941f52eb", "4381bd754142", "9b87365dca87")  # type: ignore[assignment]
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
