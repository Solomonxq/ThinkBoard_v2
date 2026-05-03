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
async def test_delete_user_from_board_success(board_service, mock_db):
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
        "app.services.board_service.get_user_by_id",
        new=AsyncMock(return_value=MagicMock())
    ), patch(
        "app.services.board_service.crud_delete_user_from_board",
        new=AsyncMock()
    ) as mock_delete:

        await board_service.delete_user_from_board("board-123", "user-456", "user-123")

        mock_delete.assert_awaited_once_with(
            mock_db,
            mock_board,
            "user-456"
        )


@pytest.mark.asyncio
async def test_delete_user_from_board_user_not_found(board_service):
    with patch(
        "app.services.board_service.is_owner",
        new=AsyncMock(return_value=True)
    ), patch(
        "app.services.board_service.get_user_by_id",
        new=AsyncMock(return_value=None)
    ), patch(
        "app.services.board_service.get_board_by_id",
        new=AsyncMock(return_value=MagicMock(id="board-123"))
    ):

        with pytest.raises(HTTPException) as exc:
            await board_service.delete_user_from_board(
                "board-123",
                "user-456",
                "user-123"
            )

        assert exc.value.status_code == 404
        assert exc.value.detail == "User not found"


@pytest.mark.asyncio
async def test_delete_user_from_board_not_owner(board_service):
    with patch(
        "app.services.board_service.is_owner",
        new=AsyncMock(return_value=False)
    ), patch(
        "app.services.board_service.get_board_by_id",
        new=AsyncMock(return_value=MagicMock(id="board-123"))
    ):

        with pytest.raises(HTTPException) as exc:
            await board_service.delete_user_from_board(
                "board-123",
                "user-456",
                "user-789"
            )

        assert exc.value.status_code == 403
        assert exc.value.detail == "Only owner can remove users from the board"


@pytest.mark.asyncio
async def test_delete_user_from_board_db_error(board_service, mock_db):
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
        "app.services.board_service.get_user_by_id",
        new=AsyncMock(return_value=MagicMock())
    ), patch(
        "app.services.board_service.crud_delete_user_from_board",
        new=AsyncMock(side_effect=Exception("DB error"))
    ) as mock_delete:

        with pytest.raises(HTTPException) as exc:
            await board_service.delete_user_from_board(
                "board-123",
                "user-456",
                "user-123"
            )

        assert exc.value.status_code == 500
        assert exc.value.detail == "Failed to remove user from board"
        mock_delete.assert_awaited_once_with(
            mock_db,
            mock_board,
            "user-456"
        )
