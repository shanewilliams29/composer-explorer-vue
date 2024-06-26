"""empty message

Revision ID: 57c8a27b56c4
Revises: 02de025ac184
Create Date: 2020-05-05 14:07:59.840119

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '57c8a27b56c4'
down_revision = '02de025ac184'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('forum_post', sa.Column('last_comment_id', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('forum_post', 'last_comment_id')
    # ### end Alembic commands ###
