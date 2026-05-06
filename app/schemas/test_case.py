import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class TestCaseCreate(BaseModel):
    input: str = Field(min_length=0)
    expected_output: str = Field(min_length=0)
    is_sample: bool = False
    order: int = Field(default=0, ge=0)


class TestCaseUpdate(BaseModel):
    input: str | None = None
    expected_output: str | None = None
    is_sample: bool | None = None
    order: int | None = Field(default=None, ge=0)


class TestCaseRead(BaseModel):
    id: uuid.UUID
    problem_id: uuid.UUID
    input: str
    expected_output: str
    is_sample: bool
    order: int
    created_at: datetime

    model_config = {"from_attributes": True}
