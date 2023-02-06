"""create corp wallet table

Revision ID: 3045239c0491
Revises: 3f4ff56e1ccf
Create Date: 2023-02-06 21:37:33.564180

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3045239c0491'
down_revision = '3f4ff56e1ccf'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        'corp_wallet',
        sa.Column('id', sa.BigInteger, primary_key=True),
        sa.Column('amount', sa.BigInteger),
        sa.Column('balance', sa.Float),
        sa.Column('context_id', sa.BigInteger),
        sa.Column('context_id_type', sa.String),
        sa.Column('date', sa.DateTime),
        sa.Column('description', sa.String),
        sa.Column('first_party_id', sa.BigInteger, primary_key=True),
        sa.Column('reason', sa.String),
        sa.Column('ref_type', sa.String),
        sa.Column('second_party_id', sa.BigInteger, primary_key=True),
        sa.Column('source', sa.String))


def downgrade() -> None:
    op.drop_table('corp_wallet')