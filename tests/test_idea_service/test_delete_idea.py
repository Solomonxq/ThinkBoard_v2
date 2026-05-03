from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from app.services.ideas_service import IdeaService
from fastapi import HTTPException


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
def idea_service(mock_db):
    return IdeaService(db=mock_db)


@pytest.fixture
def mock_idea():
    idea = MagicMock()
    idea.id = "idea-123"
    idea.board_id = "board-123"
    idea.user_id = "user-123"
    return idea


@pytest.mark.asyncio
async def test_delete_idea_success(idea_service, mock_db, mock_idea):
    mock_idea.board_id = "board-123"
    mock_idea.user_id = "user-123"

    with patch(
        "app.services.ideas_service.get_idea_by_id",
        new=AsyncMock(return_value=mock_idea)
    ), patch(
        "app.services.ideas_service.delete_idea_crud",
        new=AsyncMock()
    ) as mock_delete:
        await idea_service.delete_idea("idea-123", "user-123", "board-123")
        mock_delete.assert_awaited_once_with(mock_db, "idea-123")


@pytest.mark.asyncio
async def test_delete_idea_not_found(idea_service):
    with patch(
        "app.services.ideas_service.get_idea_by_id",
        new=AsyncMock(return_value=None)
    ):
        with pytest.raises(HTTPException) as ex:
            await idea_service.delete_idea("idea-123", "user-123", "board-123")

    assert ex.value.status_code == 404
    assert ex.value.detail == "Idea not found"


@pytest.mark.asyncio
async def test_delete_idea_not_in_board(idea_service, mock_idea):
    mock_idea.board_id = "other-board"
    mock_idea.user_id = "user-123"

    with patch(
        "app.services.ideas_service.get_idea_by_id",
        new=AsyncMock(return_value=mock_idea)
    ):
        with pytest.raises(HTTPException) as ex:
            await idea_service.delete_idea("idea-123", "user-123", "board-123")

    assert ex.value.status_code == 404
    assert ex.value.detail == "Idea not found in the specified board"


@pytest.mark.asyncio
async def test_delete_idea_not_owner(idea_service, mock_idea):
    mock_idea.board_id = "board-123"
    mock_idea.user_id = "other-user"

    with patch(
        "app.services.ideas_service.get_idea_by_id",
        new=AsyncMock(return_value=mock_idea)
    ):
        with pytest.raises(HTTPException) as ex:
            await idea_service.delete_idea("idea-123", "user-123", "board-123")

    assert ex.value.status_code == 403
    assert ex.value.detail == "User is not the owner of the idea"