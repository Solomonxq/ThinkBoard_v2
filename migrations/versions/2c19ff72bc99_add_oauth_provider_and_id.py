from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '2c19ff72bc99'
down_revision: Union[str, Sequence[str], None] = 'e569018c1e31'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('oauth_provider', sa.String(), nullable=True))
    op.add_column('users', sa.Column('oauth_id', sa.String(), nullable=True))

def downgrade() -> None:
    op.drop_column('users', 'oauth_id')
    op.drop_column('users', 'oauth_provider')