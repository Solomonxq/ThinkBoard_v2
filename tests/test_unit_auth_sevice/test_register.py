import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.auth_service import AuthService
from app.schemas.user import UserCreate
from fastapi import HTTPException
from pydantic import ValidationError

@pytest.fixture
def mock_db():
    return AsyncMock()

@pytest.fixture
def auth_service(mock_db):
    return AuthService(db=mock_db)

@pytest.mark.asyncio
async def test_register_success(auth_service, mock_db):
    data = UserCreate(email="test@ex.com", username="asdasdasd", password="sad212312sad")
    

    with patch("app.services.auth_service.get_user_email", AsyncMock(return_value=None)), \
         patch("app.services.auth_service.get_user_by_username", AsyncMock(return_value=None)), \
         patch("app.services.auth_service.create_user", AsyncMock(return_value=MagicMock(id=1, email="test@ex.com"))):
        
        result = await auth_service.register_user(data)
        
        assert result["token_type"] == "bearer"

        mock_db.commit.assert_called_once()

@pytest.mark.asyncio
async def test_register_already_exists(auth_service, mock_db):
    data = UserCreate(email="exists@ex.com", username="sdasdas", password="asdasdasd21321")
    
    with patch("app.services.auth_service.get_user_email", AsyncMock(return_value=True)):
        with pytest.raises(HTTPException) as ex:
            await auth_service.register_user(data)
        
        assert ex.value.status_code == 400
        assert "Email already registered" in ex.value.detail


@pytest.mark.asyncio
async def test_register_short_password(auth_service,mock_db):
    with pytest.raises(ValidationError) as ex:
        UserCreate(
            email="eqdsasd@sad.com",
            username="sadasds",
            password="123"
        )

    assert "password" in str(ex.value)

@pytest.mark.asyncio
async def test_register_shord_username(auth_service,mock_db):
    with pytest.raises(ValidationError) as ex:
        UserCreate(
            email="eqdsasd@sad.com",
            username="ss",
            password="sadas"
        )

    assert "username" in str(ex.value)


@pytest.mark.asyncio
async def test_register_incorrect_email(auth_service,mock_db):
    with pytest.raises(ValidationError) as ex:
        UserCreate(
            email="ass",
            username="asdas",
            password="sadasdsad"
        )