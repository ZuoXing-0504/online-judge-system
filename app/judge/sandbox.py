import platform
import subprocess


def get_preexec_fn(time_limit_sec: float, memory_limit_bytes: int):
    """Returns a preexec function for subprocess resource limits.
    Only works on Linux/macOS. Returns None on Windows."""
    if platform.system() == "Windows":
        return None

    def _set_limits():
        import resource
        cpu_limit = int(time_limit_sec) + 1
        resource.setrlimit(resource.RLIMIT_CPU, (cpu_limit, cpu_limit))
        resource.setrlimit(resource.RLIMIT_AS, (memory_limit_bytes, memory_limit_bytes))
        try:
            resource.setrlimit(resource.RLIMIT_NPROC, (0, 0))
        except (ValueError, resource.error):
            pass

    return _set_limits


def get_subprocess_flags():
    if platform.system() == "Windows":
        return subprocess.CREATE_NO_WINDOW  # type: ignore[attr-defined]
    return 0
