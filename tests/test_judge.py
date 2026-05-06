import pytest

from app.judge.comparator import compare_output
from app.judge.executor import execute_test_case


@pytest.mark.asyncio
async def test_correct_code():
    result = await execute_test_case(
        code="a = int(input())\nb = int(input())\nprint(a + b)",
        input_data="2\n3\n",
        expected_output="5",
        time_limit_ms=5000,
        memory_limit_kb=262144,
    )
    assert result.status == "accepted", f"Expected accepted, got {result.status}: {result.error_message}"
    assert result.execution_time_ms > 0
    assert result.output.strip() == "5"


@pytest.mark.asyncio
async def test_wrong_answer():
    result = await execute_test_case(
        code="print(1)",
        input_data="",
        expected_output="2",
        time_limit_ms=5000,
        memory_limit_kb=262144,
    )
    assert result.status == "wrong_answer"


@pytest.mark.asyncio
async def test_runtime_error():
    result = await execute_test_case(
        code="1 / 0",
        input_data="",
        expected_output="",
        time_limit_ms=5000,
        memory_limit_kb=262144,
    )
    assert result.status == "runtime_error"


@pytest.mark.asyncio
async def test_time_limit_exceeded():
    result = await execute_test_case(
        code="while True: pass",
        input_data="",
        expected_output="",
        time_limit_ms=500,
        memory_limit_kb=262144,
    )
    assert result.status == "time_limit_exceeded"


@pytest.mark.asyncio
async def test_multiline_output():
    result = await execute_test_case(
        code="for i in range(3): print(i)",
        input_data="",
        expected_output="0\n1\n2",
        time_limit_ms=5000,
        memory_limit_kb=262144,
    )
    assert result.status == "accepted", f"Got {result.status}, output={result.output!r}, expected={result.expected_output!r}"


@pytest.mark.asyncio
async def test_syntax_error():
    result = await execute_test_case(
        code="print(",
        input_data="",
        expected_output="",
        time_limit_ms=5000,
        memory_limit_kb=262144,
    )
    assert result.status == "runtime_error"


def test_compare_output_exact_match():
    assert compare_output("hello", "hello") is True
    assert compare_output("hello", "world") is False


def test_compare_output_trailing_whitespace():
    assert compare_output("hello\n", "hello") is True
    assert compare_output("hello  ", "hello") is True
    assert compare_output("hello\n\n", "hello") is True


def test_compare_output_empty():
    assert compare_output("", "") is True
    assert compare_output("", "\n") is True
    assert compare_output("", "a") is False
