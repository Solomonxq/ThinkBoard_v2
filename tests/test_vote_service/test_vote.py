import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.vote_service import VoteService
from fastapi import HTTPException, WebSocket


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


def test_authorize_valid_token(service):
    with patch("app.services.vote_service.decode_token", return_value={"sub": "user1"}):
        assert service.authorize("token") == "user1"


def test_authorize_invalid_token(service):
    with patch("app.services.vote_service.decode_token", return_value=None):
        assert service.authorize("bad") is None


def test_authorize_no_token(service):
    assert service.authorize(None) is None


@pytest.mark.asyncio
async def test_get_init_state_404(service):
    with patch("app.services.vote_service.get_idea_by_id", new=AsyncMock(return_value=None)):
        with pytest.raises(HTTPException) as exc:
            await service.get_init_state("idea1")
        assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_get_init_state_ok(service):
    fake_idea = MagicMock()
    fake_idea.voting_ends_at = None
    fake_idea.accepted = False

    with patch("app.services.vote_service.get_idea_by_id", new=AsyncMock(return_value=fake_idea)), \
         patch("app.services.vote_service.get_vote_counts", new=AsyncMock(return_value={"approve": 2, "reject": 1})):
        result = await service.get_init_state("idea1")

    assert result["event"] == "init"
    assert result["approve"] == 2
    assert result["reject"] == 1


@pytest.mark.asyncio
async def test_get_init_state_already_finished(service):
    from datetime import datetime, timezone
    fake_idea = MagicMock()
    fake_idea.voting_ends_at = datetime(2000, 1, 1, tzinfo=timezone.utc)
    fake_idea.accepted = True

    with patch("app.services.vote_service.get_idea_by_id", new=AsyncMock(return_value=fake_idea)):
        result = await service.get_init_state("idea1")

    assert result["event"] == "voting_already_finished"
    assert result["accepted"] is True


@pytest.mark.asyncio
async def test_vote_not_in_board(service):
    with patch("app.services.vote_service.already_member_of_board", new=AsyncMock(return_value=False)):
        with pytest.raises(HTTPException) as exc:
            await service.vote("u1", "b1", "i1", True)

    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_vote_idea_not_found(service):
    with patch("app.services.vote_service.already_member_of_board", new=AsyncMock(return_value=True)), \
         patch("app.services.vote_service.get_idea_by_id", new=AsyncMock(return_value=None)):
        with pytest.raises(HTTPException) as exc:
            await service.vote("u1", "b1", "i1", True)

    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_vote_ended(service):
    from datetime import datetime, timezone
    idea = MagicMock()
    idea.voting_ends_at = datetime(2000, 1, 1, tzinfo=timezone.utc)

    with patch("app.services.vote_service.already_member_of_board", new=AsyncMock(return_value=True)), \
         patch("app.services.vote_service.get_idea_by_id", new=AsyncMock(return_value=idea)):
        with pytest.raises(HTTPException) as exc:
            await service.vote("u1", "b1", "i1", True)

    assert exc.value.status_code == 400
    assert "ended" in exc.value.detail.lower()


@pytest.mark.asyncio
async def test_vote_create(service):
    with patch("app.services.vote_service.already_member_of_board", new=AsyncMock(return_value=True)), \
         patch("app.services.vote_service.get_idea_by_id", new=AsyncMock(return_value=MagicMock(voting_ends_at=None))), \
         patch("app.services.vote_service.get_vote", new=AsyncMock(return_value=None)), \
         patch("app.services.vote_service.create_vote", new=AsyncMock()), \
         patch("app.services.vote_service.get_vote_counts", new=AsyncMock(return_value={"approve": 1, "reject": 0})):
        result = await service.vote("u1", "b1", "i1", True)

    assert result["event"] == "vote_updated"
    assert result["approve"] == 1


@pytest.mark.asyncio
async def test_vote_update(service):
    existing = MagicMock()
    existing.status = False

    with patch("app.services.vote_service.already_member_of_board", new=AsyncMock(return_value=True)), \
         patch("app.services.vote_service.get_idea_by_id", new=AsyncMock(return_value=MagicMock(voting_ends_at=None))), \
         patch("app.services.vote_service.get_vote", new=AsyncMock(return_value=existing)), \
         patch("app.services.vote_service.update_vote", new=AsyncMock()), \
         patch("app.services.vote_service.get_vote_counts", new=AsyncMock(return_value={"approve": 1, "reject": 0})):
        result = await service.vote("u1", "b1", "i1", True)

    assert result["event"] == "vote_updated"


@pytest.mark.asyncio
async def test_vote_skip_same_status(service):
    existing = MagicMock()
    existing.status = True

    create_mock = AsyncMock()
    update_mock = AsyncMock()

    with patch("app.services.vote_service.already_member_of_board", new=AsyncMock(return_value=True)), \
         patch("app.services.vote_service.get_idea_by_id", new=AsyncMock(return_value=MagicMock(voting_ends_at=None))), \
         patch("app.services.vote_service.get_vote", new=AsyncMock(return_value=existing)), \
         patch("app.services.vote_service.create_vote", create_mock), \
         patch("app.services.vote_service.update_vote", update_mock), \
         patch("app.services.vote_service.get_vote_counts", new=AsyncMock(return_value={"approve": 1, "reject": 0})):
        await service.vote("u1", "b1", "i1", True)

    create_mock.assert_not_called()
    update_mock.assert_not_called()


@pytest.mark.asyncio
async def test_finalize_accept(service, db):
    idea = MagicMock()
    idea.accepted = False

    mock_board = MagicMock()
    mock_board.board_name = "Test Board"
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_board
    db.execute = AsyncMock(return_value=mock_result)

    with patch("app.services.vote_service.get_vote_counts", new=AsyncMock(return_value={"approve": 5, "reject": 2})), \
         patch("app.services.vote_service.get_idea_by_id", new=AsyncMock(return_value=idea)), \
         patch("app.services.vote_service.notify_voting_finished", new=AsyncMock()), \
         patch.object(db, "commit", new=AsyncMock()):
        result = await service.finalize_voting(db, "i1", "b1")

    assert result["accepted"] is True
    assert idea.accepted is True


@pytest.mark.asyncio
async def test_finalize_delete(service, db):
    idea = MagicMock()

    mock_board = MagicMock()
    mock_board.board_name = "Test Board"
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_board
    db.execute = AsyncMock(return_value=mock_result)

    with patch("app.services.vote_service.get_vote_counts", new=AsyncMock(return_value={"approve": 1, "reject": 3})), \
         patch("app.services.vote_service.get_idea_by_id", new=AsyncMock(return_value=idea)), \
         patch("app.services.vote_service.notify_voting_finished", new=AsyncMock()), \
         patch("app.services.vote_service.delete_idea", new=AsyncMock()):
        result = await service.finalize_voting(db, "i1", "b1")

    assert result["accepted"] is False


@pytest.mark.asyncio
async def test_finalize_idea_not_found(service, db):
    with patch("app.services.vote_service.get_vote_counts", new=AsyncMock(return_value={"approve": 1, "reject": 0})), \
         patch("app.services.vote_service.get_idea_by_id", new=AsyncMock(return_value=None)):
        with pytest.raises(HTTPException) as exc:
            await service.finalize_voting(db, "i1", "b1")

    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_ws_handler_unauthorized(service, websocket):
    websocket.query_params = {}

    with patch.object(service, "authorize", return_value=None):
        await service.ws_handler(websocket, "i1", "b1")

    websocket.close.assert_called()