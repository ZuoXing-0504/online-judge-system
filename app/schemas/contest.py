import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ContestCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    slug: str = Field(min_length=1, max_length=200, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    is_public: bool = True
    freeze_minutes: int = Field(default=0, ge=0)
    problem_slugs: list[str] = []


class ContestUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    is_public: Optional[bool] = None
    freeze_minutes: Optional[int] = None
    problem_slugs: Optional[list[str]] = None


class ContestRead(BaseModel):
    id: uuid.UUID
    title: str
    slug: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    is_public: bool
    freeze_minutes: int
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime
    participant_count: int = 0
    problem_count: int = 0

    model_config = {"from_attributes": True}


class ContestList(BaseModel):
    id: uuid.UUID
    title: str
    slug: str
    start_time: datetime
    end_time: datetime
    is_public: bool
    participant_count: int = 0
    problem_count: int = 0

    model_config = {"from_attributes": True}


class ContestProblemRead(BaseModel):
    id: uuid.UUID
    problem_id: uuid.UUID
    label: str
    order: int
    title: str = ""
    slug: str = ""

    model_config = {"from_attributes": True}


class LeaderboardEntry(BaseModel):
    rank: int
    user_id: uuid.UUID
    username: str
    solved_count: int
    penalty: int  # seconds
    score: int


class ContestRegisterRequest(BaseModel):
    contest_slug: str
