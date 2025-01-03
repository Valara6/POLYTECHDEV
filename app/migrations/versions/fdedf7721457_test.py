"""test

Revision ID: fdedf7721457
Revises: 
Create Date: 2024-11-29 20:06:48.455739

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fdedf7721457'
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

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('lots', schema=None) as batch_op:
        batch_op.alter_column('lot_name',
               existing_type=sa.String(length=255),
               type_=sa.TEXT(length=255),
               existing_nullable=False)

    # ### end Alembic commands ###
