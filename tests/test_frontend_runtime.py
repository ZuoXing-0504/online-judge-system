import shutil
import subprocess
from pathlib import Path

import pytest


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js is required for frontend runtime smoke tests")
def test_frontend_runtime_smoke():
    root = Path(__file__).resolve().parents[1]
    script = root / "tests" / "frontend_runtime_smoke.mjs"
    result = subprocess.run(
        ["node", str(script)],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    assert result.returncode == 0, result.stderr or result.stdout
