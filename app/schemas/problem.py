import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ProblemCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    slug: str = Field(
        min_length=1,
        max_length=200,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
    )
    description: str = Field(min_length=1)
    difficulty: str = Field(default="easy", pattern=r"^(easy|medium|hard)$")
    time_limit_ms: int = Field(default=2000, ge=100, le=30000)
    memory_limit_kb: int = Field(default=262144, ge=4096, le=1048576)
    input_description: Optional[str] = None
    output_description: Optional[str] = None
    sample_input: Optional[str] = None
    sample_output: Optional[str] = None
    is_public: bool = False


class ProblemUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = None
    difficulty: Optional[str] = Field(default=None, pattern=r"^(easy|medium|hard)$")
    time_limit_ms: Optional[int] = Field(default=None, ge=100, le=30000)
    memory_limit_kb: Optional[int] = Field(default=None, ge=4096, le=1048576)
    input_description: Optional[str] = None
    output_description: Optional[str] = None
    sample_input: Optional[str] = None
    sample_output: Optional[str] = None
    is_public: Optional[bool] = None


class ProblemRead(BaseModel):
    id: uuid.UUID
    title: str
    slug: str
    description: str
    difficulty: str
    time_limit_ms: int
    memory_limit_kb: int
    input_description: Optional[str] = None
    output_description: Optional[str] = None
    sample_input: Optional[str] = None
    sample_output: Optional[str] = None
    is_public: bool
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProblemList(BaseModel):
    id: uuid.UUID
    title: str
    slug: str
    difficulty: str
    is_public: bool
    created_at: datetime

    model_config = {"from_attributes": True}
