from app.api.deps import get_profile_service
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import UpdateProfileRequest, UserPublicResponse, UserResponse
from app.services.profile_service import ProfileService
from fastapi import APIRouter, Depends, File, UploadFile

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    return current_user

@router.patch("/me", response_model=UserResponse)
async def update_my_profile(
    data: UpdateProfileRequest,
    service: ProfileService = Depends(get_profile_service),
    current_user: User = Depends(get_current_user)
):
    return await service.update_profile(current_user, data)

@router.post("/me/avatar", response_model=UserResponse)
async def upload_my_avatar(
    file: UploadFile = File(...),
    service: ProfileService = Depends(get_profile_service),
    current_user: User = Depends(get_current_user)
):
    return await service.upload_avatar(current_user, file)

@router.delete("/me", status_code=204)
async def delete_my_account(
    service: ProfileService = Depends(get_profile_service),
    current_user: User = Depends(get_current_user)
):
    await service.delete_account(current_user)

@router.get("/{username}", response_model=UserPublicResponse)
async def get_user_profile(
    username: str,
    service: ProfileService = Depends(get_profile_service)
):
    return await service.get_public_profile(username)
