"""empty message

Revision ID: e753fcb52b89
Revises: 64dd9af50d86
Create Date: 2023-03-31 11:20:54.495021

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e753fcb52b89'
down_revision = '64dd9af50d86'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('performers',
    sa.Column('id', sa.String(length=48), nullable=False),
    sa.Column('name', sa.String(length=256), nullable=True),
    sa.Column('img', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('performers', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_performers_name'), ['name'], unique=False)

    op.create_table('performer_albums',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('performer_id', sa.String(length=48), nullable=True),
    sa.Column('work_id', sa.String(length=24), nullable=True),
    sa.Column('album_id', sa.String(length=46), nullable=True),
    sa.ForeignKeyConstraint(['album_id'], ['work_albums.id'], ),
    sa.ForeignKeyConstraint(['performer_id'], ['performers.id'], ),
    sa.ForeignKeyConstraint(['work_id'], ['work_list.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('performer_albums')
    with op.batch_alter_table('performers', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_performers_name'))

    op.drop_table('performers')
    # ### end Alembic commands ###
