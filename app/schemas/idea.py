from pydantic import BaseModel, Field
from datetime import datetime

class IdeaCreate(BaseModel):
    title: str = Field(min_length=3, max_length=25)
    description: str
class IdeaResponse(BaseModel):
    id: str
    title: str
    description: str
    created_at: datetime
    board_id: str
    user_id: str
    

    model_config = {"from_attributes": True}