from pydantic import BaseModel, Field
from app.schemas.common import UserShort, BoardShort

class AddMemberRequest(BaseModel):
    user_id: str

class DeleteMemberRequest(BaseModel):
    user_id: str

class BulkMemberRequest(BaseModel):
    user_ids: list[str]

class BoardCreate(BaseModel):
    board_name: str = Field(min_length=1, max_length=25)
    access: bool
    description: str = Field(min_length=1, max_length=500)

class BoardResponse(BaseModel):
    id: str
    board_name: str
    description: str
    owner_id: str
    access: bool
    members: list[UserShort] = []
    model_config = {"from_attributes": True}