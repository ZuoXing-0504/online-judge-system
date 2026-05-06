import asyncio
import os
import tempfile
import time

from app.core.config import settings
from app.judge.comparator import compare_output
from app.judge.sandbox import get_preexec_fn, get_subprocess_flags


class ExecutionResult:
    def __init__(self, status: str, execution_time_ms: float = 0.0,
                 memory_used_kb: float = 0.0, output: str = "",
                 expected_output: str = "", error_message: str = ""):
        self.status = status
        self.execution_time_ms = execution_time_ms
        self.memory_used_kb = memory_used_kb
        self.output = output
        self.expected_output = expected_output
        self.error_message = error_message


async def execute_test_case(
    code: str, input_data: str, expected_output: str,
    time_limit_ms: int, memory_limit_kb: int,
) -> ExecutionResult:
    timeout_sec = (time_limit_ms / 1000.0) + 1.0
    memory_limit_bytes = memory_limit_kb * 1024

    preexec_fn = get_preexec_fn(timeout_sec, memory_limit_bytes)
    flags = get_subprocess_flags()

    try:
        start_time = time.perf_counter()
        proc = await asyncio.create_subprocess_exec(
            "python", "-c", code,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            preexec_fn=preexec_fn,
            creationflags=flags,
        )

        try:
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(input=input_data.encode()),
                timeout=timeout_sec,
            )
        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()
            return ExecutionResult(status="time_limit_exceeded")

        elapsed_ms = (time.perf_counter() - start_time) * 1000
        stdout_str = stdout.decode("utf-8", errors="replace")

        if stdout_str and len(stdout_str.encode("utf-8")) > settings.max_output_length:
            stdout_str = stdout_str[:settings.max_output_length]

        if proc.returncode != 0:
            stderr_str = stderr.decode("utf-8", errors="replace")[:2000]
            return ExecutionResult(
                status="runtime_error",
                execution_time_ms=elapsed_ms,
                output=stdout_str,
                expected_output=expected_output,
                error_message=stderr_str.strip() or f"Exit code: {proc.returncode}",
            )

        passed = compare_output(expected_output, stdout_str)
        if passed:
            return ExecutionResult(
                status="accepted",
                execution_time_ms=elapsed_ms,
                output=stdout_str,
                expected_output=expected_output,
            )
        else:
            return ExecutionResult(
                status="wrong_answer",
                execution_time_ms=elapsed_ms,
                output=stdout_str,
                expected_output=expected_output,
            )

    except FileNotFoundError:
        return ExecutionResult(status="runtime_error", error_message="Python not found")
