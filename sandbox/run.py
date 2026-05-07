import os
import sys
import traceback
import base64

encoded = os.environ.get("OJ_CODE", "")
if not encoded:
    sys.exit(0)

code = base64.b64decode(encoded).decode("utf-8")

# Swap stdin to a custom reader that splits code from input.
# The code has already been extracted from the env var.
# sys.stdin still points to the container's stdin (test input).
exec_globals = {"__builtins__": __builtins__}
try:
    exec(code, exec_globals)
except Exception:
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)
