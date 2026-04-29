from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.schemas.idea import IdeaCreate
from app.services.ideas_service import IdeaService
from fastapi import HTTPException
from pydantic import ValidationError


# -------------------------
# FIXTURES
# -------------------------
@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
def idea_service(mock_db):
    return IdeaService(db=mock_db)


# =====================================================
# SUCCESS
# =====================================================
@pytest.mark.asyncio
async def test_create_idea_success(idea_service):
    data = IdeaCreate(title="Test Idea", description="Test")

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


# =====================================================
# DUPLICATE TITLE
# =====================================================
@pytest.mark.asyncio
async def test_create_idea_duplicate_title(idea_service):
    data = IdeaCreate(title="Test Idea", description="Test")

    with patch("app.services.ideas_service.get_idea_by_title", AsyncMock(return_value=MagicMock())):

        with pytest.raises(HTTPException) as ex:
            await idea_service.create_idea(data, "user-1", "board-1")

        assert ex.value.status_code == 400
        assert "already exists" in ex.value.detail.lower()


# =====================================================
# USER NOT MEMBER
# =====================================================
@pytest.mark.asyncio
async def test_create_idea_user_not_member(idea_service):
    data = IdeaCreate(title="Test Idea", description="Test")

    with patch("app.services.ideas_service.get_idea_by_title", AsyncMock(return_value=None)), \
         patch("app.services.ideas_service.alredy_member_of_board", AsyncMock(return_value=False)):

        with pytest.raises(HTTPException) as ex:
            await idea_service.create_idea(data, "user-1", "board-1")

        assert ex.value.status_code == 403
        assert "not a member" in ex.value.detail.lower()


# =====================================================
# VALIDATION ERROR (Pydantic)
# =====================================================

def test_create_idea_invalid_title():
    with pytest.raises(ValidationError) as ex:
        IdeaCreate(title="ab", description="test")

    assert "string should have at least 3 characters" in str(ex.value).lower()
