from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '063b9ec714ab'
down_revision: Union[str, Sequence[str], None] = 'a7f3ce393156'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('boards', 'description',
               existing_type=sa.String(length=500),
               type_=sa.VARCHAR(length=30),
               nullable=True)
    op.create_table('user_favorite_boards',
    sa.Column('user_id', sa.VARCHAR(length=36), autoincrement=False, nullable=False),
    sa.Column('board_id', sa.VARCHAR(length=36), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['board_id'], ['boards.id'], name=op.f('user_favorite_boards_board_id_fkey')),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('user_favorite_boards_user_id_fkey')),
    sa.PrimaryKeyConstraint('user_id', 'board_id', name=op.f('user_favorite_boards_pkey'))
    )
    op.drop_table('user_user_favorite_boards')
