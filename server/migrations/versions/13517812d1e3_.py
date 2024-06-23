"""empty message

Revision ID: 13517812d1e3
Revises: e72ebb739321
Create Date: 2020-04-21 09:46:53.745536

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '13517812d1e3'
down_revision = 'e72ebb739321'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('artists',
    sa.Column('id', sa.String(length=128), nullable=False),
    sa.Column('name', sa.String(length=256), nullable=True),
    sa.Column('workid', sa.String(length=24), nullable=True),
    sa.Column('album_id', sa.String(length=46), nullable=True),
    sa.Column('composer', sa.String(length=48), nullable=True),
    sa.Column('count', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['album_id'], ['work_albums.id'], ),
    sa.ForeignKeyConstraint(['workid'], ['work_list.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('artists')
    # ### end Alembic commands ###
