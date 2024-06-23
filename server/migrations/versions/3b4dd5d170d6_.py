"""empty message

Revision ID: 3b4dd5d170d6
Revises: cdcb7f3403e8
Create Date: 2022-05-22 11:01:57.239732

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3b4dd5d170d6'
down_revision = 'cdcb7f3403e8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('composer_list', sa.Column('tier', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('composer_list', 'tier')
    # ### end Alembic commands ###
