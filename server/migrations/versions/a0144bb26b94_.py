"""empty message

Revision ID: a0144bb26b94
Revises: 52d62c5c9694
Create Date: 2023-04-02 20:54:58.596792

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a0144bb26b94'
down_revision = '52d62c5c9694'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('performers', schema=None) as batch_op:
        batch_op.add_column(sa.Column('description', sa.String(length=256), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('performers', schema=None) as batch_op:
        batch_op.drop_column('description')

    # ### end Alembic commands ###
