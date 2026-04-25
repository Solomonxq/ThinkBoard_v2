from sqlalchemy.ext.asyncio import AsyncSession
from app.core.logging import setup_logging
from app.crud.idea import( create_idea as create_idea_crud ,get_idea_by_title, user_member_of_board,
    delete_idea as delete_idea_crud, owner_of_idea,
    get_idea_by_id, check_idea_in_board)
from app.schemas.idea import IdeaCreate
from fastapi import HTTPException
from pydantic import ValidationError

class IdeaService:
    def __init__(self, db):
        self.db = db
        self.logger = setup_logging()

    async def create_idea(self, data, user_id: str, board_id: str):
        existing_idea = await get_idea_by_title(self.db, data.title, board_id)
        if existing_idea:
            raise HTTPException(status_code=400, detail="Idea with this title already exists in the board")

        member_chek = await user_member_of_board(self.db, user_id, board_id)
        if not member_chek:
            raise HTTPException(status_code=403, detail="User is not a member of the board")

        self.logger.info(
            f"Creating idea '{data.title}' for user {user_id} in board {board_id}"
        )
        try:
            return await create_idea_crud(self.db, data, user_id, board_id)
        except ValidationError as ve:
            self.logger.error(f"Validation error while creating idea: {ve}")
            raise HTTPException(status_code=422, detail=str(ve))    

    async def delete_idea(self, idea_id: str, user_id: str, board_id: str):
        idea = await get_idea_by_id(self.db, idea_id)
        if not idea:
            raise HTTPException(status_code=404, detail="Idea not found")
        if not await check_idea_in_board(self.db, idea_id, idea.board_id):
            raise HTTPException(status_code=404, detail="Idea not found in the specified board")
        if not await owner_of_idea(self.db, user_id, idea_id):
            raise HTTPException(status_code=403, detail="User is not the owner of the idea")
        await delete_idea_crud(self.db, idea_id)