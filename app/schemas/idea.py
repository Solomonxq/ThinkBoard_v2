from datetime import datetime, timezone, timedelta
from pydantic import BaseModel, field_validator, Field

MAX_VOTING_DURATION = timedelta(days=1)


class IdeaCreate(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    description: str = Field(min_length=1)
    voting_ends_at: datetime

    @field_validator("voting_ends_at")
    @classmethod
    def voting_ends_at_must_be_future(cls, v):
        now = datetime.now(timezone.utc)
        if v <= now:
            raise ValueError("voting_ends_at must be in the future")
        if v > now + MAX_VOTING_DURATION:
            raise ValueError("voting_ends_at cannot be more than 1 day from now")
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

class IdeaDetail(IdeaResponse):
    author: str | None = None
    approve: int = 0
    reject: int = 0
