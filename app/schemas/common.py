from pydantic import BaseModel


class UserShort(BaseModel):
    id: str
    username: str
    email: str
    model_config = {"from_attributes": True}

class BoardShort(BaseModel):
    id: str
    board_name: str
    model_config = {"from_attributes": True}
