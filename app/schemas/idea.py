from datetime import datetime

from pydantic import BaseModel, Field


class IdeaCreate(BaseModel):
    title: str = Field(min_length=3, max_length=25)
    description: str
    voting_ends_at: datetime


class IdeaResponse(BaseModel):
    id: str
    title: str
    description: str | None
    board_id: str
    user_id: str
    accepted: bool
    voting_ends_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}
