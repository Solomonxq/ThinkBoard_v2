from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'da59b34bc6e2'
down_revision: Union[str, Sequence[str], None] = '32aaec8013f4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass
