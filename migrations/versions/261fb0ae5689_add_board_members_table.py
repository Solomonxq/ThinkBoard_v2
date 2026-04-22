from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '261fb0ae5689'
down_revision: Union[str, Sequence[str], None] = '1a201e59c8e8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column('boards', 'access')
