from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.services.vote_service import VoteService
from fastapi import HTTPException, WebSocket

# -------------------------
# FIXTURES
# -------------------------

@pytest.fixture
def db():
    return AsyncMock()


@pytest.fixture
def service(db):
    return VoteService(db)


@pytest.fixture
def websocket():
    ws = AsyncMock(spec=WebSocket)
    ws.query_params = {"token": "valid_token"}
    return ws


# -------------------------
# AUTH TESTS
# -------------------------

def test_authorize_valid_token(service):
    with patch("app.services.vote_service.decode_token", return_value={"sub": "user1"}):
        user_id = service.authorize("token")
        assert user_id == "user1"


def test_authorize_invalid_token(service):
    with patch("app.services.vote_service.decode_token", return_value=None):
        user_id = service.authorize("bad")
        assert user_id is None


def test_authorize_no_token(service):
    assert service.authorize(None) is None


# -------------------------
# INIT STATE TEST
# -------------------------

@pytest.mark.asyncio
async def test_get_init_state_404(service, db):
    with patch("app.services.vote_service.get_idea_by_id", new=AsyncMock(return_value=None)):
        with pytest.raises(HTTPException) as exc:
            await service.get_init_state("idea1")
        assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_get_init_state_ok(service, db):
    fake_idea = MagicMock()
    fake_idea.voting_ends_at = None
    fake_idea.accepted = False

    with patch("app.services.vote_service.get_idea_by_id", new=AsyncMock(return_value=fake_idea)):
        with patch("app.services.vote_service.get_vote_counts", new=AsyncMock(return_value={"approve": 2, "reject": 1})):
            result = await service.get_init_state("idea1")

            assert result["event"] == "init"
            assert result["approve"] == 2
            assert result["reject"] == 1


# -------------------------
# VOTE TESTS
# -------------------------

@pytest.mark.asyncio
async def test_vote_not_in_board(service, db):
    with patch("app.services.vote_service.alredy_member_of_board", new=AsyncMock(return_value=False)):
        with pytest.raises(HTTPException) as exc:
            await service.vote("u1", "b1", "i1", True)

        assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_vote_create(service, db):
    with patch("app.services.vote_service.alredy_member_of_board", new=AsyncMock(return_value=True)):
        with patch("app.services.vote_service.get_idea_by_id", new=AsyncMock(return_value=MagicMock(voting_ends_at=None))):
            with patch("app.services.vote_service.get_vote", new=AsyncMock(return_value=None)):
                with patch("app.services.vote_service.create_vote", new=AsyncMock()):
                    with patch("app.services.vote_service.get_vote_counts", new=AsyncMock(return_value={"approve": 1, "reject": 0})):

                        result = await service.vote("u1", "b1", "i1", True)

                        assert result["event"] == "vote_updated"
                        assert result["approve"] == 1


# -------------------------
# FINALIZE TEST
# -------------------------

@pytest.mark.asyncio
async def test_finalize_accept(service, db):
    idea = MagicMock()
    idea.accepted = False

    with patch("app.services.vote_service.get_vote_counts", new=AsyncMock(return_value={"approve": 5, "reject": 2})):
        with patch("app.services.vote_service.get_idea_by_id", new=AsyncMock(return_value=idea)):
            with patch.object(db, "commit", new=AsyncMock()):

                result = await service.finalize_voting("i1", "b1")

                assert result["accepted"] is True
                assert idea.accepted is True


@pytest.mark.asyncio
async def test_finalize_delete(service, db):
    idea = MagicMock()

    with patch("app.services.vote_service.get_vote_counts", new=AsyncMock(return_value={"approve": 1, "reject": 3})):
        with patch("app.services.vote_service.get_idea_by_id", new=AsyncMock(return_value=idea)):
            with patch("app.services.vote_service.delete_idea", new=AsyncMock()):

                result = await service.finalize_voting("i1", "b1")

                assert result["accepted"] is False


# -------------------------
# WS HANDLER BASIC TEST
# -------------------------

@pytest.mark.asyncio
async def test_ws_handler_unauthorized(service, websocket):
    websocket.query_params = {}

    with patch.object(service, "authorize", return_value=None):
        await service.ws_handler(websocket, "i1", "b1")

        websocket.close.assert_called()
