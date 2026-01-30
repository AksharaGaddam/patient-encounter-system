"""initial migration

Revision ID: 0001_initial
Revises: 
Create Date: 2026-01-30 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'akshara_patients',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=150), nullable=False, unique=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        'akshara_doctors',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('full_name', sa.String(length=150), nullable=False),
        sa.Column('specialization', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default=sa.text('1')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        'akshara_appointments',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('patient_id', sa.Integer(), sa.ForeignKey('akshara_patients.id'), nullable=False),
        sa.Column('doctor_id', sa.Integer(), sa.ForeignKey('akshara_doctors.id'), nullable=False),
        sa.Column('start_time', sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column('duration_minutes', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    )


def downgrade():
    op.drop_table('akshara_appointments')
    op.drop_table('akshara_doctors')
    op.drop_table('akshara_patients')
