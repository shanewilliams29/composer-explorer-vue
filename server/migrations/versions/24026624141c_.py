"""empty message

Revision ID: 24026624141c
Revises: 5c489d2a83b2
Create Date: 2021-05-12 10:41:46.018027

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '24026624141c'
down_revision = '5c489d2a83b2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'user', ['display_name'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'user', type_='unique')
    # ### end Alembic commands ###
