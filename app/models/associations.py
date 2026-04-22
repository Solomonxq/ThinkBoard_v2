from sqlalchemy import Column, String, ForeignKey, Table
from app.db.base import Base

board_members = Table(
    "boards_members",
    Base.metadata,
    Column("board_id", String(36), ForeignKey("boards.id"), primary_key=True),
    Column("user_id", String(36), ForeignKey("users.id"), primary_key=True),
)


user_favorite_boards = Table(
    "user_user_favorite_boards",
    Base.metadata,
    Column("user_id",String(36),ForeignKey("users.id"), primary_key=True),
    Column("board_id",String(36),ForeignKey("boards.id"),primary_key=True)

)