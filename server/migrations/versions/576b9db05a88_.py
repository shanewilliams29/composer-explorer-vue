"""empty message

Revision ID: 576b9db05a88
Revises: 2da16cd278de
Create Date: 2021-05-11 16:14:10.885840

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '576b9db05a88'
down_revision = '2da16cd278de'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('album_like_ibfk_3', 'album_like', type_='foreignkey')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key('album_like_ibfk_3', 'album_like', 'work_albums', ['album_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###
