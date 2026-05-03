import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.auth_service import AuthService
from app.schemas.user import UserLogin
from fastapi import HTTPException


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
def auth_service(mock_db):
    return AuthService(db=mock_db)


@pytest.mark.asyncio
async def test_login_access(auth_service, mock_db):
    login_data = UserLogin(
        email="asda@ads.com",
        password="sads"
    )

    mock_user = MagicMock()
    mock_user.id = 1
    mock_user.email = "asda@ads.com"
    mock_user.password = "hashed_password_in_db"
    mock_user.refresh_token = None

    with patch("app.services.auth_service.get_user_email", AsyncMock(return_value=mock_user)), \
         patch("app.services.auth_service.verify_password_async", AsyncMock(return_value=True)), \
         patch("app.services.auth_service.create_token", return_value="fake_access"), \
         patch("app.services.auth_service.create_refresh_token", return_value="fake_refresh"):

        result = await auth_service.login_user(login_data)

        assert result["access_token"] == "fake_access"
        assert result["token_type"] == "bearer"
        assert result["needs_password"] is False

        assert result["refresh_token"] == "fake_refresh"
        assert mock_user.refresh_token == "fake_refresh"

        mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_login_user_not_found(auth_service):
    login_data = UserLogin(
        email="asdas@adsas.com",
        password="asdasd"
    )

    with patch("app.services.auth_service.get_user_email", AsyncMock(return_value=None)):

        with pytest.raises(HTTPException) as ex:
            await auth_service.login_user(login_data)

        assert ex.value.status_code == 401
        assert ex.value.detail == "User not found"


@pytest.mark.asyncio
async def test_login_google(auth_service):
    login_data = UserLogin(
        email="asdas@adsas.com",
        password="asdasd"
    )

    mock_user = MagicMock()
    mock_user.password = None

    with patch("app.services.auth_service.get_user_email", AsyncMock(return_value=mock_user)):

        with pytest.raises(HTTPException) as ex:
            await auth_service.login_user(login_data)

        assert ex.value.status_code == 400
        assert ex.value.detail == "This account uses Google login"


@pytest.mark.asyncio
async def test_login_invalid_password(auth_service):
    login_data = UserLogin(
        email="aaa@aa.com",
        password="aaaaa"
    )

    mock_user = MagicMock()
    mock_user.password = "aaaa"

    with patch("app.services.auth_service.get_user_email", AsyncMock(return_value=mock_user)), \
         patch("app.services.auth_service.verify_password_async", AsyncMock(return_value=False)):

        with pytest.raises(HTTPException) as ex:
            await auth_service.login_user(login_data)

        assert ex.value.status_code == 401
        assert ex.value.detail == "Invalid password"