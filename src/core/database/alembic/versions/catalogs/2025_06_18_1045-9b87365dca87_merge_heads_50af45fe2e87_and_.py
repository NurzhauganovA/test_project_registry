"""merge heads 50af45fe2e87 and d7e3e6270d2c

Revision ID: 9b87365dca87
Revises: 50af45fe2e87, d7e3e6270d2c
Create Date: 2025-06-18 10:45:47.557408

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "9b87365dca87"
down_revision: Union[str, None] = ("50af45fe2e87", "d7e3e6270d2c")  # type: ignore[assignment]
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
