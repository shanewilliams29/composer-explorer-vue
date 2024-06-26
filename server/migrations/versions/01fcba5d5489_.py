"""empty message

Revision ID: 01fcba5d5489
Revises: f74b05e83ab7
Create Date: 2023-04-04 19:02:02.238863

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '01fcba5d5489'
down_revision = 'f74b05e83ab7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('work_list', schema=None) as batch_op:
        batch_op.add_column(sa.Column('duration', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('work_list', schema=None) as batch_op:
        batch_op.drop_column('duration')

    # ### end Alembic commands ###
