import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import WebSocket, HTTPException

from app.core.redis import get_redis
from app.core.security import decode_token
from app.core.ws_manager import manager

from app.crud.idea import get_idea_by_id, delete_idea
from app.crud.vote import create_vote, get_vote, update_vote, get_vote_counts
from app.crud.board import already_member_of_board

from app.db.session import SessionLocal
from app.utils.time import utcnow
from app.models.board import Board
from app.events.voting_events import notify_voting_finished


TIMER_KEY = "voting_timer:{idea_id}"


class VoteService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def connect(self, websocket: WebSocket, board_id: str):
        await manager.connect(websocket, board_id)

    def disconnect(self, websocket: WebSocket, board_id: str):
        manager.disconnect(websocket, board_id)

    async def broadcast(self, board_id: str, message: dict):
        await manager.broadcast(board_id, message)

    def authorize(self, token: str | None) -> str | None:
        if not token:
            return None
        payload = decode_token(token)
        return payload.get("sub") if payload else None

    async def _set_timer(self, idea_id: str, ttl: int):
        redis = await get_redis()
        await redis.set(TIMER_KEY.format(idea_id=idea_id), "1", ex=ttl + 10)

    async def _clear_timer(self, idea_id: str):
        redis = await get_redis()
        await redis.delete(TIMER_KEY.format(idea_id=idea_id))

    async def _timer_exists(self, idea_id: str) -> bool:
        redis = await get_redis()
        return bool(await redis.exists(TIMER_KEY.format(idea_id=idea_id)))

    async def get_init_state(self, idea_id: str):
        idea = await get_idea_by_id(self.db, idea_id)
        if not idea:
            raise HTTPException(404, "Idea not found")

        now = utcnow()

        if idea.voting_ends_at and idea.voting_ends_at <= now:
            return {
                "event": "voting_already_finished",
                "accepted": idea.accepted,
            }

        counts = await get_vote_counts(self.db, idea_id)

        return {
            "event": "init",
            "idea_id": idea_id,
            "seconds_left": int((idea.voting_ends_at - now).total_seconds())
            if idea.voting_ends_at else None,
            "approve": counts["approve"],
            "reject": counts["reject"],
        }

    async def vote(self, user_id: str, board_id: str, idea_id: str, status: bool):
        if not await already_member_of_board(self.db, user_id, board_id):
            raise HTTPException(403, "Not in board")

        idea = await get_idea_by_id(self.db, idea_id)
        if not idea:
            raise HTTPException(404, "Idea not found")

        if idea.voting_ends_at and utcnow() >= idea.voting_ends_at:
            raise HTTPException(400, "Voting ended")

        vote = await get_vote(self.db, user_id, idea_id)

        if not vote:
            await create_vote(self.db, user_id, idea_id, status)
        elif vote.status != status:
            await update_vote(self.db, user_id, idea_id, status)

        counts = await get_vote_counts(self.db, idea_id)

        return {
            "event": "vote_updated",
            "idea_id": idea_id,
            "approve": counts["approve"],
            "reject": counts["reject"],
        }

    async def finalize_voting(self, db: AsyncSession, idea_id: str, board_id: str):
        idea = await get_idea_by_id(db, idea_id)
        if not idea:
            raise HTTPException(404, "Idea not found")

        counts = await get_vote_counts(db, idea_id)

        accepted = counts["approve"] > counts["reject"]

        if accepted:
            idea.accepted = True
            await db.commit()
        else:
            await delete_idea(db, idea_id)

        board = (await db.execute(
            select(Board).where(Board.id == board_id)
        )).scalar_one_or_none()

        if board:
            await notify_voting_finished(
                board_id=board_id,
                board_name=board.board_name,
                idea_id=idea_id,
                result={
                    "accepted": accepted,
                    "approve": counts["approve"],
                    "reject": counts["reject"],
                },
            )

        return {
            "event": "voting_finished",
            "idea_id": idea_id,
            "accepted": accepted,
            "approve": counts["approve"],
            "reject": counts["reject"],
        }

    async def run_voting_timer(self, idea_id: str, board_id: str):
        try:
            idea = await get_idea_by_id(self.db, idea_id)
            if not idea:
                return

            wait = (idea.voting_ends_at - utcnow()).total_seconds()

            if wait > 0:
                await asyncio.sleep(wait)

            async with SessionLocal() as db:
                result = await self.finalize_voting(db, idea_id, board_id)

            await self.broadcast(board_id, result)

        finally:
            await self._clear_timer(idea_id)

    async def ws_handler(self, websocket: WebSocket, idea_id: str, board_id: str):
        token = websocket.query_params.get("token")
        user_id = self.authorize(token)

        if not user_id:
            await websocket.close(4001)
            return

        state = await self.get_init_state(idea_id)

        await self.connect(websocket, board_id)
        await websocket.send_json(state)

        if not await self._timer_exists(idea_id):
            await self._set_timer(idea_id, state.get("seconds_left") or 0)
            asyncio.create_task(self.run_voting_timer(idea_id, board_id))

        try:
            while True:
                data = await websocket.receive_json()

                result = await self.vote(
                    user_id=user_id,
                    board_id=board_id,
                    idea_id=idea_id,
                    status=data.get("status"),
                )

                await self.broadcast(board_id, result)

        except Exception:
            self.disconnect(websocket, board_id)