"""cat2

Revision ID: 3d53069c7608
Revises: bb1f827f568d
Create Date: 2024-07-12 17:11:48.427227

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel             # NEW


# revision identifiers, used by Alembic.
revision = '3d53069c7608'
down_revision = 'bb1f827f568d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###