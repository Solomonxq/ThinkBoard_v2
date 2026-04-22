from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b17dd8b57b97'
down_revision: Union[str, Sequence[str], None] = '2c19ff72bc99'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('users', 'password',
               existing_type=sa.VARCHAR(),
               nullable=False)
