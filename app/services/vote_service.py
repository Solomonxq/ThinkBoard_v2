from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException , status

from app.core.logging import setup_logging

from app.models.vote import Vote
from app.schemas.vote import VoteCreate
from app.utils.time import utcnow
from app.crud.vote import get_vote, create_vote, update_vote,check_status
from app.crud.idea import user_member_of_board
from pydantic import ValidationError
class VoteService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.logger = setup_logging()

    async def vote(self, user_id: str, board_id: str, idea_id: str, status: bool):

        if not await user_member_of_board(self.db, user_id, board_id):
            self.logger.error(f"User:{user_id} not in board:{board_id}")
            raise HTTPException(status_code=403, detail="User not in board")

        existing_vote = await get_vote(self.db, user_id, idea_id)


        if not existing_vote:
            try:
                self.logger.info(f"User:{user_id} vote in board:{board_id}")
                return await create_vote(self.db, user_id, idea_id, status)
            except Exception:
                await self.db.rollback()
                self.logger.exception("Create vote failed")
                raise HTTPException(status_code=500, detail="Internal server error")


        if existing_vote.status == status:
            return existing_vote 


        try:
            return await update_vote(self.db, user_id, idea_id, status)
        except Exception:
            await self.db.rollback()
            self.logger.exception("Update vote failed")
            raise HTTPException(status_code=500, detail="Internal server error")