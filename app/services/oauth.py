import httpx
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_token, create_refresh_token, hash_password
from app.core.logging import setup_logging
from app.crud.user import get_user_email
from app.models.user import User
from app.core.config import settings

GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"


class OAuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.logger = setup_logging()
        self.google_token_url = GOOGLE_TOKEN_URL
        self.google_userinfo_url = GOOGLE_USERINFO_URL

    def get_google_auth_url(self) -> str:
        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
        }
        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f"https://accounts.google.com/o/oauth2/v2/auth?{query}"

    async def exchange_code_for_token(self, code: str) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.post(self.google_token_url, data={
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            })
        
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to exchange code")
        
        return response.json()

    async def get_google_user_info(self, access_token: str) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.google_userinfo_url,
                headers={"Authorization": f"Bearer {access_token}"}
            )
        
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to fetch user info")
        
        return response.json()

    async def login_or_register(self, code: str) -> dict:
        token_data = await self.exchange_code_for_token(code)
        user_info = await self.get_google_user_info(token_data["access_token"])
        
        email = user_info.get("email").lower() 
        if not email:
            raise HTTPException(status_code=400, detail="Email not provided by Google")
        
        user = await get_user_email(self.db, email)
        if not user:
            user = User(
                email=email,
                username=user_info.get("name", email.split("@")[0]),
                password=None,
                oauth_provider="google",
                oauth_id=user_info.get("id"),
            )
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            self.logger.info(f"New OAuth user created: {email}")
        
        access_token = create_token({"sub": str(user.id), "email": user.email})
        refresh_token = create_refresh_token({"sub": str(user.id), "email": user.email})

        user.refresh_token = hash_password(refresh_token)
        await self.db.commit()
        self.logger.info(f"OAuth login successful: {email}")

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }