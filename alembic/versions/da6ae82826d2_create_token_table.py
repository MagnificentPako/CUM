"""create token table

Revision ID: da6ae82826d2
Revises: 
Create Date: 2022-08-09 22:39:47.089176

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'da6ae82826d2'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'char_tokens',
        sa.Column('id', sa.String, primary_key=True),
        sa.Column('token_type', sa.String),
        sa.Column('access_token', sa.String),
        sa.Column('refresh_token', sa.String),
        sa.Column('character_id', sa.Integer),
        sa.Column('expires_at', sa.Integer)
    )


def downgrade() -> None:
    op.drop_table('char_tokens')
