"""add oauth fields to user

Revision ID: e569018c1e31
Revises: 1df7d129a5e6
Create Date: 2026-04-18 00:45:17.154983

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'e569018c1e31'
down_revision: Union[str, Sequence[str], None] = '1df7d129a5e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.alter_column('users', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.DateTime(timezone=True),
               existing_nullable=True)



def downgrade() -> None:
    """Downgrade schema."""

    op.alter_column('users', 'created_at',
               existing_type=sa.DateTime(timezone=True),
               type_=postgresql.TIMESTAMP(),
               existing_nullable=True)
    # ### end Alembic commands ###
