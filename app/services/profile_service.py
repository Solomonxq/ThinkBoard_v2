import uuid
import os
from fastapi import HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.core.logging import setup_logging
from app.models.user import User
from app.crud.user import update_user_profile, get_user_by_username
from app.schemas.user import UpdateProfileRequest

UPLOAD_DIR = "/app/uploads/avatars"
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_SIZE = 5 * 1024 * 1024

os.makedirs(UPLOAD_DIR, exist_ok=True)


class ProfileService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.logger = setup_logging()
        self.upload_dir = UPLOAD_DIR
        self.allowed_types = ALLOWED_TYPES
        self.max_size = MAX_SIZE

    async def update_profile(self, user: User, data: UpdateProfileRequest) -> User:
        update_data = data.model_dump(exclude_none=True)
        if not update_data:
            raise HTTPException(status_code=400, detail="No data to update")
        self.logger.info(f"Updating profile for user {user.id}")
        return await update_user_profile(self.db, user, update_data)

    async def upload_avatar(self, user: User, file: UploadFile) -> User:
        if file.content_type not in self.allowed_types:
            raise HTTPException(status_code=400, detail="Only JPEG, PNG, WEBP allowed")

        contents = await file.read()
        if len(contents) > self.max_size:
            raise HTTPException(status_code=400, detail="File too large. Max 5MB")

        ext = file.filename.split(".")[-1]
        filename = f"{uuid.uuid4()}.{ext}"
        filepath = os.path.join(self.upload_dir, filename)

        with open(filepath, "wb") as f:
            f.write(contents)

        avatar_url = f"/uploads/avatars/{filename}"
        self.logger.info(f"Avatar uploaded for user {user.id}: {avatar_url}")
        return await update_user_profile(self.db, user, {"avatar_url": avatar_url})

    async def get_public_profile(self, username: str) -> dict:
        result = await self.db.execute(
            select(User)
            .options(
                selectinload(User.boards),
                selectinload(User.member_of)
            )
            .where(User.username == username)
        )
        user = result.scalars().first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return {
            "id": user.id,
            "username": user.username,
            "bio": user.bio,
            "avatar_url": user.avatar_url,
            "boards": [b for b in user.boards if b.access],
            "member_of": [b for b in user.member_of if b.access],
        }