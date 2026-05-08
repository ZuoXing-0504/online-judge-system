import asyncio
import base64
import platform
import subprocess
import sys
import time

import docker
from docker.errors import DockerException, ImageNotFound

from app.core.config import settings
from app.judge.comparator import compare_output
from app.judge.sandbox import get_preexec_fn, get_subprocess_flags

_client: docker.DockerClient | None = None


def _get_client() -> docker.DockerClient:
    global _client
    if _client is None:
        _client = docker.from_env()
    return _client


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


async def _execute_locally(
    code: str,
    input_data: str,
    expected_output: str,
    time_limit_ms: int,
    memory_limit_kb: int,
    language: str = "python",
) -> ExecutionResult:
    if language != "python":
        return ExecutionResult(
            status="runtime_error",
            error_message=f"Local execution only supports Python (requested: {language}). Use Docker for multi-language judging.",
        )

    timeout_sec = max(time_limit_ms / 1000.0, 0.1)
    preexec_fn = get_preexec_fn(timeout_sec, memory_limit_kb * 1024)
    creationflags = get_subprocess_flags()
    start_time = time.perf_counter()

    def _run_local() -> subprocess.CompletedProcess[bytes]:
        return subprocess.run(
            [sys.executable, "-c", code],
            input=(input_data or "").encode(),
            capture_output=True,
            timeout=timeout_sec,
            preexec_fn=preexec_fn,
            creationflags=creationflags,
            check=False,
        )

    try:
        completed = await asyncio.to_thread(_run_local)
    except subprocess.TimeoutExpired:
        return ExecutionResult(status="time_limit_exceeded")
    except Exception as exc:
        return ExecutionResult(status="runtime_error", error_message=str(exc)[:200])

    elapsed_ms = (time.perf_counter() - start_time) * 1000
    stdout_str = completed.stdout.decode("utf-8", errors="replace")
    stderr_str = completed.stderr.decode("utf-8", errors="replace")

    if stdout_str and len(stdout_str.encode("utf-8")) > settings.max_output_length:
        stdout_str = stdout_str[:settings.max_output_length]

    if completed.returncode != 0:
        return ExecutionResult(
            status="runtime_error",
            execution_time_ms=elapsed_ms,
            output=stdout_str,
            expected_output=expected_output,
            error_message=stderr_str.strip() or f"Exit code: {completed.returncode}",
        )

    if compare_output(expected_output, stdout_str):
        return ExecutionResult(
            status="accepted",
            execution_time_ms=elapsed_ms,
            output=stdout_str,
            expected_output=expected_output,
        )

    return ExecutionResult(
        status="wrong_answer",
        execution_time_ms=elapsed_ms,
        output=stdout_str,
        expected_output=expected_output,
    )


async def execute_test_case(
    code: str, input_data: str, expected_output: str,
    time_limit_ms: int, memory_limit_kb: int,
    language: str = "python",
) -> ExecutionResult:
    if platform.system() == "Windows":
        return await _execute_locally(
            code, input_data, expected_output, time_limit_ms, memory_limit_kb, language
        )

    timeout_sec = (time_limit_ms / 1000.0) + 2.0
    memory_mb = max(16, memory_limit_kb // 1024)
    encoded_code = base64.b64encode(code.encode()).decode()

    try:
        client = _get_client()
    except DockerException:
        return await _execute_locally(
            code, input_data, expected_output, time_limit_ms, memory_limit_kb, language
        )

    try:
        start_time = time.perf_counter()
        container = client.containers.create(
            image="oj-sandbox:latest",
            environment={"OJ_CODE": encoded_code, "OJ_LANG": language},
            stdin_open=True,
            network_disabled=True,
            mem_limit=f"{memory_mb}m",
            nano_cpus=1_000_000_000,
            read_only=True,
            tmpfs={"/tmp": "size=128m,exec"},
            cap_drop=["ALL"],
            security_opt=["no-new-privileges"],
        )

        def _run():
            try:
                container.start()
                socket = container.attach_socket(
                    params={"stdin": 1, "stdout": 1, "stderr": 1, "stream": 1}
                )
                if hasattr(socket, "_sock"):
                    sock = socket._sock
                    sock.sendall((input_data or "").encode())
                    sock.shutdown(1)
                result = container.wait(timeout=int(timeout_sec))
                stdout = container.logs(stdout=True, stderr=False).decode(
                    "utf-8", errors="replace"
                )
                stderr = container.logs(stdout=False, stderr=True).decode(
                    "utf-8", errors="replace"
                )
                return stdout, stderr, result.get("StatusCode", 1)
            except Exception as e:
                return "", str(e), 1
            finally:
                try:
                    container.remove(force=True)
                except Exception:
                    pass

        try:
            stdout_str, stderr_str, exit_code = await asyncio.wait_for(
                asyncio.to_thread(_run), timeout=timeout_sec + 3
            )
        except asyncio.TimeoutError:
            try:
                container.remove(force=True)
            except Exception:
                pass
            return ExecutionResult(status="time_limit_exceeded")

        elapsed_ms = (time.perf_counter() - start_time) * 1000

        if stdout_str and len(stdout_str.encode("utf-8")) > settings.max_output_length:
            stdout_str = stdout_str[:settings.max_output_length]

        if exit_code == 137:
            return ExecutionResult(status="time_limit_exceeded")

        if exit_code != 0:
            return ExecutionResult(
                status="runtime_error",
                execution_time_ms=elapsed_ms,
                output=stdout_str,
                expected_output=expected_output,
                error_message=stderr_str.strip() or f"Exit code: {exit_code}",
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

    except ImageNotFound:
        return await _execute_locally(
            code, input_data, expected_output, time_limit_ms, memory_limit_kb, language
        )
    except DockerException as e:
        fallback = await _execute_locally(
            code, input_data, expected_output, time_limit_ms, memory_limit_kb
        )
        if fallback.status != "runtime_error" or not fallback.error_message:
            return fallback
        fallback.error_message = fallback.error_message or str(e)[:200]
        return fallback
