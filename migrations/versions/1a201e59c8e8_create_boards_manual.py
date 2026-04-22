from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '1a201e59c8e8'
down_revision: Union[str, Sequence[str], None] = 'e2555413ec88'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'boards',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('board_name', sa.String(25), nullable=False, index=True),
        sa.Column('owner_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table(
        'boards_members',
        sa.Column('board_id', sa.String(36), sa.ForeignKey('boards.id'), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), primary_key=True),
    )

def downgrade() -> None:
    op.drop_table('boards_members')
    op.drop_table('boards')
