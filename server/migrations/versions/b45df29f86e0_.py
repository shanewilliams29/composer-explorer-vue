"""empty message

Revision ID: b45df29f86e0
Revises: 5d2e03d78c6e
Create Date: 2020-05-05 13:48:54.880599

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'b45df29f86e0'
down_revision = '5d2e03d78c6e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('forum_post_ibfk_3', 'forum_post', type_='foreignkey')
    op.drop_column('forum_post', 'last_commenter')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('forum_post', sa.Column('last_commenter', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.create_foreign_key('forum_post_ibfk_3', 'forum_post', 'user', ['last_commenter'], ['id'])
    # ### end Alembic commands ###
