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
            await board_service.add_user_to_board(
                board_id="board-123",
                user_id="user-456",
                current_id="owner-123"
            )

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
        "app.services.board_service.is_owner",
        new=AsyncMock(return_value=True)
    ), patch(
        "app.services.board_service.get_board_by_id",
        new=AsyncMock(return_value=None)
    ):

        with pytest.raises(HTTPException) as exc:
            await board_service.add_user_to_board(
                board_id="board-123",
                user_id="user-456",
                current_id="owner-123"
            )

        assert exc.value.status_code == 404
        assert exc.value.detail == "Board not found"

# -------------------------
# NOT OWNER
# -------------------------
@pytest.mark.asyncio
async def test_add_user_to_board_not_owner(board_service):

    with patch(
        "app.services.board_service.get_user_by_id",
        new=AsyncMock(return_value=MagicMock())
    ), patch(
        "app.services.board_service.get_board_by_id",
        new=AsyncMock(return_value=MagicMock())
    ), patch(
        "app.services.board_service.is_owner",
        new=AsyncMock(return_value=False)
    ):

        with pytest.raises(HTTPException) as exc:
            await board_service.add_user_to_board(
                board_id="board-123",
                user_id="user-456",
                current_id="owner-123"
            )

        assert exc.value.status_code == 403
# -------------------------
# USER ALREADY MEMBER
# -------------------------
@pytest.mark.asyncio
async def test_add_user_to_board_already_member(board_service):

    with patch(
        "app.services.board_service.get_user_by_id",
        new=AsyncMock(return_value=MagicMock())
    ), patch(
        "app.services.board_service.get_board_by_id",
        new=AsyncMock(return_value=MagicMock())
    ), patch(
        "app.services.board_service.is_owner",
        new=AsyncMock(return_value=True)
    ), patch(
        "app.services.board_service.crud_alredy_member_of_board",
        new=AsyncMock(return_value=True)
    ):

        with pytest.raises(HTTPException) as exc:
            await board_service.add_user_to_board(
                board_id="board-123",
                user_id="user-456",
                current_id="owner-123"
            )

        assert exc.value.status_code == 400
        assert exc.value.detail == "User is already a member of the board"


# -------------------------
# SUCCESS DB ERROR
# -------------------------
@pytest.mark.asyncio
async def test_add_user_to_board_db_error(board_service):

    mock_user = MagicMock()
    mock_board = MagicMock()

    with patch(
        "app.services.board_service.get_user_by_id",
        new=AsyncMock(return_value=mock_user)
    ), patch(
        "app.services.board_service.get_board_by_id",
        new=AsyncMock(return_value=mock_board)
    ), patch(
        "app.services.board_service.is_owner",
        new=AsyncMock(return_value=True)
    ), patch(
        "app.services.board_service.crud_alredy_member_of_board",
        new=AsyncMock(return_value=False)
    ), patch(
        "app.services.board_service.crud_add_user_to_board",
        new=AsyncMock(side_effect=Exception("DB error"))
    ):

        with pytest.raises(HTTPException) as exc:
            await board_service.add_user_to_board(
                board_id="board-123",
                user_id="user-456",
                current_id="owner-123"
            )

        assert exc.value.status_code == 500
        assert exc.value.detail == "Failed to add user to board"
