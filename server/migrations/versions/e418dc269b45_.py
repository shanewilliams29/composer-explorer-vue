"""empty message

Revision ID: e418dc269b45
Revises: a0144bb26b94
Create Date: 2023-04-02 21:53:07.761231

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e418dc269b45'
down_revision = 'a0144bb26b94'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('performers', schema=None) as batch_op:
        batch_op.add_column(sa.Column('hidden', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('performers', schema=None) as batch_op:
        batch_op.drop_column('hidden')

    # ### end Alembic commands ###
