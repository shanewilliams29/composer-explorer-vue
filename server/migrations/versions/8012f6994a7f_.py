"""empty message

Revision ID: 8012f6994a7f
Revises: ff7519450ddb
Create Date: 2020-05-05 14:12:01.710295

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '8012f6994a7f'
down_revision = 'ff7519450ddb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('forum_post', sa.Column('last_comment_username', sa.String(length=64), nullable=True))
    op.drop_column('forum_post', 'last_comment_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('forum_post', sa.Column('last_comment_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.drop_column('forum_post', 'last_comment_username')
    # ### end Alembic commands ###
