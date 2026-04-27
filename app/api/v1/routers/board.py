from fastapi import APIRouter, Depends
from app.schemas.board import BoardCreate, BoardResponse, AddMemberRequest, BulkMemberRequest
from app.services.board_service import BoardService
from app.api.deps import get_board_service
from app.core.dependencies import get_current_user
from app.models.user import User

from app.api.v1.routers.idea import router as idea_router

router = APIRouter()


# -------------------------
# CREATE BOARD
# -------------------------
@router.post("/create", response_model=BoardResponse)
async def create_board_route(
    data: BoardCreate,
    service: BoardService = Depends(get_board_service),
    current_user: User = Depends(get_current_user),
):
    return await service.create_board(data, current_user.id)


# -------------------------
# DELETE BOARD
# -------------------------
@router.delete("/{board_id}", status_code=204)
async def delete_board_route(
    board_id: str,
    service: BoardService = Depends(get_board_service),
    current_user: User = Depends(get_current_user),
):
    return await service.delete_board(board_id, current_user.id)


# -------------------------
# ADD MEMBER
# -------------------------
@router.post("/{board_id}/members", status_code=200)
async def add_member_route(
    board_id: str,
    data: AddMemberRequest,
    service: BoardService = Depends(get_board_service),
    current_user: User = Depends(get_current_user),
):
    await service.add_user_to_board(
        board_id,
        data.user_id,
        current_user.id
    )
    return {"detail": "User added to board successfully"}


# -------------------------
# REMOVE MEMBER
# -------------------------
@router.delete("/{board_id}/members/{user_id}", status_code=200)
async def remove_member_route(
    board_id: str,
    user_id: str,
    service: BoardService = Depends(get_board_service),
    current_user: User = Depends(get_current_user),
):
    await service.delete_user_from_board(
        board_id,
        user_id,
        current_user.id
    )
    return {"detail": "User removed from board successfully"}


# -------------------------
# BULK ADD MEMBERS
# -------------------------
@router.post("/{board_id}/members/bulk", status_code=200)
async def add_members_route(
    board_id: str,
    data: BulkMemberRequest,
    service: BoardService = Depends(get_board_service),
    current_user: User = Depends(get_current_user),
):
    await service.add_users_to_board(
        board_id,
        data.user_ids,
        current_user.id
    )
    return {"detail": "Users added to board successfully"}


@router.delete("/{board_id}/members/bulk", status_code=200)
async def remove_members_bulk_route(
    board_id: str,
    data: BulkMemberRequest,
    service: BoardService = Depends(get_board_service),
    current_user: User = Depends(get_current_user),
):
    await service.delete_users_from_board(
        board_id,
        data.user_ids,
        current_user.id
    )
    return {"detail": "Users removed from board successfully"}

# -------------------------
# INCLUDE IDEAS ROUTER
# -------------------------
router.include_router(
    idea_router,
    prefix="/{board_id}/ideas",
    tags=["ideas"]
)