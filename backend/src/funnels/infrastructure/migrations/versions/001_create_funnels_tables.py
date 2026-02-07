"""
Initial migration for Funnels module - SPEC-FUN-001.
Creates funnels, funnel_steps, funnel_templates, and funnel_versions tables.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create funnels table
    op.create_table(
        'funnels',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('account_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('funnel_type', sa.String(50), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='draft'),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True)),
        sa.Column('deleted_at', sa.DateTime()),
    )
    op.create_index('idx_funnels_account_id', 'funnels', ['account_id'])
    op.create_index('idx_funnels_status', 'funnels', ['status'])
    op.create_index('idx_funnels_type', 'funnels', ['funnel_type'])
    op.create_index('idx_funnels_deleted_at', 'funnels', ['deleted_at'])
    op.create_index('idx_funnels_account_name_unique', 'funnels', ['account_id', 'name', 'deleted_at'], unique=True)

    # Create funnel_steps table
    op.create_table(
        'funnel_steps',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('funnel_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('funnels.id', ondelete='CASCADE'), nullable=False),
        sa.Column('step_type', sa.String(20), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.Column('page_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('pages.id', ondelete='SET NULL')),
        sa.Column('config', postgresql.JSONB(), nullable=False, server_default=sa.text('{}')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
    )
    op.create_index('idx_funnel_steps_funnel_id', 'funnel_steps', ['funnel_id'])
    op.create_index('idx_funnel_steps_page_id', 'funnel_steps', ['page_id'])
    op.create_index('idx_funnel_steps_funnel_order_unique', 'funnel_steps', ['funnel_id', 'order'], unique=True)

    # Create funnel_templates table
    op.create_table(
        'funnel_templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(100), nullable=False, unique=True),
        sa.Column('description', sa.Text()),
        sa.Column('category', sa.String(50)),
        sa.Column('funnel_type', sa.String(50), nullable=False),
        sa.Column('preview_image_url', sa.String(500)),
        sa.Column('template_data', postgresql.JSONB(), nullable=False),
        sa.Column('use_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('is_system_template', sa.Boolean(), nullable=False, server_default='true'),
    )
    op.create_index('idx_funnel_templates_category', 'funnel_templates', ['category'])
    op.create_index('idx_funnel_templates_type', 'funnel_templates', ['funnel_type'])

    # Create funnel_versions table
    op.create_table(
        'funnel_versions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('funnel_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('funnels.id', ondelete='CASCADE'), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('funnel_snapshot', postgresql.JSONB(), nullable=False),
        sa.Column('change_description', sa.Text()),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
    )
    op.create_index('idx_funnel_versions_funnel_id', 'funnel_versions', ['funnel_id'])
    op.create_index('idx_funnel_versions_funnel_version_unique', 'funnel_versions', ['funnel_id', 'version'], unique=True)


def downgrade():
    op.drop_table('funnel_versions')
    op.drop_table('funnel_templates')
    op.drop_table('funnel_steps')
    op.drop_table('funnels')
