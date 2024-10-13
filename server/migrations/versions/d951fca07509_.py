"""empty message

Revision ID: d951fca07509
Revises: 53c17d50af78
Create Date: 2020-05-08 10:38:59.319726

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd951fca07509'
down_revision = '53c17d50af78'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('work_list', sa.Column('suite', sa.String(length=512), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('work_list', 'suite')
    # ### end Alembic commands ###