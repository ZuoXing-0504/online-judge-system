import traceback
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.judge.executor import execute_test_case
from app.models.problem import Problem
from app.models.submission import Submission
from app.models.submission_test_result import SubmissionTestResult
from app.models.test_case import TestCase


async def _do_judge(db: AsyncSession, submission_id: uuid.UUID) -> None:
    result = await db.execute(
        select(Submission).where(Submission.id == submission_id)
    )
    submission = result.scalar_one_or_none()
    if not submission:
        return

    problem_result = await db.execute(
        select(Problem).where(Problem.id == submission.problem_id)
    )
    problem = problem_result.scalar_one_or_none()
    if not problem:
        return

    test_cases_result = await db.execute(
        select(TestCase)
        .where(TestCase.problem_id == submission.problem_id)
        .order_by(TestCase.order)
    )
    test_cases = list(test_cases_result.scalars().all())
    if not test_cases:
        submission.status = "accepted"
        await db.commit()
        return

    submission.status = "running"
    submission.total_test_cases = len(test_cases)
    await db.commit()

    passed = 0
    max_time = 0.0
    max_mem = 0.0
    final_status = "accepted"
    error_msg = None

    for tc in test_cases:
        exec_result = await execute_test_case(
            code=submission.code,
            input_data=tc.input,
            expected_output=tc.expected_output,
            time_limit_ms=problem.time_limit_ms,
            memory_limit_kb=problem.memory_limit_kb,
        )

        test_result = SubmissionTestResult(
            submission_id=submission.id,
            test_case_id=tc.id,
            status=exec_result.status,
            execution_time_ms=exec_result.execution_time_ms,
            memory_used_kb=exec_result.memory_used_kb,
            output=exec_result.output,
            expected_output=exec_result.expected_output if tc.is_sample else None,
            error_message=exec_result.error_message,
        )
        db.add(test_result)

        if exec_result.execution_time_ms > max_time:
            max_time = exec_result.execution_time_ms
        if exec_result.memory_used_kb > max_mem:
            max_mem = exec_result.memory_used_kb

        if exec_result.status == "accepted":
            passed += 1
        elif final_status == "accepted":
            final_status = exec_result.status
            error_msg = exec_result.error_message

    submission.status = final_status
    submission.passed_test_cases = passed
    submission.max_execution_time_ms = max_time
    submission.max_memory_used_kb = max_mem
    submission.error_message = error_msg
    await db.commit()


async def judge_submission(db: AsyncSession, submission_id: uuid.UUID) -> None:
    try:
        await _do_judge(db, submission_id)
    except Exception:
        await db.rollback()
        try:
            submission = await db.get(Submission, submission_id)
            if submission and submission.status == "running":
                submission.status = "error"
                submission.error_message = traceback.format_exc()[-2000:]
                await db.commit()
        except Exception:
            pass
