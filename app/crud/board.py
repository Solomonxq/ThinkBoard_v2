import json

from app.core.redis import get_redis
from app.models.associations import board_members, user_favorite_boards
from app.models.board import Board
from app.models.user import User
from app.schemas.board import BoardCreate
from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


async def create_board(db: AsyncSession, data: BoardCreate, owner_id: str) -> Board:
    board = Board(
        board_name=data.board_name,
        owner_id=owner_id,
        access=data.access,
        description=data.description,
    )
    db.add(board)
    await db.flush()

    board_id = board.id

    owner_result = await db.execute(select(User).where(User.id == owner_id))
    owner = owner_result.scalars().first()

    if owner:
        await db.execute(
            board_members.insert().values(
                board_id=board_id,
                user_id=owner_id,
            )
        )
        board.__dict__["members"] = [owner]

    await db.commit()
    return board


async def get_board_by_id(db: AsyncSession, board_id: str) -> Board | None:
    redis = await get_redis()
    cache_key = f"board:{board_id}"

    cached = await redis.get(cache_key)
    if cached:
        data = json.loads(cached)
        board = Board(**{k: v for k, v in data.items() if k != "members"})
        board.__dict__["members"] = [User(**m) for m in data.get("members", [])]
        return board

    result = await db.execute(
        select(Board)
        .options(selectinload(Board.members))
        .where(Board.id == board_id)
    )
    board = result.scalars().first()

    if board:
        data = {
            "id": board.id,
            "board_name": board.board_name,
            "owner_id": board.owner_id,
            "access": board.access,
            "description": board.description,
            "created_at": board.created_at.isoformat() if board.created_at else None,
            "members": [
                {"id": m.id, "username": m.username, "email": m.email}
                for m in board.members
            ],
        }
        await redis.setex(cache_key, 120, json.dumps(data))

    return board


async def invalidate_board_cache(board_id: str):
    redis = await get_redis()
    await redis.delete(f"board:{board_id}")


async def delete_board(db: AsyncSession, board_id: str):
    result = await db.execute(select(Board).where(Board.id == board_id))
    board = result.scalars().first()
    if board:
        await db.delete(board)
        await db.commit()
        await invalidate_board_cache(board_id)


async def is_owner(db: AsyncSession, user_id: str, board_id: str) -> bool:
    result = await db.execute(
        select(exists().where(
            Board.id == board_id,
            Board.owner_id == user_id,
        ))
    )
    return result.scalar()


async def add_user_to_board(db: AsyncSession, board_id: str, user_id: str):
    result = await db.execute(
        select(Board)
        .options(selectinload(Board.members))
        .where(Board.id == board_id)
    )
    board = result.scalars().first()
    if not board:
        return

    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalars().first()
    if not user:
        return

    board.members.append(user)
    await db.commit()
    await invalidate_board_cache(board_id)


async def delete_user_from_board(db: AsyncSession, board: Board, user_id: str):
    board.members = [m for m in board.members if m.id != user_id]
    await db.commit()
    await invalidate_board_cache(board.id)


async def delete_users_from_board(db: AsyncSession, board: Board, user_ids: list[str]):
    board.members = [m for m in board.members if m.id not in user_ids]
    await db.commit()
    await invalidate_board_cache(board.id)


async def add_to_favorite_boards(db: AsyncSession, user_id: str, board_id: str):
    already = await db.execute(
        select(exists().where(
            user_favorite_boards.c.user_id == user_id,
            user_favorite_boards.c.board_id == board_id,
        ))
    )
    if not already.scalar():
        await db.execute(
            user_favorite_boards.insert().values(
                user_id=user_id,
                board_id=board_id,
            )
        )
        await db.commit()


async def remove_from_favorite_boards(db: AsyncSession, user_id: str, board_id: str):
    await db.execute(
        user_favorite_boards.delete().where(
            user_favorite_boards.c.user_id == user_id,
            user_favorite_boards.c.board_id == board_id,
        )
    )
    await db.commit()


async def already_member_of_board(db: AsyncSession, user_id: str, board_id: str) -> bool:
    result = await db.execute(
        select(exists().where(
            board_members.c.board_id == board_id,
            board_members.c.user_id == user_id,
        ))
    )
    return result.scalar()