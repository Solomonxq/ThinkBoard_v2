from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b1340c004a26'
down_revision: Union[str, Sequence[str], None] = '62021f468f65'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass
