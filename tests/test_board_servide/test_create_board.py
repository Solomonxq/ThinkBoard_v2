from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.schemas.board import BoardCreate
from app.services.board_service import BoardService
from fastapi import HTTPException
from pydantic import ValidationError


@pytest.fixture
def mock_db():
    return AsyncMock()

@pytest.fixture
def board_service(mock_db):
    return BoardService(db=mock_db)

@pytest.mark.asyncio
async def test_create_board_success(board_service, mock_db):
    data = BoardCreate(
        board_name="Test Board",
        access=True,
        description="A board for testing"
    )
    mock_board = MagicMock()
    mock_board.board_name = data.board_name
    mock_board.owner_id = "user-123"
    mock_board.access = data.access
    mock_board.description = data.description

    mock_user = MagicMock()
    mock_user.email = "user@example.com"

    with patch(
        "app.services.board_service.get_user_by_id",
        new=AsyncMock(return_value=mock_user)
    ), patch(
        "app.services.board_service.crud_create_board",
        new=AsyncMock(return_value=mock_board)
    ) as mock_create:

        result = await board_service.create_board(data, "user-123")

        mock_create.assert_awaited_once_with(mock_db, data, "user-123")
        assert result.board_name == data.board_name
        assert result.owner_id == "user-123"
        assert result.access == data.access
        assert result.description == data.description

@pytest.mark.asyncio
async def test_create_board_failure(board_service, mock_db):
    data = BoardCreate(
        board_name="Test Board",
        access=True,
        description="A board for testing"
    )

    mock_user = MagicMock()
    mock_user.email = "user@example.com"

    with patch(
        "app.services.board_service.get_user_by_id",
        new=AsyncMock(return_value=mock_user)
    ), patch(
        "app.services.board_service.crud_create_board",
        new=AsyncMock(side_effect=Exception("DB error"))
    ) as mock_create:

        with pytest.raises(HTTPException) as exc_info:
            await board_service.create_board(data, "user-123")

        mock_create.assert_awaited_once_with(mock_db, data, "user-123")
        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == "Failed to create board"

@pytest.mark.asyncio
async def test_create_board_validation_error(board_service, mock_db):
    with pytest.raises(ValidationError):
        await board_service.create_board(
            BoardCreate(board_name="ab", access=True, description="desc"), "user-123"
        )
