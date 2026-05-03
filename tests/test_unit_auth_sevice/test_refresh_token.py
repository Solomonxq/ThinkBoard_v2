import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException

from app.services.auth_service import AuthService


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
def auth_service(mock_db):
    return AuthService(db=mock_db)


@pytest.mark.asyncio
async def test_refresh_token_access(auth_service, mock_db):
    old_token = "old_token"
    payload = {"sub": "uuid-123"}

    mock_user = MagicMock()
    mock_user.id = "uuid-123"
    mock_user.refresh_token = "old_token"

    with patch("app.services.auth_service.decode_refresh_token", return_value=payload), \
         patch("app.services.auth_service.get_user_by_id", AsyncMock(return_value=mock_user)), \
         patch("app.services.auth_service.verify_password_async", AsyncMock(return_value=True)), \
         patch("app.services.auth_service.create_token", return_value="new_access"), \
         patch("app.services.auth_service.create_refresh_token", return_value="new_refresh"), \
         patch("app.core.security.hash_password_async", return_value="hashed_refresh"):

        result = await auth_service.refresh_tokens(old_token)

        assert result["access_token"] == "new_access"
        assert result["refresh_token"] == "new_refresh"
        assert mock_user.refresh_token != "old_token"

        mock_db.commit.assert_called_once()

@pytest.mark.asyncio
async def test_refresh_user_not_found(auth_service):
    old_token = "token"
    payload = {"sub": "uuid-123"}

    with patch("app.services.auth_service.decode_refresh_token", return_value=payload), \
         patch("app.services.auth_service.get_user_by_id", AsyncMock(return_value=None)):

        with pytest.raises(HTTPException) as ex:
            await auth_service.refresh_tokens(old_token)

        assert ex.value.status_code == 401
        assert ex.value.detail == "User not found"



@pytest.mark.asyncio
async def test_refresh_invalid_password(auth_service):
    old_token = "token"
    payload = {"sub": "uuid-123"}

    mock_user = MagicMock()
    mock_user.refresh_token = "wrong_token"

    with patch("app.services.auth_service.decode_refresh_token", return_value=payload), \
         patch("app.services.auth_service.get_user_by_id", AsyncMock(return_value=mock_user)), \
         patch("app.services.auth_service.verify_password_async", AsyncMock(return_value=False)):

        with pytest.raises(HTTPException) as ex:
            await auth_service.refresh_tokens(old_token)

        assert ex.value.status_code == 401
        assert ex.value.detail == "Invalid password"

@pytest.mark.asyncio
async def test_refresh_invalid_token(auth_service):
    invalid_token = "bad_token"

    with patch("app.services.auth_service.decode_refresh_token", return_value=None):

        with pytest.raises(HTTPException) as ex:
            await auth_service.refresh_tokens(invalid_token)

        assert ex.value.status_code == 401
        assert ex.value.detail == "Invalid refresh token"



@pytest.mark.asyncio
async def test_refresh_empty_payload(auth_service):
    old_token = "token"

    with patch("app.services.auth_service.decode_refresh_token", return_value={} ):

        with pytest.raises(HTTPException):
            await auth_service.refresh_tokens(old_token)