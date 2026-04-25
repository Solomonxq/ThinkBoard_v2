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
# SUCCESS ADD USERS TO BOARD
# -------------------------
@pytest.mark.asyncio
async def test_add_users_to_board_success(board_service, mock_db):
    mock_board = MagicMock()
    mock_board.id = "board-123"
    mock_board.owner_id = "user-123"

    mock_user = MagicMock()
    mock_user.id = "user-456"

    with patch(
        "app.services.board_service.get_board_by_id",
        new=AsyncMock(return_value=mock_board)
    ), patch(
        "app.services.board_service.get_user_by_id",
        new=AsyncMock(return_value=mock_user)
    ), patch(
        "app.services.board_service.crud_add_user_to_board",
        new=AsyncMock()
    ) as mock_add:

        await board_service.add_users_to_board(
            "board-123",
            ["user-456", "user-789"]
        )

        assert mock_add.await_count == 2

# -------------------------
# USER NOT FOUND
# -------------------------
@pytest.mark.asyncio
async def test_add_users_to_board_user_not_found(board_service):
    
    with patch(
        "app.services.board_service.get_user_by_id",
        new=AsyncMock(return_value=None)
    ):

        with pytest.raises(HTTPException) as exc:
            await board_service.add_users_to_board("board-123", ["user-456", "user-789"])

        assert exc.value.status_code == 404
        assert exc.value.detail == "User not found"