"""empty message

Revision ID: bc6043c343b9
Revises: 5d5da7b75989
Create Date: 2023-05-08 13:34:04.136825

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'bc6043c343b9'
down_revision = '5d5da7b75989'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('artists', schema=None) as batch_op:
        batch_op.drop_index('ix_artists_name')

    op.drop_table('artists')
    with op.batch_alter_table('artist_list', schema=None) as batch_op:
        batch_op.drop_index('ix_artist_list_timestamp')

    op.drop_table('artist_list')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('artist_list',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('timestamp', mysql.DATETIME(), nullable=True),
    sa.Column('content', mysql.LONGTEXT(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb3_general_ci',
    mysql_default_charset='utf8mb3',
    mysql_engine='InnoDB'
    )
    with op.batch_alter_table('artist_list', schema=None) as batch_op:
        batch_op.create_index('ix_artist_list_timestamp', ['timestamp'], unique=False)

    op.create_table('artists',
    sa.Column('id', mysql.VARCHAR(length=128), nullable=False),
    sa.Column('name', mysql.VARCHAR(length=256), nullable=True),
    sa.Column('workid', mysql.VARCHAR(length=24), nullable=True),
    sa.Column('album_id', mysql.VARCHAR(length=46), nullable=True),
    sa.Column('composer', mysql.VARCHAR(length=48), nullable=True),
    sa.Column('count', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.Column('spotify_id', mysql.VARCHAR(length=48), nullable=True),
    sa.Column('spotify_img', mysql.VARCHAR(length=128), nullable=True),
    sa.ForeignKeyConstraint(['album_id'], ['work_albums.id'], name='artists_ibfk_1'),
    sa.ForeignKeyConstraint(['workid'], ['work_list.id'], name='artists_ibfk_2'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb3_general_ci',
    mysql_default_charset='utf8mb3',
    mysql_engine='InnoDB'
    )
    with op.batch_alter_table('artists', schema=None) as batch_op:
        batch_op.create_index('ix_artists_name', ['name'], unique=False)

    # ### end Alembic commands ###
