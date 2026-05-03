from app.core.logging import setup_logging
from app.crud.board import already_member_of_board
from app.crud.idea import get_idea_by_id
from app.crud.idea import create_idea as create_idea_crud
from app.crud.idea import delete_idea as delete_idea_crud
from app.schemas.idea import IdeaCreate
from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession


class IdeaService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.logger = setup_logging()

    async def create_idea(self, data: IdeaCreate, user_id: str, board_id: str):
        if not await already_member_of_board(self.db, user_id, board_id):
            self.logger.error(f"User {user_id} is not a member of board {board_id}")
            raise HTTPException(status_code=403, detail="User is not a member of the board")

        self.logger.info(f"Creating idea '{data.title}' for user {user_id} in board {board_id}")

        try:
            return await create_idea_crud(self.db, data, user_id, board_id)
        except ValidationError as ve:
            self.logger.error(f"Validation error while creating idea: {ve}")
            raise HTTPException(status_code=422, detail=str(ve))
        except Exception as e:
            if "uq_board_idea_title" in str(e):
                self.logger.error(f"Idea '{data.title}' already exists in board {board_id}")
                raise HTTPException(status_code=400, detail="Idea with this title already exists in the board")
            self.logger.error(f"Error while creating idea '{data.title}': {e}")
            raise HTTPException(status_code=500, detail="Failed to create idea")

    async def delete_idea(self, idea_id: str, user_id: str, board_id: str):
        idea = await get_idea_by_id(self.db, idea_id)

        if not idea:
            self.logger.error(f"Idea {idea_id} not found")
            raise HTTPException(status_code=404, detail="Idea not found")

        if idea.board_id != board_id:
            self.logger.error(f"Idea {idea_id} not in board {board_id}")
            raise HTTPException(status_code=404, detail="Idea not found in the specified board")

        if idea.user_id != user_id:
            self.logger.error(f"User {user_id} is not owner of idea {idea_id}")
            raise HTTPException(status_code=403, detail="User is not the owner of the idea")

        self.logger.info(f"Deleting idea {idea_id} by user {user_id} from board {board_id}")
        await delete_idea_crud(self.db, idea_id)