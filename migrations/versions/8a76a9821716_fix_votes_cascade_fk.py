"""fix votes cascade fk

Revision ID: 8a76a9821716
Revises: 1fd8c8df1924
Create Date: 2026-05-03 20:56:41.658655

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8a76a9821716'
down_revision: Union[str, Sequence[str], None] = '1fd8c8df1924'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

from alembic import op


def upgrade():
    op.drop_constraint("votes_idea_id_fkey", "votes", type_="foreignkey")
    op.create_foreign_key(
        "votes_idea_id_fkey",
        "votes",
        "ideas",
        ["idea_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade():
    op.drop_constraint("votes_idea_id_fkey", "votes", type_="foreignkey")
    op.create_foreign_key(
        "votes_idea_id_fkey",
        "votes",
        "ideas",
        ["idea_id"],
        ["id"],
    )