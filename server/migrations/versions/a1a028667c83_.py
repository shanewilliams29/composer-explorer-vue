"""empty message

Revision ID: a1a028667c83
Revises: c7f4c3524259
Create Date: 2022-05-01 08:11:09.254976

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1a028667c83'
down_revision = 'c7f4c3524259'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('work_albums', sa.Column('compilation', sa.Boolean(), nullable=True))
    op.add_column('work_albums', sa.Column('label', sa.String(length=1024), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('work_albums', 'label')
    op.drop_column('work_albums', 'compilation')
    # ### end Alembic commands ###
