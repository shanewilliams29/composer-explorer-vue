"""empty message

Revision ID: 49b4ac4076b6
Revises: 24026624141c
Create Date: 2021-05-12 11:10:19.817326

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '49b4ac4076b6'
down_revision = '24026624141c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('admin', table_name='user')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index('admin', 'user', ['admin'], unique=True)
    # ### end Alembic commands ###