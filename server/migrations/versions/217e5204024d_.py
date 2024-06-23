"""empty message

Revision ID: 217e5204024d
Revises: 2a17ce282348
Create Date: 2023-03-31 13:18:44.105353

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '217e5204024d'
down_revision = '2a17ce282348'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('performer_albums',
    sa.Column('performer_id', sa.Integer(), nullable=True),
    sa.Column('album_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['album_id'], ['work_albums.id'], ),
    sa.ForeignKeyConstraint(['performer_id'], ['performers.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('performer_albums')
    # ### end Alembic commands ###
