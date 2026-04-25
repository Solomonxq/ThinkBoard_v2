from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models import board
from app.models.board import Board
from app.models.user import User
from app.schemas.board import BoardCreate





async def create_board(db:AsyncSession,data: BoardCreate, owner_id:str) ->Board:
    board = Board(
        board_name=data.board_name,
        owner_id=owner_id,
        access=data.access,
        description=data.description,
    )
    db.add(board)
    await db.commit()

    return board

async def get_board_by_id(db: AsyncSession, board_id: str) -> Board | None:
    result = await db.execute(
        select(Board)
        .options(selectinload(Board.members))
        .where(Board.id == board_id)
    )
    return result.scalars().first()


async def delete_board(db: AsyncSession, board_id: str):
    result = await db.execute(select(Board).where(Board.id == board_id))
    board = result.scalars().first()
    if board:
        await db.delete(board)
        await db.commit()

async def is_owner(db: AsyncSession, user_id: str, board_id: str) -> bool:
    result = await db.execute(
        select(Board).where(Board.id == board_id, Board.owner_id == user_id)
    )
    return result.scalars().first() is not None

async def add_user_to_board(db: AsyncSession, board_id: str, user_id: str):
    board.members.append(User(id=user_id))
    await db.commit()

async def delete_user_from_board(db: AsyncSession, board: Board, user_id: str):
    board.members = [member for member in board.members if member.id != user_id]
    await db.commit()


async def delete_users_from_board(db: AsyncSession, board: Board, user_ids: list[str]):
    board.members = [member for member in board.members if member.id not in user_ids]
    await db.commit()


async def add_to_favorite_boards(db: AsyncSession, user: User, board_id: str):
    user.favorite_boards.append(Board(id=board_id))
    await db.commit()

async def remove_from_favorite_boards(db: AsyncSession, user: User, board_id: str):
    user.favorite_boards = [board for board in user.favorite_boards if board.id != board_id]
    await db.commit()