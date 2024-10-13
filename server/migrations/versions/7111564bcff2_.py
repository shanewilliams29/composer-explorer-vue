"""empty message

Revision ID: 7111564bcff2
Revises: 7bc1fc22cbdc
Create Date: 2020-04-28 11:29:30.104846

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7111564bcff2'
down_revision = '7bc1fc22cbdc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('composer_list', sa.Column('view', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('composer_list', 'view')
    # ### end Alembic commands ###