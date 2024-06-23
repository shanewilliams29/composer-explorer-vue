"""empty message

Revision ID: 506f492be358
Revises: bc6043c343b9
Create Date: 2023-05-15 15:41:26.996458

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '506f492be358'
down_revision = 'bc6043c343b9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('message', schema=None) as batch_op:
        batch_op.drop_index('ix_message_timestamp')

    op.drop_table('message')
    op.drop_table('artist_albums')
    op.drop_table('favorites')
    op.drop_table('visits')
    with op.batch_alter_table('comment', schema=None) as batch_op:
        batch_op.drop_index('ix_comment_timestamp')

    op.drop_table('comment')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('comment',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('body', mysql.TEXT(), nullable=True),
    sa.Column('timestamp', mysql.DATETIME(), nullable=True),
    sa.Column('workid', mysql.VARCHAR(length=24), nullable=True),
    sa.Column('user_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='comment_ibfk_1'),
    sa.ForeignKeyConstraint(['workid'], ['work_list.id'], name='comment_ibfk_2'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb3_general_ci',
    mysql_default_charset='utf8mb3',
    mysql_engine='InnoDB'
    )
    with op.batch_alter_table('comment', schema=None) as batch_op:
        batch_op.create_index('ix_comment_timestamp', ['timestamp'], unique=False)

    op.create_table('visits',
    sa.Column('work_id', mysql.VARCHAR(length=24), nullable=True),
    sa.Column('user_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='visits_ibfk_1'),
    sa.ForeignKeyConstraint(['work_id'], ['work_list.id'], name='visits_ibfk_2'),
    mysql_collate='utf8mb3_general_ci',
    mysql_default_charset='utf8mb3',
    mysql_engine='InnoDB'
    )
    op.create_table('favorites',
    sa.Column('composer_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.Column('user_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['composer_id'], ['composer_list.id'], name='favorites_ibfk_1'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='favorites_ibfk_2'),
    mysql_collate='utf8mb3_general_ci',
    mysql_default_charset='utf8mb3',
    mysql_engine='InnoDB'
    )
    op.create_table('artist_albums',
    sa.Column('id', mysql.VARCHAR(length=24), nullable=False),
    sa.Column('results', mysql.MEDIUMTEXT(), nullable=True),
    sa.Column('artists', mysql.TEXT(), nullable=True),
    sa.Column('updated', mysql.DATETIME(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb3_general_ci',
    mysql_default_charset='utf8mb3',
    mysql_engine='InnoDB'
    )
    op.create_table('message',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('sender_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.Column('recipient_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.Column('body', mysql.TEXT(), nullable=True),
    sa.Column('timestamp', mysql.DATETIME(), nullable=True),
    sa.Column('recipient_visible', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True),
    sa.Column('sender_visible', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['recipient_id'], ['user.id'], name='message_ibfk_1'),
    sa.ForeignKeyConstraint(['sender_id'], ['user.id'], name='message_ibfk_2'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb3_general_ci',
    mysql_default_charset='utf8mb3',
    mysql_engine='InnoDB'
    )
    with op.batch_alter_table('message', schema=None) as batch_op:
        batch_op.create_index('ix_message_timestamp', ['timestamp'], unique=False)

    # ### end Alembic commands ###
