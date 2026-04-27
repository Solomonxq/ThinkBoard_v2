from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.user import (
    UserCreate,
    UserResponse,
    UserLogin,
    TokenResponse,
    RefreshRequest,
    SetPasswordRequest,
    RegisterResponse
)

from app.services.auth_service import AuthService
from app.services.oauth import OAuthService
from app.api.deps import get_auth_service, get_oauth_service
from app.core.dependencies import get_current_user
from app.core.security import hash_password
from app.models.user import User

from app.core.limiter import limiter   # ✅ FIXED


router = APIRouter()


# -------------------------
# GOOGLE LOGIN
# -------------------------
@router.get("/google")
async def google_login(
    service: OAuthService = Depends(get_oauth_service)
):
    state = service.generate_state()
    auth_url = service.get_google_auth_url(state)

    response = RedirectResponse(url=auth_url)
    
    response.delete_cookie("oauth_state")  # ✅ видаляємо стару
    response.set_cookie(
        key="oauth_state",
        value=state,
        httponly=True,
        max_age=600,
        samesite="lax",
        secure=False,  # ✅ для локального HTTP
    )
    return response

# -------------------------
# GOOGLE CALLBACK
# -------------------------
@router.get("/google/callback")
async def google_callback(
    code: str,
    state: str,
    request: Request,
    service: OAuthService = Depends(get_oauth_service)
):
    stored_state = request.cookies.get("oauth_state")
    
    
    return await service.login_or_register(
        code=code,
        state=state,
        stored_state=stored_state
    )

# -------------------------
# REGISTER
# -------------------------
@router.post("/register", response_model=RegisterResponse)
@limiter.limit("3/minute")
async def register(
    request: Request,
    data: UserCreate,
    service: AuthService = Depends(get_auth_service)
):
    return await service.register_user(data)


# -------------------------
# LOGIN
# -------------------------
@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
async def login(
    request: Request,
    data: UserLogin,
    service: AuthService = Depends(get_auth_service)
):
    return await service.login_user(data)


# -------------------------
# REFRESH
# -------------------------
@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    data: RefreshRequest,
    service: AuthService = Depends(get_auth_service)
):
    return await service.refresh_tokens(data.refresh_token)


# -------------------------
# ME
# -------------------------
@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


# -------------------------
# SET PASSWORD
# -------------------------
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

    return {"message": "Password set successfully"}