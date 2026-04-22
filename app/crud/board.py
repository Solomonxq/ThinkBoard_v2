from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.board import Board
from app.models.user import User
from app.schemas.board import BoardCreate


async def get_user_by_id_simple(db: AsyncSession, user_id: str) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalars().first()


async def get_users_by_ids(db: AsyncSession, user_ids: list[str]) -> list[User]:
    result = await db.execute(select(User).where(User.id.in_(user_ids)))
    return result.scalars().all()


async def get_board_by_id(db: AsyncSession, board_id: str) -> Board | None:
    result = await db.execute(
        select(Board)
        .options(selectinload(Board.members))
        .where(Board.id == board_id)
    )
    return result.scalars().first()


async def create_board(db: AsyncSession, data: BoardCreate, owner_id: str) -> Board:
    board = Board(
        board_name=data.board_name,
        owner_id=owner_id,
        access=data.access,
        description=data.description,
    )
    db.add(board)
    await db.commit()

    return await get_board_by_id(db, board.id)