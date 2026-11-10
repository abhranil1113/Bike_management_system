"""tariffs cod and reviews

Revision ID: d10f8a912e34
Revises: c95a9f5b45bb
Create Date: 2026-11-07 10:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector


# revision identifiers, used by Alembic.
revision: str = 'd10f8a912e34'
down_revision: Union[str, None] = '94f370b12a50'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    tables = inspector.get_table_names()

    # 1. Create bike_tariffs table if not exists
    if 'bike_tariffs' not in tables:
        op.create_table(
            'bike_tariffs',
            sa.Column('id', sa.String(length=36), nullable=False),
            sa.Column('bike_id', sa.String(length=36), nullable=False),
            sa.Column('hours', sa.Integer(), nullable=False),
            sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
            sa.CheckConstraint('hours > 0', name='ck_bike_tariffs_hours_positive'),
            sa.CheckConstraint('price >= 0', name='ck_bike_tariffs_price_nonnegative'),
            sa.ForeignKeyConstraint(['bike_id'], ['bikes.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('bike_id', 'hours', name='uq_bike_tariffs_bike_hours')
        )
        op.create_index('ix_bike_tariffs_bike_id', 'bike_tariffs', ['bike_id'], unique=False)

    # 2. Add columns to bike_pricing
    if 'bike_pricing' in tables:
        cols = [c['name'] for c in inspector.get_columns('bike_pricing')]
        if 'hourly_rate' not in cols:
            op.add_column('bike_pricing', sa.Column('hourly_rate', sa.Numeric(precision=10, scale=2), server_default='100.00', nullable=True))
        if 'late_fee_per_hour' not in cols:
            op.add_column('bike_pricing', sa.Column('late_fee_per_hour', sa.Numeric(precision=10, scale=2), server_default='50.00', nullable=True))

    # 3. Add columns to bike_booking_requests
    if 'bike_booking_requests' in tables:
        cols = [c['name'] for c in inspector.get_columns('bike_booking_requests')]
        if 'rental_hours' not in cols:
            op.add_column('bike_booking_requests', sa.Column('rental_hours', sa.Integer(), server_default='24', nullable=True))
        if 'total_amount' not in cols:
            op.add_column('bike_booking_requests', sa.Column('total_amount', sa.Numeric(precision=10, scale=2), server_default='0.00', nullable=True))
        if 'payment_method' not in cols:
            op.add_column('bike_booking_requests', sa.Column('payment_method', sa.String(length=30), server_default='cod', nullable=True))
        if 'cash_received' not in cols:
            op.add_column('bike_booking_requests', sa.Column('cash_received', sa.Boolean(), server_default=sa.text('false'), nullable=True))
        if 'cash_received_at' not in cols:
            op.add_column('bike_booking_requests', sa.Column('cash_received_at', sa.DateTime(timezone=True), nullable=True))
        if 'cod_admin_escalated' not in cols:
            op.add_column('bike_booking_requests', sa.Column('cod_admin_escalated', sa.Boolean(), server_default=sa.text('false'), nullable=True))

    # 4. Add columns to driver_bike_assignments
    if 'driver_bike_assignments' in tables:
        cols = [c['name'] for c in inspector.get_columns('driver_bike_assignments')]
        if 'rental_hours' not in cols:
            op.add_column('driver_bike_assignments', sa.Column('rental_hours', sa.Integer(), server_default='24', nullable=True))
        if 'total_rent_amount' not in cols:
            op.add_column('driver_bike_assignments', sa.Column('total_rent_amount', sa.Numeric(precision=10, scale=2), server_default='0.00', nullable=True))
        if 'payment_method' not in cols:
            op.add_column('driver_bike_assignments', sa.Column('payment_method', sa.String(length=30), server_default='cod', nullable=True))
        if 'cash_received' not in cols:
            op.add_column('driver_bike_assignments', sa.Column('cash_received', sa.Boolean(), server_default=sa.text('false'), nullable=True))
        if 'cash_received_at' not in cols:
            op.add_column('driver_bike_assignments', sa.Column('cash_received_at', sa.DateTime(timezone=True), nullable=True))
        if 'last_cod_reminder_at' not in cols:
            op.add_column('driver_bike_assignments', sa.Column('last_cod_reminder_at', sa.DateTime(timezone=True), nullable=True))
        if 'cod_admin_escalated' not in cols:
            op.add_column('driver_bike_assignments', sa.Column('cod_admin_escalated', sa.Boolean(), server_default=sa.text('false'), nullable=True))


def downgrade() -> None:
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    tables = inspector.get_table_names()

    if 'bike_tariffs' in tables:
        op.drop_index('ix_bike_tariffs_bike_id', table_name='bike_tariffs')
        op.drop_table('bike_tariffs')
