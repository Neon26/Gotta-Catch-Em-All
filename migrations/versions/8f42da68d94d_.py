"""empty message

Revision ID: 8f42da68d94d
Revises: c7b13767eab7
Create Date: 2022-08-04 21:28:05.201717

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8f42da68d94d'
down_revision = 'c7b13767eab7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('pokemon', sa.Column('created_on', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('pokemon', 'created_on')
    # ### end Alembic commands ###
