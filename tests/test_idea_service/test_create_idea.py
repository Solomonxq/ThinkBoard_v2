from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app.schemas.idea import IdeaCreate
from app.services.ideas_service import IdeaService

VOTING_ENDS_AT = datetime.now(timezone.utc) + timedelta(days=7)




@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
def idea_service(mock_db):
    return IdeaService(db=mock_db)



@pytest.mark.asyncio
async def test_create_idea_success(idea_service):
    data = IdeaCreate(title="Test Idea", description="Test", voting_ends_at=VOTING_ENDS_AT)
    board_id = "board-123"
    user_id = "user-123"

    mock_idea = MagicMock()
    mock_idea.id = "idea-1"
    mock_idea.title = data.title
    mock_idea.description = data.description
    mock_idea.board_id = board_id
    mock_idea.user_id = user_id

    with patch("app.services.ideas_service.get_idea_by_title", AsyncMock(return_value=None)), \
         patch("app.services.ideas_service.alredy_member_of_board", AsyncMock(return_value=True)), \
         patch("app.services.ideas_service.create_idea_crud", AsyncMock(return_value=mock_idea)):

        result = await idea_service.create_idea(data, user_id, board_id)

    assert result.id == "idea-1"
    assert result.title == data.title
    assert result.board_id == board_id
    assert result.user_id == user_id

@pytest.mark.asyncio
async def test_create_idea_duplicate_title(idea_service):
    data = IdeaCreate(title="Test Idea", description="Test", voting_ends_at=VOTING_ENDS_AT)

    with patch("app.services.ideas_service.get_idea_by_title", AsyncMock(return_value=MagicMock())):
        with pytest.raises(HTTPException) as ex:
            await idea_service.create_idea(data, "user-1", "board-1")

    assert ex.value.status_code == 400
    assert "already exists" in ex.value.detail.lower()

@pytest.mark.asyncio
async def test_create_idea_db_exception(idea_service):
    data = IdeaCreate(title="Test Idea", description="Test", voting_ends_at=VOTING_ENDS_AT)

    with patch("app.services.ideas_service.get_idea_by_title", AsyncMock(return_value=None)), \
         patch("app.services.ideas_service.alredy_member_of_board", AsyncMock(return_value=True)), \
         patch("app.services.ideas_service.create_idea_crud", AsyncMock(side_effect=Exception("DB error"))):

        with pytest.raises(Exception) as ex:
            await idea_service.create_idea(data, "user-1", "board-1")

    assert "DB error" in str(ex.value)




def test_create_idea_voting_ends_at_in_past():
    past = datetime.now(timezone.utc) - timedelta(days=1)
    with pytest.raises(ValidationError):
        IdeaCreate(title="Test Idea", description="Test", voting_ends_at=past)



def test_create_idea_empty_title():
    with pytest.raises(ValidationError):
        IdeaCreate(title="", description="Test", voting_ends_at=VOTING_ENDS_AT)


def test_create_idea_empty_description():
    with pytest.raises(ValidationError):
        IdeaCreate(title="Valid Title", description="", voting_ends_at=VOTING_ENDS_AT)



def test_create_idea_whitespace_title():
    with pytest.raises(ValidationError):
        IdeaCreate(title="   ", description="Test", voting_ends_at=VOTING_ENDS_AT)

def test_create_idea_title_too_long():
    with pytest.raises(ValidationError):
        IdeaCreate(title="A" * 256, description="Test", voting_ends_at=VOTING_ENDS_AT)

@pytest.mark.asyncio
async def test_create_idea_different_boards(idea_service):
    """Одна й та сама ідея може існувати в різних бордах"""
    data = IdeaCreate(title="Same Title", description="Test", voting_ends_at=VOTING_ENDS_AT)

    mock_idea = MagicMock()
    mock_idea.id = "idea-99"
    mock_idea.title = data.title
    mock_idea.board_id = "board-999"
    mock_idea.user_id = "user-999"

    with patch("app.services.ideas_service.get_idea_by_title", AsyncMock(return_value=None)), \
         patch("app.services.ideas_service.alredy_member_of_board", AsyncMock(return_value=True)), \
         patch("app.services.ideas_service.create_idea_crud", AsyncMock(return_value=mock_idea)):

        result = await idea_service.create_idea(data, "user-999", "board-999")

    assert result.id == "idea-99"
    assert result.board_id == "board-999"