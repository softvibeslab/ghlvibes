"""
Migration for Funnels Orders module - SPEC-FUN-003.
Creates orders, order_items, order_bumps, order_upsells, and refunds tables.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0003'
down_revision = '0002'
branch_labels = None
depends_on = ['0002', '0001']


def upgrade():
    # Create orders table
    op.create_table(
        'orders',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('account_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('funnel_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('funnels.id'), nullable=False),
        sa.Column('funnel_step_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('funnel_steps.id'), nullable=False),
        sa.Column('contact_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('contacts.id')),
        sa.Column('order_number', sa.String(50), nullable=False, unique=True),
        sa.Column('customer_email', sa.String(255), nullable=False),
        sa.Column('customer_name', sa.String(255)),
        sa.Column('customer_phone', sa.String(50)),
        sa.Column('billing_address', postgresql.JSONB(), nullable=False),
        sa.Column('shipping_address', postgresql.JSONB()),
        sa.Column('currency', sa.String(3), nullable=False, server_default='usd'),
        sa.Column('subtotal_cents', sa.Integer(), nullable=False),
        sa.Column('tax_cents', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('shipping_cents', sa.Integer()),
        sa.Column('discount_cents', sa.Integer(), server_default='0'),
        sa.Column('total_cents', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('payment_status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('payment_method', sa.String(20), nullable=False),
        sa.Column('stripe_payment_intent_id', sa.String(255), unique=True),
        sa.Column('paid_at', sa.DateTime()),
        sa.Column('failure_reason', sa.Text()),
        sa.Column('metadata', postgresql.JSONB(), server_default=sa.text('{}')),
        sa.Column('affiliate_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
    )
    op.create_index('idx_orders_account_id', 'orders', ['account_id'])
    op.create_index('idx_orders_funnel_id', 'orders', ['funnel_id'])
    op.create_index('idx_orders_contact_id', 'orders', ['contact_id'])
    op.create_index('idx_orders_status', 'orders', ['status'])
    op.create_index('idx_orders_payment_status', 'orders', ['payment_status'])
    op.create_index('idx_orders_created_at', 'orders', ['created_at'])
    op.create_index('idx_orders_order_number', 'orders', ['order_number'])

    # Create order_items table
    op.create_table(
        'order_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('order_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('orders.id', ondelete='CASCADE'), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('products.id'), nullable=False),
        sa.Column('product_name', sa.String(255), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('unit_price_cents', sa.Integer(), nullable=False),
        sa.Column('tax_cents', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('discount_cents', sa.Integer(), server_default='0'),
        sa.Column('total_cents', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
    )
    op.create_index('idx_order_items_order_id', 'order_items', ['order_id'])
    op.create_index('idx_order_items_product_id', 'order_items', ['product_id'])

    # Create order_bumps table
    op.create_table(
        'order_bumps',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('order_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('orders.id', ondelete='CASCADE'), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('products.id'), nullable=False),
        sa.Column('product_name', sa.String(255), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('unit_price_cents', sa.Integer(), nullable=False),
        sa.Column('total_cents', sa.Integer(), nullable=False),
        sa.Column('accepted_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
    )
    op.create_index('idx_order_bumps_order_id', 'order_bumps', ['order_id'])

    # Create order_upsells table
    op.create_table(
        'order_upsells',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('order_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('orders.id', ondelete='CASCADE'), nullable=False),
        sa.Column('funnel_step_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('funnel_steps.id'), nullable=False),
        sa.Column('offer_type', sa.String(10), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('products.id'), nullable=False),
        sa.Column('product_name', sa.String(255), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('unit_price_cents', sa.Integer(), nullable=False),
        sa.Column('total_cents', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='accepted'),
        sa.Column('stripe_payment_intent_id', sa.String(255), unique=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('responded_at', sa.DateTime()),
    )
    op.create_index('idx_order_upsells_order_id', 'order_upsells', ['order_id'])

    # Create refunds table
    op.create_table(
        'refunds',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('order_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('orders.id', ondelete='CASCADE'), nullable=False),
        sa.Column('amount_cents', sa.Integer(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('stripe_refund_id', sa.String(255), unique=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('completed_at', sa.DateTime()),
    )
    op.create_index('idx_refunds_order_id', 'refunds', ['order_id'])
    op.create_index('idx_refunds_status', 'refunds', ['status'])


def downgrade():
    op.drop_table('refunds')
    op.drop_table('order_upsells')
    op.drop_table('order_bumps')
    op.drop_table('order_items')
    op.drop_table('orders')
