from pydantic import BaseModel, EmailStr, Field
from app.schemas.common import BoardShort

class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=25)
    password: str = Field(min_length=4)
    bio: str | None = Field(default=None, max_length=500)
    avatar_url: str | None = None

class UserShort(BaseModel):
    id: str
    username: str
    email: str
    model_config = {"from_attributes": True}


class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    is_active: bool
    bio: str | None = None
    avatar_url: str | None = None
    boards: list[BoardShort] = []
    member_of: list[BoardShort] = []
    favorite_boards: list[BoardShort] = []
    model_config = {"from_attributes": True}

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=4)

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshRequest(BaseModel):
    refresh_token: str


class SetPasswordRequest(BaseModel):
    password: str = Field(min_length=4)

class RegisterResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    needs_password: bool = False


class UserPublicResponse(BaseModel):
    id: str
    username: str
    bio: str | None = None
    avatar_url: str | None = None
    boards: list[BoardShort] = []
    member_of: list[BoardShort] = []
    model_config = {"from_attributes": True}
    favorite_boards: list[BoardShort] = []

class UpdateProfileRequest(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=25)
    bio: str | None = Field(default=None, max_length=500)
    avatar_url: str | None = None