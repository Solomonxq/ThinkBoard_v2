from app.api.deps import get_idea_service
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.idea import IdeaCreate, IdeaResponse
from app.services.ideas_service import IdeaService
from fastapi import APIRouter, Depends

router = APIRouter()


@router.post('/create', response_model=IdeaResponse)
async def create_idea_route(
    board_id: str,
    data: IdeaCreate,
    service: IdeaService = Depends(get_idea_service),
    current_user: User = Depends(get_current_user),
):
    return await service.create_idea(data, current_user.id, board_id)


@router.delete('/delete/{idea_id}')
async def delete_idea_route(
    board_id: str,
    idea_id: str,
    service: IdeaService = Depends(get_idea_service),
    current_user: User = Depends(get_current_user),
):
    await service.delete_idea(idea_id, current_user.id, board_id)
    return {"detail": "Idea deleted successfully"}
