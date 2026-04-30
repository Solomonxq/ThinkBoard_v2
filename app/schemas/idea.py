from datetime import datetime, timezone
from pydantic import BaseModel, field_validator, Field


class IdeaCreate(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    description: str = Field(min_length=1)
    voting_ends_at: datetime

    @field_validator("voting_ends_at")
    @classmethod
    def voting_ends_at_must_be_future(cls, v):
        if v <= datetime.now(timezone.utc):
            raise ValueError("voting_ends_at must be in the future")
        return v

    @field_validator("title")
    @classmethod
    def title_no_whitespace_only(cls, v):
        if not v.strip():
            raise ValueError("title cannot be whitespace only")
        return v

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
