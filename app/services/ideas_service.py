import inspect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException

from app.core.logging import setup_logging
from app.crud.board import already_member_of_board
from app.crud.idea import (
    get_idea_by_id,
    create_idea as create_idea_crud,
    delete_idea as delete_idea_crud,
)
from app.models.board import Board
from app.tasks.email_tasks import send_email_task


class IdeaService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.logger = setup_logging()

    async def create_idea(self, data, user_id: str, board_id: str):
        await self._ensure_board_access(user_id, board_id)

        try:
            idea = await create_idea_crud(self.db, data, user_id, board_id)
        except Exception as e:
            if "uq_board_idea_title" in str(e):
                raise HTTPException(400, "Idea already exists")
            raise HTTPException(status_code=500, detail="Failed to create idea")

        result = await self.db.execute(
            select(Board)
            .options(selectinload(Board.members))
            .where(Board.id == board_id)
        )
        board = result.scalar_one_or_none()
        if inspect.isawaitable(board):
            board = await board

        self._notify_board_members(board, idea.title, board_id)

        return idea

    async def delete_idea(self, idea_id: str, user_id: str, board_id: str):
        idea = await self._get_and_validate_idea(idea_id, user_id, board_id)
        await delete_idea_crud(self.db, idea_id)
        return {"status": "deleted", "idea_id": idea.id}

    async def _ensure_board_access(self, user_id: str, board_id: str):
        has_access = await already_member_of_board(self.db, user_id, board_id)

        if not has_access:
            raise HTTPException(403, "Not a board member")

    async def _get_and_validate_idea(self, idea_id: str, user_id: str, board_id: str):
        idea = await get_idea_by_id(self.db, idea_id)

        if not idea:
            raise HTTPException(404, "Idea not found")

        if idea.board_id != board_id:
            raise HTTPException(status_code=404, detail="Idea not found in the specified board")

        if idea.user_id != user_id:
            raise HTTPException(status_code=403, detail="User is not the owner of the idea")

        return idea

    def _notify_board_members(self, board, idea_title: str, board_id: str):
        if not board:
            return

        for member in board.members:
            send_email_task.delay(
                member.email,
                "Idea Created",
                f"Idea '{idea_title}' created in board {board_id}"
            )