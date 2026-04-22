from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'da5941d10ca1'
down_revision: Union[str, Sequence[str], None] = '3f349da157ae'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass
