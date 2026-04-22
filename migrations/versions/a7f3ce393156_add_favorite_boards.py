from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a7f3ce393156'
down_revision: Union[str, Sequence[str], None] = 'aef553ca2896'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('user_favorite_boards',
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('board_id', sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(['board_id'], ['boards.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('user_id', 'board_id')
    )


def downgrade() -> None:
    op.drop_table('user_favorite_boards')
