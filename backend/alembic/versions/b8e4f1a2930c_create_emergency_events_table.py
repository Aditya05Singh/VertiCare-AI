"""create_emergency_events_table

Revision ID: b8e4f1a2930c
Revises: aa57239e9162
Create Date: 2026-08-31 01:57:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b8e4f1a2930c'
down_revision: Union[str, None] = 'aa57239e9162'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'emergency_events',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('patient_id', sa.String(length=36), nullable=False),
        sa.Column('risk_assessment_id', sa.String(length=36), nullable=True),
        sa.Column(
            'severity',
            sa.Enum('LOW', 'MEDIUM', 'HIGH', 'CRITICAL', name='emergencyseverity', native_enum=False),
            nullable=False
        ),
        sa.Column(
            'status',
            sa.Enum('PENDING', 'CONTACT_INITIATED', 'ACKNOWLEDGED', 'RESOLVED', 'CANCELLED', name='emergencystatus', native_enum=False),
            nullable=False
        ),
        sa.Column('contacted_doctor', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('contacted_emergency_contact', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('contacted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['patient_id'], ['patient_profiles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['risk_assessment_id'], ['risk_assessments.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_emergency_events_patient_id'), 'emergency_events', ['patient_id'], unique=False)
    op.create_index(op.f('ix_emergency_events_risk_assessment_id'), 'emergency_events', ['risk_assessment_id'], unique=False)
    op.create_index(op.f('ix_emergency_events_severity'), 'emergency_events', ['severity'], unique=False)
    op.create_index(op.f('ix_emergency_events_status'), 'emergency_events', ['status'], unique=False)
    op.create_index(op.f('ix_emergency_events_created_at'), 'emergency_events', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_emergency_events_created_at'), table_name='emergency_events')
    op.drop_index(op.f('ix_emergency_events_status'), table_name='emergency_events')
    op.drop_index(op.f('ix_emergency_events_severity'), table_name='emergency_events')
    op.drop_index(op.f('ix_emergency_events_risk_assessment_id'), table_name='emergency_events')
    op.drop_index(op.f('ix_emergency_events_patient_id'), table_name='emergency_events')
    op.drop_table('emergency_events')

