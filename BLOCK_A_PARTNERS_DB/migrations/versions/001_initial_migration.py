"""initial migration for partners database

Revision ID: 001_initial
Revises: 
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Создание таблицы partners
    op.create_table('partners',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('partner_code', sa.String(length=50), nullable=False),
        sa.Column('company_name', sa.String(length=200), nullable=False),
        sa.Column('legal_form', sa.String(length=20), nullable=True),
        sa.Column('inn', sa.String(length=12), nullable=False),
        sa.Column('ogrn', sa.String(length=15), nullable=True),
        sa.Column('legal_address', sa.Text(), nullable=True),
        sa.Column('actual_address', sa.Text(), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('email', sa.String(length=120), nullable=True),
        sa.Column('website', sa.String(length=200), nullable=True),
        sa.Column('contact_person', sa.String(length=100), nullable=True),
        sa.Column('main_category', sa.String(length=50), nullable=True),
        sa.Column('specializations', postgresql.JSONB(), nullable=True),
        sa.Column('services', postgresql.JSONB(), nullable=True),
        sa.Column('regions', postgresql.JSONB(), nullable=True),
        sa.Column('verification_status', sa.String(length=20), server_default='pending', nullable=True),
        sa.Column('verification_date', sa.DateTime(), nullable=True),
        sa.Column('verified_by', sa.String(length=50), nullable=True),
        sa.Column('documents', postgresql.JSONB(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='false', nullable=True),
        sa.Column('subscription_type', sa.String(length=20), server_default='free', nullable=True),
        sa.Column('subscription_expires', sa.DateTime(), nullable=True),
        sa.Column('rating', sa.Float(), server_default='0.0', nullable=True),
        sa.Column('reviews_count', sa.Integer(), server_default='0', nullable=True),
        sa.Column('completed_projects', sa.Integer(), server_default='0', nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('inn'),
        sa.UniqueConstraint('partner_code')
    )
    
    # Создание индексов
    op.create_index('idx_partners_inn', 'partners', ['inn'], unique=True)
    op.create_index('idx_partners_status', 'partners', ['verification_status'])
    op.create_index('idx_partners_created', 'partners', ['created_at'])
    op.create_index('idx_partners_active', 'partners', ['is_active'])
    
    # Таблица верификации
    op.create_table('partner_verification_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('partner_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(length=50), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('details', postgresql.JSONB(), nullable=True),
        sa.Column('performed_by', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['partner_id'], ['partners.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Таблица услуг партнеров
    op.create_table('partner_services',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('partner_id', sa.Integer(), nullable=False),
        sa.Column('service_name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('price_from', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('price_to', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('unit', sa.String(length=50), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['partner_id'], ['partners.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('partner_services')
    op.drop_table('partner_verification_logs')
    op.drop_table('partners')
