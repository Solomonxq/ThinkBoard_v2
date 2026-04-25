import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException
from app.services.board_service import BoardService


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
def board_service(mock_db):
    return BoardService(db=mock_db)


# -------------------------
# SUCCESS
# -------------------------
@pytest.mark.asyncio
async def test_add_user_to_board_success(board_service, mock_db):
    mock_board = MagicMock()
    mock_user = MagicMock()

    with patch(
        "app.services.board_service.get_user_by_id",
        new=AsyncMock(return_value=mock_user)
    ), patch(
        "app.services.board_service.get_board_by_id",
        new=AsyncMock(return_value=mock_board)
    ), patch(
        "app.services.board_service.crud_add_user_to_board",
        new=AsyncMock()
    ) as mock_add:

        await board_service.add_user_to_board("board-123", "user-456")

        mock_add.assert_awaited_once_with(
            mock_db,
            "board-123",
            "user-456"
        )


# -------------------------
# USER NOT FOUND
# -------------------------
@pytest.mark.asyncio
async def test_add_user_to_board_user_not_found(board_service):

    with patch(
        "app.services.board_service.get_user_by_id",
        new=AsyncMock(return_value=None)
    ):

        with pytest.raises(HTTPException) as exc:
            await board_service.add_user_to_board("board-123", "user-456")

        assert exc.value.status_code == 404
        assert exc.value.detail == "User not found"


# -------------------------
# BOARD NOT FOUND
# -------------------------
@pytest.mark.asyncio
async def test_add_user_to_board_board_not_found(board_service):

    with patch(
        "app.services.board_service.get_user_by_id",
        new=AsyncMock(return_value=MagicMock())
    ), patch(
        "app.services.board_service.get_board_by_id",
        new=AsyncMock(return_value=None)
    ):

        with pytest.raises(HTTPException) as exc:
            await board_service.add_user_to_board("board-123", "user-456")

        assert exc.value.status_code == 404
        assert exc.value.detail == "Board not found"


# -------------------------
# DB ERROR
# -------------------------
@pytest.mark.asyncio
async def test_add_user_to_board_failure(board_service, mock_db):

    with patch(
        "app.services.board_service.get_user_by_id",
        new=AsyncMock(return_value=MagicMock())
    ), patch(
        "app.services.board_service.get_board_by_id",
        new=AsyncMock(return_value=MagicMock())
    ), patch(
        "app.services.board_service.crud_add_user_to_board",
        new=AsyncMock(side_effect=Exception("DB error"))
    ):

        with pytest.raises(HTTPException) as exc:
            await board_service.add_user_to_board("board-123", "user-456")

        assert exc.value.status_code == 500
        assert exc.value.detail == "Failed to add user to board"