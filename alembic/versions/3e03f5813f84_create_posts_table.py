"""create posts table

Revision ID: 3e03f5813f84
Revises: 
Create Date: 2025-09-08 09:19:06.438022

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3e03f5813f84'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'posts',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('title', sa.String(), nullable=False))    
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('posts')
    pass
