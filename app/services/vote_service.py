import asyncio

from app.core.logging import setup_logging
from app.core.redis import get_redis
from app.core.security import decode_token
from app.core.ws_manager import manager
from app.crud.board import alredy_member_of_board
from app.crud.idea import delete_idea, get_idea_by_id
from app.crud.vote import create_vote, get_vote, get_vote_counts, update_vote
from app.db.session import SessionLocal
from app.utils.time import utcnow
from fastapi import HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

TIMER_KEY = "voting_timer:{idea_id}"


class VoteService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.logger = setup_logging()

    async def _is_timer_active(self, idea_id: str) -> bool:
        redis = await get_redis()
        return bool(await redis.exists(TIMER_KEY.format(idea_id=idea_id)))

    async def _set_timer_active(self, idea_id: str, ttl_seconds: int):
        redis = await get_redis()
        await redis.set(
            TIMER_KEY.format(idea_id=idea_id),
            "1",
            ex=ttl_seconds + 10,
        )

    async def _clear_timer(self, idea_id: str):
        redis = await get_redis()
        await redis.delete(TIMER_KEY.format(idea_id=idea_id))

    async def connect(self, websocket: WebSocket, board_id: str):
        self.logger.info(f"[WS CONNECT] board={board_id}")
        await manager.connect(websocket, board_id)

    def disconnect(self, websocket: WebSocket, board_id: str):
        self.logger.info(f"[WS DISCONNECT] board={board_id}")
        manager.disconnect(websocket, board_id)

    async def broadcast(self, board_id: str, message: dict):
        self.logger.debug(f"[BROADCAST] board={board_id} msg={message}")
        await manager.broadcast(board_id, message)

    def authorize(self, token: str | None) -> str | None:
        self.logger.debug(f"[AUTH] token_present={bool(token)}")

        if not token:
            self.logger.warning("[AUTH FAILED] no token")
            return None

        payload = decode_token(token)
        if not payload:
            self.logger.warning("[AUTH FAILED] invalid token")
            return None

        user_id = payload.get("sub")
        self.logger.info(f"[AUTH OK] user={user_id}")
        return user_id

    async def get_init_state(self, idea_id: str) -> dict:
        self.logger.debug(f"[INIT STATE] idea_id={idea_id}")

        idea = await get_idea_by_id(self.db, idea_id)
        if not idea:
            self.logger.error(f"[INIT STATE ERROR] idea not found {idea_id}")
            raise HTTPException(status_code=404, detail="Idea not found")

        now = utcnow()

        if idea.voting_ends_at and idea.voting_ends_at <= now:
            self.logger.info(f"[INIT STATE] already finished idea={idea_id}")
            return {
                "event": "voting_already_finished",
                "accepted": idea.accepted,
            }

        counts = await get_vote_counts(self.db, idea_id)

        state = {
            "event": "init",
            "idea_id": idea_id,
            "seconds_left": (
                int((idea.voting_ends_at - now).total_seconds())
                if idea.voting_ends_at
                else None
            ),
            "approve": counts["approve"],
            "reject": counts["reject"],
        }

        self.logger.info(f"[INIT STATE READY] idea={idea_id} state={state}")
        return state

    async def vote(
        self,
        user_id: str,
        board_id: str,
        idea_id: str,
        status: bool,
    ) -> dict:
        self.logger.info(f"[VOTE] user={user_id} idea={idea_id} status={status}")

        if not await alredy_member_of_board(self.db, user_id, board_id):
            self.logger.warning(f"[VOTE DENIED] user={user_id} not in board={board_id}")
            raise HTTPException(status_code=403, detail="Not in board")

        idea = await get_idea_by_id(self.db, idea_id)
        if not idea:
            self.logger.error(f"[VOTE ERROR] idea not found {idea_id}")
            raise HTTPException(status_code=404, detail="Idea not found")

        if idea.voting_ends_at and utcnow() >= idea.voting_ends_at:
            self.logger.warning(f"[VOTE REJECTED] voting ended idea={idea_id}")
            raise HTTPException(status_code=400, detail="Voting ended")

        existing_vote = await get_vote(self.db, user_id, idea_id)

        try:
            if not existing_vote:
                self.logger.debug(f"[VOTE CREATE] user={user_id}")
                await create_vote(self.db, user_id, idea_id, status)
            elif existing_vote.status != status:
                self.logger.debug(f"[VOTE UPDATE] user={user_id}")
                await update_vote(self.db, user_id, idea_id, status)
            else:
                self.logger.debug(f"[VOTE SKIP] no change user={user_id}")
        except Exception:
            self.logger.exception("[VOTE FAILED]")
            raise HTTPException(status_code=500, detail="Vote error")

        counts = await get_vote_counts(self.db, idea_id)

        result = {
            "event": "vote_updated",
            "idea_id": idea_id,
            "approve": counts["approve"],
            "reject": counts["reject"],
        }

        self.logger.info(f"[VOTE RESULT] {result}")
        return result

    async def finalize_voting(self, db: AsyncSession, idea_id: str, board_id: str) -> dict:
        self.logger.info(f"[FINALIZE] idea={idea_id}")

        counts = await get_vote_counts(db, idea_id)
        idea = await get_idea_by_id(db, idea_id)

        if not idea:
            self.logger.error(f"[FINALIZE ERROR] idea not found {idea_id}")
            raise HTTPException(status_code=404, detail="Idea not found")

        accepted = counts["approve"] > counts["reject"]

        if accepted:
            idea.accepted = True
            await db.commit()
            self.logger.info(f"[FINALIZE] accepted idea={idea_id}")
        else:
            await delete_idea(db, idea_id)
            self.logger.info(f"[FINALIZE] deleted idea={idea_id}")

        result = {
            "event": "voting_finished",
            "idea_id": idea_id,
            "accepted": accepted,
            "approve": counts["approve"],
            "reject": counts["reject"],
        }

        self.logger.info(f"[FINALIZE RESULT] {result}")
        return result

    async def run_voting_timer(self, idea_id: str, board_id: str):
        self.logger.info(f"[TIMER START] idea={idea_id}")

        try:
            idea = await get_idea_by_id(self.db, idea_id)

            if not idea or not idea.voting_ends_at:
                self.logger.error(f"[TIMER STOP] idea not found {idea_id}")
                return

            wait = (idea.voting_ends_at - utcnow()).total_seconds()
            self.logger.info(f"[TIMER WAIT] {wait}s idea={idea_id}")

            if wait > 0:
                await asyncio.sleep(wait)

            async with SessionLocal() as db:
                idea = await get_idea_by_id(db, idea_id)
                if not idea:
                    self.logger.info(f"[TIMER SKIP] idea already gone {idea_id}")
                    return

                result = await self.finalize_voting(db, idea_id, board_id)

            await self.broadcast(board_id, result)

        except Exception:
            self.logger.exception(f"[TIMER FAILED] idea={idea_id}")

        finally:
            await self._clear_timer(idea_id)
            self.logger.info(f"[TIMER END] idea={idea_id}")

    async def ws_handler(
        self,
        websocket: WebSocket,
        idea_id: str,
        board_id: str,
    ):
        self.logger.info(f"[WS HANDLER START] idea={idea_id} board={board_id}")

        token = websocket.query_params.get("token")
        user_id = self.authorize(token)

        if not user_id:
            self.logger.warning("[WS CLOSE] unauthorized")
            await websocket.close(code=4001)
            return

        try:
            init_state = await self.get_init_state(idea_id)
        except Exception:
            self.logger.exception("[WS INIT FAILED]")
            await websocket.close(code=4004)
            return

        if init_state["event"] == "voting_already_finished":
            self.logger.info("[WS CLOSED] already finished")
            await websocket.send_json(init_state)
            await websocket.close()
            return

        await self.connect(websocket, board_id)
        await websocket.send_json(init_state)

        if not await self._is_timer_active(idea_id):
            seconds_left = init_state.get("seconds_left") or 0
            await self._set_timer_active(idea_id, ttl_seconds=seconds_left)
            self.logger.info(f"[TIMER CREATED] idea={idea_id}")
            asyncio.create_task(self.run_voting_timer(idea_id, board_id))

        try:
            while True:
                try:
                    data = await websocket.receive_json()
                except WebSocketDisconnect:
                    raise
                except Exception:
                    self.logger.warning("[INVALID JSON] cannot parse message")
                    await websocket.send_json({"error": "Invalid JSON"})
                    continue

                status = data.get("status")

                if not isinstance(status, bool):
                    self.logger.warning(f"[INVALID STATUS] {data}")
                    await websocket.send_json({"error": "Invalid status"})
                    continue

                result = await self.vote(
                    user_id=user_id,
                    board_id=board_id,
                    idea_id=idea_id,
                    status=status,
                )
                await self.broadcast(board_id, result)

        except WebSocketDisconnect:
            self.logger.info(f"[WS DISCONNECT EVENT] idea={idea_id}")
            self.disconnect(websocket, board_id)