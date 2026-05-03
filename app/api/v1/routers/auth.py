from app.api.deps import get_auth_service, get_oauth_service
from app.core.dependencies import get_current_user
from app.core.limiter import limiter
from app.core.security import hash_password
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import (
    RefreshRequest,
    RegisterResponse,
    SetPasswordRequest,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
)
from app.services.auth_service import AuthService
from app.services.oauth import OAuthService
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.events.auth_event import  password_reset_event

router = APIRouter()

@router.get("/google")
async def google_login(
    service: OAuthService = Depends(get_oauth_service)
):
    state = service.generate_state()
    auth_url = service.get_google_auth_url(state)

    await service.store_state(state)
    return RedirectResponse(url=auth_url)


@router.get("/google/callback")
async def google_callback(
    code: str,
    state: str,
    service: OAuthService = Depends(get_oauth_service)
):
    return await service.login_or_register(
        code=code,
        state=state,
    )


@router.post("/register", response_model=RegisterResponse)
@limiter.limit("100/minute")
async def register(
    request: Request,
    data: UserCreate,
    service: AuthService = Depends(get_auth_service)
):
    return await service.register_user(data)



@router.post("/login", response_model=TokenResponse)
@limiter.limit("100/minute")
async def login(
    request: Request,
    data: UserLogin,
    service: AuthService = Depends(get_auth_service)
):
    return await service.login_user(data)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    data: RefreshRequest,
    service: AuthService = Depends(get_auth_service)
):
    return await service.refresh_tokens(data.refresh_token)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/set-password")
async def set_password(
    data: SetPasswordRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.password:
        raise HTTPException(status_code=400, detail="Password already set")

    current_user.password = hash_password(data.password)
    await db.commit()
    
    password_reset_event(current_user.email)

    return {"message": "Password set successfully"}
