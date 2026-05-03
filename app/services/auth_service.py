from app.core.logging import setup_logging
from app.core.security import (
    create_refresh_token,
    create_token,
    decode_refresh_token,
    hash_password,
    hash_password_async,
    verify_password_async,
)
from app.crud.user import (
    create_user,
    get_user_by_id,
    get_user_by_username,
    get_user_email,
)
from app.schemas.user import UserCreate, UserLogin
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.events.auth_event import login_event, registration_event


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.logger = setup_logging()

    async def register_user(self, data: UserCreate) -> dict:
        if await get_user_email(self.db, data.email):
            self.logger.warning(f"Registration attempt with existing email: {data.email}")
            raise HTTPException(status_code=400, detail="Email already registered")
        if await get_user_by_username(self.db, data.username):
            self.logger.warning(f"Registration attempt with existing username: {data.username}")
            raise HTTPException(status_code=400, detail="Username already exists")

        user = await create_user(self.db, data)
        access_token = create_token({"sub": str(user.id), "email": user.email})
        refresh_token = create_refresh_token({"sub": str(user.id), "email": user.email})

        user.refresh_token = await hash_password_async(refresh_token)
        await self.db.commit()

        self.logger.info(f"User registered: {user.email}")
        registration_event(user.email)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "needs_password": True,
        }

    async def login_user(self, data: UserLogin) -> dict:
        user = await get_user_email(self.db, data.email)
        if not user:
            self.logger.warning(f"Login attempt for non-existent email: {data.email}")
            raise HTTPException(status_code=401, detail="User not found")

        if not user.password:
            raise HTTPException(
                status_code=400,
                detail="This account uses Google login"
            )

        if not await verify_password_async(data.password, user.password):
            self.logger.warning(f"Invalid password attempt for user: {user.email}")
            raise HTTPException(status_code=401, detail="Invalid password")

        access_token = create_token({"sub": str(user.id), "email": user.email})
        refresh_token = create_refresh_token({"sub": str(user.id), "email": user.email})

        user.refresh_token = refresh_token
        await self.db.commit()

        self.logger.info(f"User logged in: {user.email}")

        login_event(user.email)        

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "needs_password": False,
        }

    async def refresh_tokens(self, token: str) -> dict:
        payload = decode_refresh_token(token)
        if not payload:
            self.logger.warning("Invalid refresh token provided")
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        user = await get_user_by_id(self.db, payload["sub"])
        if not user or not user.refresh_token:
            self.logger.warning(f"Refresh token for non-existent or invalid user: {payload.get('sub')}")
            raise HTTPException(status_code=401, detail="User not found")

        if not await verify_password_async(token, user.refresh_token):
            self.logger.warning(f"Invalid refresh token verification for user: {user.id}")
            raise HTTPException(status_code=401, detail="Invalid password")

        access_token = create_token({"sub": str(user.id), "email": user.email})
        refresh_token = create_refresh_token({"sub": str(user.id), "email": user.email})

        user.refresh_token = await hash_password_async(refresh_token)
        await self.db.commit()

        self.logger.info(f"Tokens refreshed for user: {user.id}")


        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }