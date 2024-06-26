"""empty message

Revision ID: a23b173bf46e
Revises: a1a028667c83
Create Date: 2022-05-01 08:20:28.943618

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a23b173bf46e'
down_revision = 'a1a028667c83'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('work_albums', sa.Column('title', sa.String(length=2048), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('work_albums', 'title')
    # ### end Alembic commands ###
