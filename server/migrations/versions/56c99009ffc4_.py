"""empty message

Revision ID: 56c99009ffc4
Revises: 448e7a374010
Create Date: 2022-12-07 19:11:21.896853

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '56c99009ffc4'
down_revision = '448e7a374010'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('work_images')
    op.drop_index('ix_post_timestamp', table_name='post')
    op.drop_table('post')
    op.drop_table('followers')
    op.drop_index('ix_album_like_user_id', table_name='album_like')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index('ix_album_like_user_id', 'album_like', ['user_id'], unique=False)
    op.create_table('followers',
    sa.Column('follower_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.Column('followed_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['followed_id'], ['user.id'], name='followers_ibfk_1'),
    sa.ForeignKeyConstraint(['follower_id'], ['user.id'], name='followers_ibfk_2'),
    mysql_default_charset='utf8',
    mysql_engine='InnoDB'
    )
    op.create_table('post',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('body', mysql.VARCHAR(length=140), nullable=True),
    sa.Column('timestamp', mysql.DATETIME(), nullable=True),
    sa.Column('user_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='post_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset='utf8',
    mysql_engine='InnoDB'
    )
    op.create_index('ix_post_timestamp', 'post', ['timestamp'], unique=False)
    op.create_table('work_images',
    sa.Column('id', mysql.VARCHAR(length=128), nullable=False),
    sa.Column('genre', mysql.VARCHAR(length=128), nullable=True),
    sa.Column('url', mysql.TEXT(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset='utf8',
    mysql_engine='InnoDB'
    )
    # ### end Alembic commands ###
