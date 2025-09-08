"""add content column to post table

Revision ID: 5aae689e232a
Revises: 3e03f5813f84
Create Date: 2025-09-08 10:46:34.879566

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5aae689e232a'
down_revision: Union[str, Sequence[str], None] = '3e03f5813f84'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('posts', sa.Column('content', sa.String(), nullable=False))
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('posts', 'content')
    pass
