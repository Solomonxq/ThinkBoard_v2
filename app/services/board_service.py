from app.core.logging import setup_logging
from app.crud.board import add_to_favorite_boards as crud_add_to_favorite_boards
from app.crud.board import add_user_to_board as crud_add_user_to_board
from app.crud.board import already_member_of_board as crud_already_member_of_board
from app.crud.board import create_board as crud_create_board
from app.crud.board import delete_board as crud_delete_board
from app.crud.board import delete_user_from_board as crud_delete_user_from_board
from app.crud.board import (
    get_board_by_id,
    get_board_with_ideas,
    get_favorite_board_ids,
    get_user_boards,
    is_owner,
)
from app.crud.board import (
    remove_from_favorite_boards as crud_remove_from_favorite_boards,
)
from app.crud.user import get_user_by_id
from app.models.board import Board
from app.schemas.board import BoardCreate
from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
import traceback
from app.tasks.email_tasks import send_email_task


class BoardService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.logger = setup_logging()


   
    async def create_board(self, data: BoardCreate, owner_id: str) -> Board:
        self.logger.info(f"Creating board '{data.board_name}' for owner {owner_id}")

        user = await get_user_by_id(self.db, owner_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        try:
            board = await crud_create_board(self.db, data, owner_id)

            self.logger.info(
                f"Board '{board.board_name}' created successfully with ID {board.id}"
            )

            send_email_task.delay(
                user.email,
                "Board Created",
                f"Your board '{board.board_name}' has been created successfully!"
            )

            return board

        except Exception:
            self.logger.error(traceback.format_exc())
            raise HTTPException(status_code=500, detail="Failed to create board")

    async def delete_board(self,board_id:str,user_id:str):
        board = await get_board_by_id(self.db, board_id)
        if not board:
            self.logger.error(f"Board with ID {board_id} not found for deletion")
            raise HTTPException(status_code=404, detail="Board not found")
        owner = await is_owner(self.db, user_id, board_id)
        if not owner:
            self.logger.error(f"User {user_id} is not the owner of board {board_id}")
            raise HTTPException(status_code=403, detail="Only owner can delete the board")
        try:
            await crud_delete_board(self.db, board_id)
            self.logger.info(f"Board with ID {board_id} deleted successfully")
            send_email_task.delay(
                board.owner.email,
                "Board Deleted",
                f"Your board '{board.board_name}' has been deleted successfully!"
            )

        except Exception as e:
            self.logger.error(f"Error occurred while deleting board {board_id}: {e}")
            raise HTTPException(status_code=500, detail="Failed to delete board")


    async def add_user_to_board(self, board_id: str, user_id: str,current_id:str):
        user = await get_user_by_id(self.db, user_id)
        if not user:
            self.logger.error(f"User with ID {user_id} not found for adding to board {board_id}")
            raise HTTPException(status_code=404, detail="User not found")
        if not await is_owner(self.db,current_id,board_id):
            self.logger.error(f"User:{current_id} not owner")
            raise HTTPException(status_code=403,detail=f"User:{current_id} not owner")
        board = await get_board_by_id(self.db, board_id)
        if not board:
            self.logger.error(f"Board with ID {board_id} not found for adding user {user_id}")
            raise HTTPException(status_code=404, detail="Board not found")
        if await crud_already_member_of_board(self.db, user_id, board_id):
            self.logger.error(f"User {user_id} is already a member of board {board_id}")
            raise HTTPException(status_code=400, detail="User is already a member of the board")
        try:
            await crud_add_user_to_board(self.db, board_id, user_id)
            send_email_task.delay(
                user.email,
                "Added to Board",
                f"You have been added to the board '{board.board_name}'!"
            )
            self.logger.info(f"User {user_id} added to board {board_id} successfully")
        except ValidationError as e:
            self.logger.error(f"Validation error occurred while adding user {user_id} to board {board_id}: {e}")
            raise HTTPException(status_code=422, detail="Invalid data for adding user to board")
        except Exception as e:
            self.logger.error(f"Error occurred while adding user {user_id} to board {board_id}: {e}")
            raise HTTPException(status_code=500, detail="Failed to add user to board")

    async def delete_user_from_board(self, board_id: str, user_id: str,owner_id:str):
        owner = await is_owner(self.db, owner_id, board_id)
        if not owner:
            self.logger.error(f"User {owner_id} is not the owner of board {board_id} for removing user {user_id}")
            raise HTTPException(status_code=403, detail="Only owner can remove users from the board")
        user = await get_user_by_id(self.db, user_id)
        if not user:
            self.logger.error(f"User with ID {user_id} not found for removing from board {board_id}")
            raise HTTPException(status_code=404, detail="User not found")
        board = await get_board_by_id(self.db, board_id)
        if not board:
            self.logger.error(f"Board with ID {board_id} not found for removing user {user_id}")
            raise HTTPException(status_code=404, detail="Board not found")
        try:
            await crud_delete_user_from_board(self.db, board, user_id)
            send_email_task.delay(
                user.email,
                "Removed from Board",
                f"You have been removed from the board '{board.board_name}'!"
            )
            self.logger.info(f"User {user_id} removed from board {board_id} successfully")
        except ValidationError as e:
            self.logger.error(f"Validation error occurred while removing user {user_id} from board {board_id}: {e}")
            raise HTTPException(status_code=422, detail="Invalid data for removing user from board")
        except Exception as e:
            self.logger.error(f"Error occurred while removing user {user_id} from board {board_id}: {e}")
            raise HTTPException(status_code=500, detail="Failed to remove user from board")

    async def add_users_to_board(self,board_id:str, user_ids:list[str],current_id:str):
        for user_id in user_ids:
            try:
                await self.add_user_to_board(board_id, user_id,current_id)
            except HTTPException as e:
                self.logger.error(f"HTTP error occurred while adding user {user_id} to board {board_id}: {e.detail}")
                raise e
            except Exception as e:
                self.logger.error(f"Error occurred while adding user {user_id} to board {board_id}: {e}")
                raise HTTPException(status_code=500, detail="Failed to add users to board")

    async def delete_users_from_board(self, board_id: str, user_ids: list[str],owner_id):
        board = await get_board_by_id(self.db, board_id)

        if not board:
            self.logger.error(f"Board with ID {board_id} not found for removing users {user_ids}")
            raise HTTPException(status_code=404, detail="Board not found")
        try:
            for user_id in user_ids:
                    await self.delete_user_from_board(board_id,user_id,owner_id)
        except HTTPException as e:
            self.logger.error(f"HTTP error occurred while delete user {user_id} to board {board_id}: {e.detail}")

    async def add_to_favorite_boards(self, user_id: str, board_id: str):
        board = await get_board_by_id(self.db, board_id)
        if not board:
            self.logger.error(f"Board with ID {board_id} not found for adding to favorites by user {user_id}")
            raise HTTPException(status_code=404, detail="Board not found")
        try:
            await crud_add_to_favorite_boards(self.db, user_id, board_id)
            send_email_task.delay(
                user_id,
                "Added to Favorites",
                f"You have added the board '{board.board_name}' to your favorites!"
            )
            self.logger.info(f"Board {board_id} added to favorites for user {user_id} successfully")
        except ValidationError as e:
            self.logger.error(f"Validation error occurred while adding board {board_id} to favorites for user {user_id}: {e}")
            raise HTTPException(status_code=422, detail="Invalid data for adding board to favorites")
        except Exception as e:
            self.logger.error(f"Error occurred while adding board {board_id} to favorites for user {user_id}: {e}")
            raise HTTPException(status_code=500, detail="Failed to add board to favorites")


    async def remove_from_favorite_boards(self, board_id: str, user_id: str):
        board = await get_board_by_id(self.db, board_id)
        if not board:
            self.logger.error(f"Board with ID {board_id} not found for removing from favorites by user {user_id}")
            raise HTTPException(status_code=404, detail="Board not found")
        try:
            await crud_remove_from_favorite_boards(self.db, user_id, board_id)
            send_email_task.delay(
                user_id,
                "Removed from Favorites",
                f"You have removed the board '{board.board_name}' from your favorites!"
            )
            self.logger.info(f"Board {board_id} removed from favorites for user {user_id} successfully")
        except ValidationError as e:
            self.logger.error(f"Validation error occurred while removing board {board_id} from favorites for user {user_id}: {e}")
            raise HTTPException(status_code=422, detail="Invalid data for removing board from favorites")
        except Exception as e:
            self.logger.error(f"Error occurred while removing board {board_id} from favorites for user {user_id}: {e}")
            raise HTTPException(status_code=500, detail="Failed to remove board from favorites")


    def _board_to_dict(self, board: Board, favorite_ids: set[str]) -> dict:
        return {
            "id": board.id,
            "board_name": board.board_name,
            "description": board.description,
            "owner_id": board.owner_id,
            "access": board.access,
            "created_at": board.created_at,
            "members": board.members,
            "is_favorite": board.id in favorite_ids,
            "ideas_count": len(board.ideas),
        }

    async def list_user_boards(self, user_id: str) -> list[dict]:
        boards = await get_user_boards(self.db, user_id)
        favorite_ids = await get_favorite_board_ids(self.db, user_id)
        return [self._board_to_dict(board, favorite_ids) for board in boards]

    async def get_board_detail(self, board_id: str, user_id: str) -> dict:
        board = await get_board_with_ideas(self.db, board_id)
        if not board:
            raise HTTPException(status_code=404, detail="Board not found")
        is_member = any(m.id == user_id for m in board.members)
        if not is_member and not board.access:
            raise HTTPException(status_code=403, detail="No access to this board")

        favorite_ids = await get_favorite_board_ids(self.db, user_id)
        data = self._board_to_dict(board, favorite_ids)
        data["ideas"] = [
            {
                "id": idea.id,
                "title": idea.title,
                "description": idea.description,
                "board_id": idea.board_id,
                "user_id": idea.user_id,
                "accepted": idea.accepted,
                "voting_ends_at": idea.voting_ends_at,
                "created_at": idea.created_at,
                "author": idea.user.username if idea.user else None,
                "approve": sum(1 for v in idea.votes if v.status),
                "reject": sum(1 for v in idea.votes if not v.status),
            }
            for idea in sorted(board.ideas, key=lambda i: i.created_at, reverse=True)
        ]
        return data
