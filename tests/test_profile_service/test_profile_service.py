from io import BytesIO
import json
from unittest.mock import AsyncMock, MagicMock, patch, mock_open

import pytest
from app.schemas.user import UpdateProfileRequest
from app.services.profile_service import ProfileService
from fastapi import HTTPException, UploadFile
from PIL import Image


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
def profile_service(mock_db):
    return ProfileService(db=mock_db)


@pytest.mark.asyncio
async def test_update_profile_success(profile_service):
    mock_user = MagicMock()
    mock_user.id = "user-123"
    mock_user.username = "test-user"

    data = UpdateProfileRequest(bio="Updated bio")
    updated_user = MagicMock()

    mock_redis = MagicMock()
    mock_redis.delete = AsyncMock()

    with patch("app.services.profile_service.update_user_profile", new=AsyncMock(return_value=updated_user)) as mock_update, \
         patch("app.services.profile_service.get_redis", new=AsyncMock(return_value=mock_redis)):
        result = await profile_service.update_profile(mock_user, data)

    mock_update.assert_awaited_once_with(profile_service.db, mock_user, {"bio": "Updated bio"})
    mock_redis.delete.assert_any_await("profile:test-user")
    mock_redis.delete.assert_any_await("user:user-123")
    assert result is updated_user


@pytest.mark.asyncio
async def test_update_profile_no_data(profile_service):
    mock_user = MagicMock()
    data = UpdateProfileRequest()

    with pytest.raises(HTTPException) as exc_info:
        await profile_service.update_profile(mock_user, data)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "No data to update"


@pytest.mark.asyncio
async def test_upload_avatar_success(profile_service):
    mock_user = MagicMock()
    mock_user.id = "user-123"
    mock_user.username = "test-user"

    image_bytes = BytesIO()
    Image.new("RGB", (10, 10), color="blue").save(image_bytes, format="PNG")
    image_bytes = image_bytes.getvalue()

    mock_file = MagicMock(spec=UploadFile)
    mock_file.read = AsyncMock(return_value=image_bytes)

    updated_user = MagicMock()
    mock_redis = MagicMock()
    mock_redis.delete = AsyncMock()

    with patch("app.services.profile_service.open", mock_open()), \
         patch("app.services.profile_service.os.makedirs", return_value=None), \
         patch("app.services.profile_service.update_user_profile", new=AsyncMock(return_value=updated_user)) as mock_update, \
         patch("app.services.profile_service.get_redis", new=AsyncMock(return_value=mock_redis)):
        result = await profile_service.upload_avatar(mock_user, mock_file)

    mock_update.assert_awaited_once()
    mock_redis.delete.assert_any_await("profile:test-user")
    mock_redis.delete.assert_any_await("user:user-123")
    assert result is updated_user


@pytest.mark.asyncio
async def test_upload_avatar_too_large(profile_service):
    mock_file = MagicMock(spec=UploadFile)
    mock_file.read = AsyncMock(return_value=b"0" * (profile_service.max_size + 1))

    with pytest.raises(HTTPException) as exc_info:
        await profile_service.upload_avatar(MagicMock(), mock_file)

    assert exc_info.value.status_code == 400
    assert "File too large" in exc_info.value.detail


@pytest.mark.asyncio
async def test_upload_avatar_invalid_image(profile_service):
    mock_file = MagicMock(spec=UploadFile)
    mock_file.read = AsyncMock(return_value=b"not-an-image")

    with pytest.raises(HTTPException) as exc_info:
        await profile_service.upload_avatar(MagicMock(), mock_file)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Invalid image file"


@pytest.mark.asyncio
async def test_get_public_profile_cached(profile_service):
    cached_data = {"id": "user-123", "username": "test-user", "bio": "bio", "avatar_url": None, "boards": [], "member_of": []}
    mock_redis = MagicMock()
    mock_redis.get = AsyncMock(return_value=json.dumps(cached_data))

    with patch("app.services.profile_service.get_redis", new=AsyncMock(return_value=mock_redis)):
        result = await profile_service.get_public_profile("test-user")

    assert result == cached_data


@pytest.mark.asyncio
async def test_get_public_profile_cache_miss(profile_service, mock_db):
    mock_user = MagicMock()
    mock_user.id = "user-123"
    mock_user.username = "test-user"
    mock_user.bio = "Bio"
    mock_user.avatar_url = "/avatar.png"

    mock_board_owned = MagicMock()
    mock_board_owned.id = "board-1"
    mock_board_owned.board_name = "Owned Board"

    mock_board_member = MagicMock()
    mock_board_member.id = "board-2"
    mock_board_member.board_name = "Member Board"

    mock_result_user = MagicMock()
    mock_scalars_user = MagicMock()
    mock_scalars_user.first.return_value = mock_user
    mock_result_user.scalars.return_value = mock_scalars_user

    mock_result_owned = MagicMock()
    mock_scalars_owned = MagicMock()
    mock_scalars_owned.all.return_value = [mock_board_owned]
    mock_result_owned.scalars.return_value = mock_scalars_owned

    mock_result_member = MagicMock()
    mock_scalars_member = MagicMock()
    mock_scalars_member.all.return_value = [mock_board_member]
    mock_result_member.scalars.return_value = mock_scalars_member

    mock_db.execute = AsyncMock(
        side_effect=[mock_result_user, mock_result_owned, mock_result_member]
    )

    mock_redis = MagicMock()
    mock_redis.get = AsyncMock(return_value=None)
    mock_redis.setex = AsyncMock()

    with patch("app.services.profile_service.get_redis", new=AsyncMock(return_value=mock_redis)):
        result = await profile_service.get_public_profile("test-user")

    assert result["username"] == "test-user"
    assert result["bio"] == "Bio"
    assert result["avatar_url"] == "/avatar.png"
    assert result["boards"] == [{"id": "board-1", "board_name": "Owned Board"}]
    assert result["member_of"] == [{"id": "board-2", "board_name": "Member Board"}]

    mock_redis.setex.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_public_profile_not_found(profile_service):
    mock_result = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.first.return_value = None
    mock_result.scalars.return_value = mock_scalars

    profile_service.db.execute = AsyncMock(return_value=mock_result)

    mock_redis = MagicMock()
    mock_redis.get = AsyncMock(return_value=None)

    with patch("app.services.profile_service.get_redis", new=AsyncMock(return_value=mock_redis)):
        with pytest.raises(HTTPException) as exc_info:
            await profile_service.get_public_profile("not-found")

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "User not found"