import os, sys, traceback, base64, subprocess, tempfile

lang = os.environ.get("OJ_LANG", "python")
encoded = os.environ.get("OJ_CODE", "")
if not encoded:
    sys.exit(0)

code = base64.b64decode(encoded).decode("utf-8")

if lang == "python":
    try:
        exec(code)
    except Exception:
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

elif lang == "cpp":
    with tempfile.TemporaryDirectory() as td:
        src = os.path.join(td, "main.cpp")
        with open(src, "w") as f:
            f.write(code)
        r = subprocess.run(
            ["g++", "-std=c++17", "-O2", "-o", os.path.join(td, "main"), src],
            capture_output=True, text=True, timeout=15,
        )
        if r.returncode != 0:
            sys.stderr.write(r.stderr[:2000])
            sys.exit(1)
        r = subprocess.run(
            [os.path.join(td, "main")],
            input=sys.stdin.read(), capture_output=True, text=True, timeout=10,
        )
        sys.stdout.write(r.stdout)
        if r.stderr:
            sys.stderr.write(r.stderr[:2000])
        sys.exit(r.returncode)

elif lang == "java":
    with tempfile.TemporaryDirectory() as td:
        src = os.path.join(td, "Main.java")
        with open(src, "w") as f:
            f.write(code)
        r = subprocess.run(
            ["javac", src], capture_output=True, text=True, timeout=20,
        )
        if r.returncode != 0:
            sys.stderr.write(r.stderr[:2000])
            sys.exit(1)
        r = subprocess.run(
            ["java", "-cp", td, "Main"],
            input=sys.stdin.read(), capture_output=True, text=True, timeout=10,
        )
        sys.stdout.write(r.stdout)
        if r.stderr:
            sys.stderr.write(r.stderr[:2000])
        sys.exit(r.returncode)

else:
    sys.stderr.write(f"Unknown language: {lang}")
    sys.exit(1)
