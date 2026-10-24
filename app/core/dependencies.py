from app.core.security import decode_token
from app.crud.user import get_user_by_id
from app.db.session import get_db
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
import json
from app.core.redis import get_redis


bearer = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncSession = Depends(get_db)
):
    token = credentials.credentials
    payload = decode_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid token type")

    user_id = payload["sub"]
    redis = await get_redis()

    cached = await redis.get(f"user:{user_id}")
    if cached:
        data = json.loads(cached)
        return User(**data)

    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    await redis.setex(f"user:{user_id}", 300, json.dumps({
        "id": str(user.id),
        "email": user.email,
        "username": user.username,
        "is_active": user.is_active,
        "bio": user.bio,
        "avatar_url": user.avatar_url,
    }))

    return user