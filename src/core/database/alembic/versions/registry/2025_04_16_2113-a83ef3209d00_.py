"""empty message

Revision ID: a83ef3209d00
Revises: 904e7a1d8dd2
Create Date: 2025-04-16 21:13:17.721322

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "a83ef3209d00"
down_revision: Union[str, None] = "904e7a1d8dd2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        "CREATE TYPE appointmenttypeenum AS ENUM ('INITIAL', 'REVISIT', 'CONSULTATION')"
    )
    op.execute(
        "CREATE TYPE appointmentinsurancetype AS ENUM ('GOBMP', 'DMS', 'OSMS', 'PAID')"
    )

    # Then add the columns using these enum types
    op.add_column(
        "appointments",
        sa.Column(
            "type",
            sa.Enum("INITIAL", "REVISIT", "CONSULTATION", name="appointmenttypeenum"),
            nullable=False,
        ),
    )
    op.add_column(
        "appointments",
        sa.Column(
            "insurance_type",
            sa.Enum("GOBMP", "DMS", "OSMS", "PAID", name="appointmentinsurancetype"),
            nullable=False,
        ),
    )
    op.add_column("appointments", sa.Column("reason", sa.Text(), nullable=True))
    op.add_column(
        "appointments", sa.Column("office_number", sa.Integer(), nullable=True)
    )
    op.add_column(
        "appointments",
        sa.Column("is_patient_info_confirmation_needed", sa.Boolean(), nullable=False),
    )
    op.add_column(
        "appointments",
        sa.Column(
            "paid_services",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="{}",
            nullable=False,
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop the added columns first
    op.drop_column("appointments", "paid_services")
    op.drop_column("appointments", "is_patient_info_confirmation_needed")
    op.drop_column("appointments", "office_number")
    op.drop_column("appointments", "reason")
    op.drop_column("appointments", "insurance_type")
    op.drop_column("appointments", "type")
    # Drop the enum types after dropping columns that use them
    op.execute("DROP TYPE appointmentinsurancetype")
    op.execute("DROP TYPE appointmenttypeenum")
