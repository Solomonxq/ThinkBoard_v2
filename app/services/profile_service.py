import io
import json
import os
import uuid

from app.core.logging import setup_logging
from app.core.redis import get_redis
from app.crud.user import delete_user, get_user_by_id, update_user_profile
from app.events.profile_event import delete_account_event
from app.models.associations import board_members
from app.models.board import Board
from app.models.user import User
from app.schemas.user import UpdateProfileRequest
from fastapi import HTTPException, UploadFile
from PIL import Image
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads/avatars")
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_SIZE = 5 * 1024 * 1024


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
            self.logger.warning(f"No data provided for profile update by user {user.id}")
            raise HTTPException(status_code=400, detail="No data to update")

        self.logger.info(f"Updating profile for user {user.id}")
        # current_user may come from the Redis cache (detached object), so load the persisted one
        old_username = user.username
        user = await get_user_by_id(self.db, user.id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        updated = await update_user_profile(self.db, user, update_data)
        await (await get_redis()).delete(f"profile:{old_username}")

        redis = await get_redis()
        await redis.delete(f"profile:{user.username}")
        await redis.delete(f"user:{user.id}")

        return updated

    async def upload_avatar(self, user: User, file: UploadFile) -> User:
        contents = await file.read()

        if len(contents) > self.max_size:
            self.logger.warning(f"File too large uploaded by user {user.id}: {len(contents)} bytes")
            raise HTTPException(status_code=400, detail="File too large. Max 5MB")

        os.makedirs(self.upload_dir, exist_ok=True)

        try:
            image = Image.open(io.BytesIO(contents))
            image.verify()
            format = image.format.upper()
        except Exception:
            self.logger.warning(f"Invalid image file uploaded by user {user.id}")
            raise HTTPException(status_code=400, detail="Invalid image file")

        allowed_formats = {"JPEG", "PNG", "WEBP"}
        if format not in allowed_formats:
            self.logger.warning(f"Unsupported image format uploaded by user {user.id}: {format}")
            raise HTTPException(
                status_code=400,
                detail="Only JPEG, PNG, WEBP allowed"
            )

        ext_map = {"JPEG": "jpg", "PNG": "png", "WEBP": "webp"}
        ext = ext_map[format]
        filename = f"{uuid.uuid4()}.{ext}"
        filepath = os.path.join(self.upload_dir, filename)

        with open(filepath, "wb") as f:
            f.write(contents)

        avatar_url = f"/uploads/avatars/{filename}"
        self.logger.info(f"Avatar uploaded for user {user.id}: {avatar_url}")

        persisted_user = await get_user_by_id(self.db, user.id)
        if not persisted_user:
            raise HTTPException(status_code=404, detail="User not found")
        updated = await update_user_profile(
            self.db,
            persisted_user,
            {"avatar_url": avatar_url}
        )

        redis = await get_redis()
        await redis.delete(f"profile:{user.username}")
        await redis.delete(f"user:{user.id}")

        return updated

    async def get_public_profile(self, username: str) -> dict:
        redis = await get_redis()
        cache_key = f"profile:{username}"

        cached = await redis.get(cache_key)
        if cached:
            return json.loads(cached)

        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        user = result.scalars().first()
        if not user:
            self.logger.warning(f"Public profile requested for non-existent user: {username}")
            raise HTTPException(status_code=404, detail="User not found")

        owned = await self.db.execute(
            select(Board).where(
                Board.owner_id == user.id,
                Board.access == True,
            )
        )
        member_of = await self.db.execute(
            select(Board)
            .join(board_members, Board.id == board_members.c.board_id)
            .where(
                board_members.c.user_id == user.id,
                Board.access == True,
            )
        )

        owned_boards = owned.scalars().all()
        member_boards = member_of.scalars().all()

        data = {
            "id": str(user.id),
            "username": user.username,
            "bio": user.bio,
            "avatar_url": user.avatar_url,
            "boards": [{"id": b.id, "board_name": b.board_name} for b in owned_boards],
            "member_of": [{"id": b.id, "board_name": b.board_name} for b in member_boards],
        }


        await redis.setex(cache_key, 120, json.dumps(data))
        return data

    async def delete_account(self, user: User) -> None:
        self.logger.info(f"Deleting profile for user {user.id}")

        persisted_user = await get_user_by_id(self.db, user.id)
        if not persisted_user:
            self.logger.warning(f"Attempt to delete non-existent user: {user.id}")
            raise HTTPException(status_code=404, detail="User not found")

        if persisted_user.avatar_url:
            avatar_path = os.path.join(
                self.upload_dir,
                os.path.basename(persisted_user.avatar_url)
            )
            if os.path.exists(avatar_path):
                try:
                    os.remove(avatar_path)
                except OSError:
                    self.logger.warning(f"Failed to remove avatar file: {avatar_path}")

        await self.db.execute(
            board_members.delete().where(board_members.c.user_id == persisted_user.id)
        )

        await delete_user(self.db, persisted_user)

        redis = await get_redis()
        await redis.delete(f"profile:{persisted_user.username}")
        await redis.delete(f"user:{persisted_user.id}")

        delete_account_event(persisted_user.email)