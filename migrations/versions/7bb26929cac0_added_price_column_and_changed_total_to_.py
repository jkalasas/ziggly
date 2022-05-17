"""Added price column and changed total to float in ItemPurchase model

Revision ID: 7bb26929cac0
Revises: 660885b5c144
Create Date: 2022-05-15 17:48:16.830792

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7bb26929cac0'
down_revision = '660885b5c144'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('item_purchase', sa.Column('price', sa.Float(), nullable=False, default=0.0))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('item_purchase', 'price')
    # ### end Alembic commands ###
