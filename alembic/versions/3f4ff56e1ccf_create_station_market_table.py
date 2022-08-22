"""create station market table

Revision ID: 3f4ff56e1ccf
Revises: da6ae82826d2
Create Date: 2022-08-10 00:41:17.479414

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3f4ff56e1ccf'
down_revision = 'da6ae82826d2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'item_types',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String),
        sa.Column('category', sa.String)
    )
    op.create_table(
        'station_market_iterations',
        sa.Column('source_char', sa.String, sa.ForeignKey('char_tokens.id'), primary_key=True),
        sa.Column('iteration', sa.Integer, primary_key=True)    
    )
    op.create_table(
        'station_market',
        sa.Column('id', sa.BigInteger, primary_key=True),
        sa.Column('iteration', sa.BigInteger),
        sa.Column('duration', sa.BigInteger),
        sa.Column('is_buy_order', sa.Boolean),
        sa.Column('issued', sa.DateTime),
        sa.Column('location_id', sa.BigInteger),
        sa.Column('min_volume', sa.BigInteger),
        sa.Column('order_id', sa.BigInteger),
        sa.Column('price', sa.Float),
        sa.Column('range', sa.String),
        sa.Column('type_id', sa.BigInteger, sa.ForeignKey('item_types.id')),
        sa.Column('volume_remain', sa.BigInteger),
        sa.Column('volume_total', sa.BigInteger),
        sa.Column('source_char', sa.String, sa.ForeignKey('char_tokens.id'))
    )


def downgrade() -> None:
    op.drop_table('item_types')
    op.drop_table('station_market_iterations')
    op.drop_table('station_market')