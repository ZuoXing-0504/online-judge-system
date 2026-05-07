import uuid
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class SubmissionCreate(BaseModel):
    problem_slug: str
    code: str = Field(min_length=1, max_length=65536)
    language: Literal["python"] = "python"


class SubmissionList(BaseModel):
    id: uuid.UUID
    problem_id: uuid.UUID
    problem_slug: str = ""
    problem_title: str = ""
    status: str
    total_test_cases: int
    passed_test_cases: int
    max_execution_time_ms: float
    max_memory_used_kb: float
    created_at: datetime

    model_config = {"from_attributes": True}


class TestResultRead(BaseModel):
    id: uuid.UUID
    test_case_id: uuid.UUID
    is_sample: bool = False
    status: str
    execution_time_ms: float
    memory_used_kb: float
    output: Optional[str] = None
    expected_output: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class SubmissionDetail(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    username: str = ""
    problem_id: uuid.UUID
    problem_title: str = ""
    problem_slug: str = ""
    language: str
    code: str
    status: str
    total_test_cases: int
    passed_test_cases: int
    max_execution_time_ms: float
    max_memory_used_kb: float
    error_message: Optional[str] = None
    created_at: datetime
    test_results: list[TestResultRead] = []

    model_config = {"from_attributes": True}


class SubmissionCreateResponse(BaseModel):
    id: uuid.UUID
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
