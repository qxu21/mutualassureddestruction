"""empty message

Revision ID: 8c9b2f7a414d
Revises: 11734b0ba334
Create Date: 2017-10-14 11:55:24.247561

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8c9b2f7a414d'
down_revision = '11734b0ba334'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('player', sa.Column('number', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('player', 'number')
    # ### end Alembic commands ###
