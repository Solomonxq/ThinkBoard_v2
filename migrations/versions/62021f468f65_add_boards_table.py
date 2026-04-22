from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '62021f468f65'
down_revision: Union[str, Sequence[str], None] = '49796ce9c0d2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass
