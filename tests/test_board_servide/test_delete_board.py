import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException
from pydantic import ValidationError
from app.services.board_service import BoardService


# -------------------------
# FIXTURES
# -------------------------
@pytest.fixture
def mock_db():
    return AsyncMock()

@pytest.fixture
def board_service(mock_db):
    return BoardService(db=mock_db)

# -------------------------
# SUCCESS DELETE
# -------------------------
@pytest.mark.asyncio
async def test_delete_board_success(board_service, mock_db):
    mock_board = MagicMock()
    mock_board.id = "board-123"
    mock_board.owner_id = "user-123"

    with patch(
        "app.services.board_service.get_board_by_id",
        new=AsyncMock(return_value=mock_board)
    ), patch(
        "app.services.board_service.is_owner",
        new=AsyncMock(return_value=True)
    ), patch(
        "app.services.board_service.crud_delete_board",
        new=AsyncMock()
    ) as mock_delete:

        await board_service.delete_board("board-123", "user-123")

        mock_delete.assert_awaited_once_with(mock_db, "board-123")

# -------------------------
# BOARD NOT FOUND
# -------------------------
@pytest.mark.asyncio
async def test_delete_board_not_found(board_service):
    with patch(
        "app.services.board_service.get_board_by_id",
        new=AsyncMock(return_value=None)
    ):

        with pytest.raises(HTTPException) as exc_info:
            await board_service.delete_board("board-123", "user-123")

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Board not found"

# -------------------------
# NOT OWNER
# -------------------------
@pytest.mark.asyncio
async def test_delete_board_not_owner(board_service, mock_db):
    mock_board = MagicMock()
    mock_board.id = "board-123"
    mock_board.owner_id = "user-123"

    with patch(
        "app.services.board_service.get_board_by_id",
        new=AsyncMock(return_value=mock_board)
    ), patch(
        "app.services.board_service.is_owner",
        new=AsyncMock(return_value=False)
    ):

        with pytest.raises(HTTPException) as exc_info:
            await board_service.delete_board("board-123", "user-456")

        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "Only owner can delete the board"


# -------------------------
# DELETE FAILURE
# -------------------------
@pytest.mark.asyncio
async def test_delete_board_failure(board_service, mock_db):
    mock_board = MagicMock()
    mock_board.id = "board-123"
    mock_board.owner_id = "user-123"

    with patch(
        "app.services.board_service.get_board_by_id",
        new=AsyncMock(return_value=mock_board)
    ), patch(
        "app.services.board_service.is_owner",
        new=AsyncMock(return_value=True)
    ), patch(
        "app.services.board_service.crud_delete_board",
        new=AsyncMock(side_effect=Exception("DB error"))
    ) as mock_delete:

        with pytest.raises(HTTPException) as exc_info:
            await board_service.delete_board("board-123", "user-123")

        mock_delete.assert_awaited_once_with(mock_db, "board-123")
        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == "Failed to delete board"




