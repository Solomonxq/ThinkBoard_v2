from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.board import BoardCreate, BoardResponse, AddMemberRequest, BulkMemberRequest
from app.services.board_service import BoardService
from app.api.deps import get_board_service
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import UserResponse
from app.api.v1.routers.idea import router as pidea_router

router = APIRouter()

@router.post('/create', response_model=BoardResponse)
async def create_board_route(
    data: BoardCreate,
    service: BoardService = Depends(get_board_service),
    current_user: User = Depends(get_current_user)
):
    return await service.create_board(data, current_user.id)

@router.post('/{board_id}/members/bulk-add', response_model=BoardResponse)
async def bulk_add_members_route(
    board_id: str,
    data: BulkMemberRequest,
    service: BoardService = Depends(get_board_service),
    current_user: User = Depends(get_current_user)
):
    return await service.bulk_add_members(board_id, data.user_ids, current_user.id)

@router.delete('/{board_id}/members/bulk-remove', response_model=BoardResponse)
async def bulk_remove_members_route(
    board_id: str,
    data: BulkMemberRequest,
    service: BoardService = Depends(get_board_service),
    current_user: User = Depends(get_current_user)
):
    return await service.bulk_remove_members(board_id, data.user_ids, current_user.id)

@router.post('/{board_id}/members', response_model=BoardResponse)
async def add_member_route(
    board_id: str,
    data: AddMemberRequest,
    service: BoardService = Depends(get_board_service),
    current_user: User = Depends(get_current_user)
):
    return await service.add_member(board_id, data.user_id, current_user.id)

@router.delete('/{board_id}/members/{user_id}', response_model=BoardResponse)
async def remove_member_route(
    board_id: str,
    user_id: str,
    service: BoardService = Depends(get_board_service),
    current_user: User = Depends(get_current_user)
):
    return await service.remove_member(board_id, user_id, current_user.id)


@router.post('/{board_id}/favorite', response_model=UserResponse)
async def add_favorite(
    board_id: str,
    service: BoardService = Depends(get_board_service),
    current_user: User = Depends(get_current_user)
):
    return await service.add_to_favorites(board_id, current_user)

@router.delete('/{board_id}/favorite', response_model=UserResponse)
async def remove_favorite(
    board_id: str,
    service: BoardService = Depends(get_board_service),
    current_user: User = Depends(get_current_user)
):
    return await service.remove_from_favorites(board_id, current_user)

router.include_router(
    pidea_router,
    prefix='/{board_id}/ideas',
    tags=['ideas']
)