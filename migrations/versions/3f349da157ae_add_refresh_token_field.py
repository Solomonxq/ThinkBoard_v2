from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '3f349da157ae'
down_revision: Union[str, Sequence[str], None] = 'b17dd8b57b97'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column('users', 'refresh_token')
