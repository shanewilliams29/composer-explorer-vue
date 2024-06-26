"""empty message

Revision ID: 188f2980f614
Revises: a17b3ab6a835
Create Date: 2022-12-09 13:15:51.317777

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '188f2980f614'
down_revision = 'a17b3ab6a835'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('ix_artists_name'), 'artists', ['name'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_artists_name'), table_name='artists')
    # ### end Alembic commands ###
