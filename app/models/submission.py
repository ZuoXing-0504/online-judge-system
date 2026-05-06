import uuid

from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class Submission(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "submissions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    problem_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("problems.id"), nullable=False, index=True
    )
    language: Mapped[str] = mapped_column(String(20), nullable=False, default="python")
    code: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")
    total_test_cases: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    passed_test_cases: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_execution_time_ms: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    max_memory_used_kb: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    user = relationship("User", back_populates="submissions")
    problem = relationship("Problem", back_populates="submissions")
    test_results = relationship(
        "SubmissionTestResult", back_populates="submission", cascade="all, delete-orphan"
    )
