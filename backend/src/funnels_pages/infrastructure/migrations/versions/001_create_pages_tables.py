"""
Initial migration for Funnels Pages module - SPEC-FUN-002.
Creates pages, page_assets, and page_versions tables.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = ['0001']


def upgrade():
    # Create pages table
    op.create_table(
        'pages',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('account_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('funnel_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('funnels.id', ondelete='SET NULL')),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('page_type', sa.String(20), nullable=False),
        sa.Column('slug', sa.String(100), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='draft'),
        sa.Column('seo_title', sa.String(60)),
        sa.Column('seo_description', sa.String(160)),
        sa.Column('og_title', sa.String(100)),
        sa.Column('og_description', sa.String(200)),
        sa.Column('og_image', sa.String(500)),
        sa.Column('canonical_url', sa.String(500)),
        sa.Column('elements', postgresql.JSONB(), nullable=False, server_default=sa.text('[]')),
        sa.Column('responsive_settings', postgresql.JSONB(), nullable=False, server_default=sa.text('{}')),
        sa.Column('tracking_scripts', postgresql.JSONB(), nullable=False, server_default=sa.text('[]')),
        sa.Column('custom_head', sa.Text()),
        sa.Column('custom_body', sa.Text()),
        sa.Column('published_url', sa.String(500)),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('published_at', sa.DateTime()),
        sa.Column('last_published_at', sa.DateTime()),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True)),
        sa.Column('deleted_at', sa.DateTime()),
    )
    op.create_index('idx_pages_account_id', 'pages', ['account_id'])
    op.create_index('idx_pages_funnel_id', 'pages', ['funnel_id'])
    op.create_index('idx_pages_status', 'pages', ['status'])
    op.create_index('idx_pages_deleted_at', 'pages', ['deleted_at'])
    op.create_index('idx_pages_account_slug_unique', 'pages', ['account_id', 'slug', 'deleted_at'], unique=True)

    # Create page_assets table
    op.create_table(
        'page_assets',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('account_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('page_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('pages.id', ondelete='SET NULL')),
        sa.Column('filename', sa.String(255), nullable=False),
        sa.Column('url', sa.String(500), nullable=False),
        sa.Column('size', sa.Integer(), nullable=False),
        sa.Column('content_type', sa.String(100), nullable=False),
        sa.Column('width', sa.Integer()),
        sa.Column('height', sa.Integer()),
        sa.Column('uploaded_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('uploaded_by', postgresql.UUID(as_uuid=True), nullable=False),
    )
    op.create_index('idx_page_assets_account_id', 'page_assets', ['account_id'])
    op.create_index('idx_page_assets_page_id', 'page_assets', ['page_id'])

    # Create page_versions table
    op.create_table(
        'page_versions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('page_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('pages.id', ondelete='CASCADE'), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('page_snapshot', postgresql.JSONB(), nullable=False),
        sa.Column('change_summary', sa.Text()),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
    )
    op.create_index('idx_page_versions_page_id', 'page_versions', ['page_id'])
    op.create_index('idx_page_versions_page_version_unique', 'page_versions', ['page_id', 'version'], unique=True)


def downgrade():
    op.drop_table('page_versions')
    op.drop_table('page_assets')
    op.drop_table('pages')
