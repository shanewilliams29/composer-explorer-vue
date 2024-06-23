"""empty message

Revision ID: fb9fccf3b8b6
Revises: 394254ee2d6b
Create Date: 2020-05-03 21:26:46.745878

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fb9fccf3b8b6'
down_revision = '394254ee2d6b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('message', sa.Column('recipient_visible', sa.Boolean(), nullable=True))
    op.add_column('message', sa.Column('sender_visible', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('message', 'sender_visible')
    op.drop_column('message', 'recipient_visible')
    # ### end Alembic commands ###
