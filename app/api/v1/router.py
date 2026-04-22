from fastapi import APIRouter
from app.api.v1.routers.auth import router as auth_router
from app.api.v1.routers.board import router as board_router
from app.api.v1.routers.profile import router as profile_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
api_router.include_router(board_router, prefix="/boards", tags=["Boards"])

api_router.include_router(profile_router, prefix="/profile", tags=["Profile"])