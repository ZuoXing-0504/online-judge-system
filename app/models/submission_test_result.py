import uuid

from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class SubmissionTestResult(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "submission_test_results"

    submission_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("submissions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    test_case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("test_cases.id"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    execution_time_ms: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    memory_used_kb: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    output: Mapped[str | None] = mapped_column(Text, nullable=True)
    expected_output: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    submission = relationship("Submission", back_populates="test_results")
