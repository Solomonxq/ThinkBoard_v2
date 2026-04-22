from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.logging import setup_logging
from app.crud.board import (
    get_board_by_id,
    get_user_by_id_simple,
    get_users_by_ids,
    create_board as crud_create_board
)
from app.schemas.board import BoardCreate
from app.models.board import Board
from app.models.user import User


class BoardService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.logger = setup_logging()

    async def _verify_board_owner(self, board: Board, current_user_id: str) -> None:
        if not board:
            raise HTTPException(status_code=404, detail="Board not found")
        if board.owner_id != current_user_id:
            raise HTTPException(status_code=403, detail="Only owner can perform this action")

    async def _commit_and_refresh(self, obj: User) -> None:
        try:
            await self.db.commit()
            await self.db.refresh(obj)
        except Exception as e:
            await self.db.rollback()
            self.logger.error(f"Database error: {e}")
            raise

    async def create_board(self, data: BoardCreate, owner_id: str) -> Board:
        self.logger.info(f"Creating board '{data.board_name}' for owner {owner_id}")
        return await crud_create_board(self.db, data, owner_id)

    async def add_member(self, board_id: str, user_id: str, current_user_id: str) -> Board:
        self.logger.info(f"Adding member {user_id} to board {board_id}")
        board = await get_board_by_id(self.db, board_id)
        await self._verify_board_owner(board, current_user_id)

        user = await get_user_by_id_simple(self.db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if user in board.members:
            raise HTTPException(status_code=400, detail="User already a member")

        board.members.append(user)
        await self.db.commit()
        return await get_board_by_id(self.db, board_id)

    async def remove_member(self, board_id: str, user_id: str, current_user_id: str) -> Board:
        self.logger.info(f"Removing member {user_id} from board {board_id}")
        board = await get_board_by_id(self.db, board_id)
        await self._verify_board_owner(board, current_user_id)

        user = await get_user_by_id_simple(self.db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if user not in board.members:
            raise HTTPException(status_code=400, detail="User is not a member")

        board.members.remove(user)
        await self.db.commit()
        return await get_board_by_id(self.db, board_id)

    async def bulk_add_members(self, board_id: str, user_ids: list[str], current_user_id: str) -> Board:
        self.logger.info(f"Bulk adding {len(user_ids)} members to board {board_id}")
        board = await get_board_by_id(self.db, board_id)
        await self._verify_board_owner(board, current_user_id)

        users = await get_users_by_ids(self.db, user_ids)
        if len(users) != len(user_ids):
            raise HTTPException(status_code=404, detail="One or more users not found")

        for user in users:
            if user not in board.members:
                board.members.append(user)

        await self.db.commit()
        return await get_board_by_id(self.db, board_id)

    async def bulk_remove_members(self, board_id: str, user_ids: list[str], current_user_id: str) -> Board:
        self.logger.info(f"Bulk removing {len(user_ids)} members from board {board_id}")
        board = await get_board_by_id(self.db, board_id)
        await self._verify_board_owner(board, current_user_id)

        users = await get_users_by_ids(self.db, user_ids)
        if len(users) != len(user_ids):
            raise HTTPException(status_code=404, detail="One or more users not found")

        for user in users:
            if user in board.members:
                board.members.remove(user)

        await self.db.commit()
        return await get_board_by_id(self.db, board_id)

    async def add_to_favorites(self, board_id: str, current_user: User) -> User:
        self.logger.info(f"Adding board {board_id} to favorites for user {current_user.id}")
        board = await get_board_by_id(self.db, board_id)

        if not board:
            raise HTTPException(status_code=404, detail="Board not found")

        if any(b.id == board_id for b in current_user.favorite_boards):
            raise HTTPException(status_code=400, detail="Already in favorites")

        current_user.favorite_boards.append(board)
        await self._commit_and_refresh(current_user)

        return current_user

    async def remove_from_favorites(self, board_id: str, current_user: User) -> User:
        self.logger.info(f"Removing board {board_id} from favorites for user {current_user.id}")
        board_to_remove = next((b for b in current_user.favorite_boards if b.id == board_id), None)

        if not board_to_remove:
            raise HTTPException(status_code=404, detail="Board not found in favorites")

        current_user.favorite_boards.remove(board_to_remove)
        await self._commit_and_refresh(current_user)

        return current_user