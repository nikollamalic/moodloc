"""empty message

Revision ID: b8f02f0dfa2d
Revises: ca5437f0fae8
Create Date: 2019-11-27 19:16:47.696723

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b8f02f0dfa2d'
down_revision = 'ca5437f0fae8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('capture', sa.Column('location_name', sa.String(length=256), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('capture', 'location_name')
    # ### end Alembic commands ###
