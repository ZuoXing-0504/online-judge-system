import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class CommentCreate(BaseModel):
    content: str = Field(min_length=1, max_length=2000)


class CommentRead(BaseModel):
    id: uuid.UUID
    problem_id: uuid.UUID
    user_id: uuid.UUID
    username: str = ""
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}
