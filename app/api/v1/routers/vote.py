from app.db.session import get_db
from app.services.vote_service import VoteService
from fastapi import APIRouter, Depends, WebSocket
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.websocket("/{idea_id}/vote/ws")
async def vote_ws(
    websocket: WebSocket,
    idea_id: str,
    board_id: str,
    db: AsyncSession = Depends(get_db),
):
    service = VoteService(db)
    await service.ws_handler(websocket, idea_id, board_id)
