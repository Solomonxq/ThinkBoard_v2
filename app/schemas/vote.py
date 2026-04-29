from pydantic import BaseModel


class VoteCreate(BaseModel):
    status:bool

