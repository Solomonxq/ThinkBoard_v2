from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '1bde1a919ade'
down_revision: Union[str, Sequence[str], None] = '261fb0ae5689'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column('users', 'avatar_url')
    op.drop_column('users', 'bio')
