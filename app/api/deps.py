from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.auth_service import AuthService
from app.services.board_service import BoardService
from app.services.profile_service import ProfileService
from app.services.oauth import OAuthService


async def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(db)


async def get_board_service(db: AsyncSession = Depends(get_db)) -> BoardService:
    return BoardService(db)


async def get_profile_service(db: AsyncSession = Depends(get_db)) -> ProfileService:
    return ProfileService(db)


async def get_oauth_service(db: AsyncSession = Depends(get_db)) -> OAuthService:
    return OAuthService(db)
