"""fix idea,user,board

Revision ID: 3a706700ea45
Revises: 1ce67a872a12
Create Date: 2026-04-25 13:20:18.947762
"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '3a706700ea45'
down_revision: Union[str, Sequence[str], None] = '1ce67a872a12'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # -----------------------------
    # boards -> users (owner)
    # -----------------------------
    op.drop_constraint(
        "boards_owner_id_fkey",
        "boards",
        type_="foreignkey"
    )
    op.create_foreign_key(
        "boards_owner_id_fkey",
        "boards",
        "users",
        ["owner_id"],
        ["id"],
        ondelete="CASCADE"
    )

    # -----------------------------
    # ideas -> boards
    # -----------------------------
    op.drop_constraint(
        "ideas_board_id_fkey",
        "ideas",
        type_="foreignkey"
    )
    op.create_foreign_key(
        "ideas_board_id_fkey",
        "ideas",
        "boards",
        ["board_id"],
        ["id"],
        ondelete="CASCADE"
    )

    # -----------------------------
    # ideas -> users
    # -----------------------------
    op.drop_constraint(
        "ideas_user_id_fkey",
        "ideas",
        type_="foreignkey"
    )
    op.create_foreign_key(
        "ideas_user_id_fkey",
        "ideas",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE"
    )


def downgrade() -> None:
    # -----------------------------
    # ideas -> users
    # -----------------------------
    op.drop_constraint(
        "ideas_user_id_fkey",
        "ideas",
        type_="foreignkey"
    )
    op.create_foreign_key(
        "ideas_user_id_fkey",
        "ideas",
        "users",
        ["user_id"],
        ["id"]
    )

    # -----------------------------
    # ideas -> boards
    # -----------------------------
    op.drop_constraint(
        "ideas_board_id_fkey",
        "ideas",
        type_="foreignkey"
    )
    op.create_foreign_key(
        "ideas_board_id_fkey",
        "ideas",
        "boards",
        ["board_id"],
        ["id"]
    )

    # -----------------------------
    # boards -> users (owner)
    # -----------------------------
    op.drop_constraint(
        "boards_owner_id_fkey",
        "boards",
        type_="foreignkey"
    )
    op.create_foreign_key(
        "boards_owner_id_fkey",
        "boards",
        "users",
        ["owner_id"],
        ["id"]
    )