"""create_assets_tables_complete

Revision ID: bdbae99c83e0
Revises: e950311523dd
Create Date: 2025-07-16 12:43:23.820147


"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'bdbae99c83e0'
down_revision: Union[str, None] = 'e950311523dd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create assets tables with all required columns."""

    # op.execute("CREATE TYPE assetstatusenum AS ENUM ('REGISTERED', 'CONFIRMED', 'REFUSED', 'CANCELLED')")
    # op.execute("CREATE TYPE assetdeliverystatusenum AS ENUM ('RECEIVED_AUTOMATICALLY', 'PENDING_DELIVERY', 'DELIVERED')")
    # op.execute("CREATE TYPE emergencyoutcomeenum AS ENUM ('HOSPITALIZED', 'TREATED_AT_HOME', 'REFUSED_TREATMENT', 'DEATH', 'TRANSFERRED')")

    # Create stationary_assets table
    op.create_table('stationary_assets',
                    sa.Column('id', sa.UUID(), nullable=False),
                    sa.Column('bg_asset_id', sa.String(length=50), nullable=True),
                    sa.Column('card_number', sa.String(length=50), nullable=True),
                    sa.Column('patient_id', sa.UUID(), nullable=False),
                    sa.Column('receive_date', sa.DateTime(timezone=True), nullable=False),
                    sa.Column('receive_time', sa.Time(), nullable=False),
                    sa.Column('actual_datetime', sa.DateTime(timezone=True), nullable=False),
                    sa.Column('received_from', sa.String(length=255), nullable=False),
                    sa.Column('is_repeat', sa.Boolean(), nullable=False, server_default='false'),
                    sa.Column('stay_period_start', sa.DateTime(timezone=True), nullable=False),
                    sa.Column('stay_period_end', sa.DateTime(timezone=True), nullable=True),
                    sa.Column('stay_outcome', sa.String(length=255), nullable=True),
                    sa.Column('diagnosis', sa.Text(), nullable=False),
                    sa.Column('area', sa.String(length=255), nullable=False),
                    sa.Column('specialization', sa.String(length=255), nullable=True),
                    sa.Column('specialist', sa.String(length=255), nullable=False),
                    sa.Column('note', sa.Text(), nullable=True),
                    sa.Column('status',
                              sa.Enum('REGISTERED', 'CONFIRMED', 'REFUSED', 'CANCELLED', name='assetstatusenum'),
                              nullable=False, server_default='REGISTERED'),
                    sa.Column('delivery_status', sa.Enum('RECEIVED_AUTOMATICALLY', 'PENDING_DELIVERY', 'DELIVERED',
                                                         name='assetdeliverystatusenum'),
                              nullable=False, server_default='RECEIVED_AUTOMATICALLY'),
                    sa.Column('reg_date', sa.DateTime(timezone=True), nullable=True, server_default=sa.text('now()')),
                    sa.Column('has_confirm', sa.Boolean(), nullable=False, server_default='false'),
                    sa.Column('has_files', sa.Boolean(), nullable=False, server_default='false'),
                    sa.Column('has_refusal', sa.Boolean(), nullable=False, server_default='false'),
                    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'),
                              nullable=False),
                    sa.Column('changed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'),
                              nullable=False),
                    sa.PrimaryKeyConstraint('id', name=op.f('pk_stationary_assets')),
                    sa.ForeignKeyConstraint(['patient_id'], ['patients.id'],
                                            name=op.f('fk_stationary_assets_patient_id_patients'), ondelete='CASCADE'),
                    sa.UniqueConstraint('bg_asset_id', name=op.f('uq_stationary_assets_bg_asset_id'))
                    )

    # Create emergency_assets table
    op.create_table('emergency_assets',
                    sa.Column('id', sa.UUID(), nullable=False),
                    sa.Column('bg_asset_id', sa.String(length=50), nullable=True),
                    sa.Column('patient_id', sa.UUID(), nullable=False),
                    sa.Column('patient_location_address', sa.Text(), nullable=True),
                    sa.Column('is_not_attached_to_mo', sa.Boolean(), nullable=False, server_default='false'),
                    sa.Column('receive_date', sa.DateTime(timezone=True), nullable=False),
                    sa.Column('receive_time', sa.Time(), nullable=False),
                    sa.Column('actual_datetime', sa.DateTime(timezone=True), nullable=False),
                    sa.Column('received_from', sa.String(length=255), nullable=False),
                    sa.Column('is_repeat', sa.Boolean(), nullable=False, server_default='false'),
                    sa.Column('outcome',
                              sa.Enum('HOSPITALIZED', 'TREATED_AT_HOME', 'REFUSED_TREATMENT', 'DEATH', 'TRANSFERRED',
                                      name='emergencyoutcomeenum'), nullable=True),
                    sa.Column('diagnoses', postgresql.JSONB(astext_type=sa.Text()), nullable=True,
                              comment='Список диагнозов в формате JSON'),
                    sa.Column('diagnosis_note', sa.Text(), nullable=True),
                    sa.Column('status',
                              sa.Enum('REGISTERED', 'CONFIRMED', 'REFUSED', 'CANCELLED', name='assetstatusenum'),
                              nullable=False, server_default='REGISTERED'),
                    sa.Column('delivery_status', sa.Enum('RECEIVED_AUTOMATICALLY', 'PENDING_DELIVERY', 'DELIVERED',
                                                         name='assetdeliverystatusenum'),
                              nullable=False, server_default='RECEIVED_AUTOMATICALLY'),
                    sa.Column('reg_date', sa.DateTime(timezone=True), nullable=True, server_default=sa.text('now()')),
                    sa.Column('has_confirm', sa.Boolean(), nullable=False, server_default='false'),
                    sa.Column('has_files', sa.Boolean(), nullable=False, server_default='false'),
                    sa.Column('has_refusal', sa.Boolean(), nullable=False, server_default='false'),
                    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'),
                              nullable=False),
                    sa.Column('changed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'),
                              nullable=False),
                    sa.PrimaryKeyConstraint('id', name=op.f('pk_emergency_assets')),
                    sa.ForeignKeyConstraint(['patient_id'], ['patients.id'],
                                            name=op.f('fk_emergency_assets_patient_id_patients'), ondelete='CASCADE'),
                    sa.UniqueConstraint('bg_asset_id', name=op.f('uq_emergency_assets_bg_asset_id'))
                    )

    # Create newborn_assets table
    op.create_table('newborn_assets',
                    sa.Column('id', sa.UUID(), nullable=False),
                    sa.Column('bg_asset_id', sa.String(length=50), nullable=True),
                    sa.Column('patient_id', sa.UUID(), nullable=True),
                    sa.Column('patient_full_name_if_not_registered', sa.String(length=255), nullable=True),
                    sa.Column('receive_date', sa.DateTime(timezone=True), nullable=False),
                    sa.Column('receive_time', sa.Time(), nullable=False),
                    sa.Column('actual_datetime', sa.DateTime(timezone=True), nullable=False),
                    sa.Column('received_from', sa.String(length=255), nullable=False),
                    sa.Column('is_repeat', sa.Boolean(), nullable=False, server_default='false'),
                    sa.Column('mother_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True,
                              comment='Данные о матери в формате JSON'),
                    sa.Column('newborn_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True,
                              comment='Данные о новорожденном в формате JSON'),
                    sa.Column('diagnoses', postgresql.JSONB(astext_type=sa.Text()), nullable=True,
                              comment='Список диагнозов в формате JSON'),
                    sa.Column('diagnosis_note', sa.Text(), nullable=True),
                    sa.Column('status',
                              sa.Enum('REGISTERED', 'CONFIRMED', 'REFUSED', 'CANCELLED', name='assetstatusenum'),
                              nullable=False, server_default='REGISTERED'),
                    sa.Column('delivery_status', sa.Enum('RECEIVED_AUTOMATICALLY', 'PENDING_DELIVERY', 'DELIVERED',
                                                         name='assetdeliverystatusenum'),
                              nullable=False, server_default='RECEIVED_AUTOMATICALLY'),
                    sa.Column('reg_date', sa.DateTime(timezone=True), nullable=True, server_default=sa.text('now()')),
                    sa.Column('has_confirm', sa.Boolean(), nullable=False, server_default='false'),
                    sa.Column('has_files', sa.Boolean(), nullable=False, server_default='false'),
                    sa.Column('has_refusal', sa.Boolean(), nullable=False, server_default='false'),
                    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'),
                              nullable=False),
                    sa.Column('changed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'),
                              nullable=False),
                    sa.PrimaryKeyConstraint('id', name=op.f('pk_newborn_assets')),
                    sa.ForeignKeyConstraint(['patient_id'], ['patients.id'],
                                            name=op.f('fk_newborn_assets_patient_id_patients'), ondelete='CASCADE'),
                    sa.UniqueConstraint('bg_asset_id', name=op.f('uq_newborn_assets_bg_asset_id'))
                    )


def downgrade() -> None:
    """Drop assets tables."""
    # Drop foreign key constraints first
    op.drop_constraint(op.f('fk_emergency_assets_patient_id_patients'), 'emergency_assets', type_='foreignkey')
    op.drop_constraint(op.f('fk_newborn_assets_patient_id_patients'), 'newborn_assets', type_='foreignkey')
    op.drop_constraint(op.f('fk_stationary_assets_patient_id_patients'), 'stationary_assets', type_='foreignkey')

    # Drop tables
    op.drop_table('emergency_assets')
    op.drop_table('newborn_assets')
    op.drop_table('stationary_assets')

    # Drop enums
    op.execute('DROP TYPE IF EXISTS assetstatusenum CASCADE')
    op.execute('DROP TYPE IF EXISTS assetdeliverystatusenum CASCADE')
    op.execute('DROP TYPE IF EXISTS emergencyoutcomeenum CASCADE')
