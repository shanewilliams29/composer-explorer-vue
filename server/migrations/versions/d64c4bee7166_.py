"""empty message

Revision ID: d64c4bee7166
Revises: 3b4dd5d170d6
Create Date: 2022-06-06 10:32:46.650451

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd64c4bee7166'
down_revision = '3b4dd5d170d6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('work_list', sa.Column('openopus', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('work_list', 'openopus')
    # ### end Alembic commands ###
