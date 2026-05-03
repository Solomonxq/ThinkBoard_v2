from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.services.board_service import BoardService
from fastapi import HTTPException


@pytest.fixture
def mock_db():
    return AsyncMock()

@pytest.fixture
def board_service(mock_db):
    return BoardService(db=mock_db)

@pytest.mark.asyncio
async def test_add_to_favorite_success(board_service, mock_db):
    mock_board = MagicMock()
    mock_board.id = "board-123"

    mock_result = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.first.return_value = MagicMock(id="user-123")
    mock_result.scalars.return_value = mock_scalars
    mock_db.execute = AsyncMock(return_value=mock_result)

    with patch(
        "app.services.board_service.get_board_by_id",
        new=AsyncMock(return_value=mock_board)
    ), patch(
        "app.services.board_service.is_owner",
        new=AsyncMock(return_value=True)
    ), patch(
        "app.services.board_service.crud_add_to_favorite_boards",
        new=AsyncMock()
    ) as mock_add:

        await board_service.add_to_favorite_boards("board-123", "user-123")

        mock_add.assert_awaited_once()

@pytest.mark.asyncio
async def test_add_to_favorite_board_not_found(board_service):
    with patch(
        "app.services.board_service.get_board_by_id",
        new=AsyncMock(return_value=None)
    ):

        with pytest.raises(HTTPException) as exc_info:
            await board_service.add_to_favorite_boards("board-123", "user-123")

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Board not found"


@pytest.mark.asyncio
async def test_add_to_favorite_db_error(board_service, mock_db):
    mock_board = MagicMock()
    mock_board.id = "board-123"

    with patch(
        "app.services.board_service.get_board_by_id",
        new=AsyncMock(return_value=mock_board)
    ), patch(
        "app.services.board_service.is_owner",
        new=AsyncMock(return_value=True)
    ), patch(
        "app.services.board_service.crud_add_to_favorite_boards",
        new=AsyncMock(side_effect=Exception("DB error"))
    ):

        with pytest.raises(HTTPException) as exc_info:
            await board_service.add_to_favorite_boards("board-123", "user-123")

        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == "Failed to add board to favorites"
