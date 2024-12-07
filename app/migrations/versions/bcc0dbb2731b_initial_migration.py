"""Initial migration

Revision ID: bcc0dbb2731b
Revises: 
Create Date: 2024-12-07 10:13:18.130760

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bcc0dbb2731b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('lots', schema=None) as batch_op:
        batch_op.alter_column('lot_name',
               existing_type=sa.TEXT(length=255),
               type_=sa.String(length=255),
               existing_nullable=False)
        batch_op.drop_constraint('fk_lots_auction_id_auctions', type_='foreignkey')
        batch_op.create_foreign_key(batch_op.f('fk_lots_auction_id_auctions'), 'auctions', ['auction_id'], ['id'], ondelete='CASCADE')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('lots', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_lots_auction_id_auctions'), type_='foreignkey')
        batch_op.create_foreign_key(None, 'auctions', ['auction_id'], ['id'])
        batch_op.alter_column('lot_name',
               existing_type=sa.String(length=255),
               type_=sa.TEXT(length=255),
               existing_nullable=False)

    # ### end Alembic commands ###
