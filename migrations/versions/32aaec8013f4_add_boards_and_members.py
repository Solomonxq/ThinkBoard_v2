from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '32aaec8013f4'
down_revision: Union[str, Sequence[str], None] = 'da5941d10ca1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass
