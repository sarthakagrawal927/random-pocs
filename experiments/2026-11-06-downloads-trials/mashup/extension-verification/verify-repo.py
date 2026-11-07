import json
import subprocess
from pathlib import Path

checks = [
    ("check", ["npm", "run", "check"]),
    ("lint", ["npm", "run", "lint"]),
    ("test", ["npm", "test"]),
    ("build", ["npm", "run", "build"]),
    ("mashup-tests", ["uv", "run", "--project", "tools/mashup", "--locked", "--no-default-groups", "--extra", "mcp", "--with", "pytest", "python", "-m", "pytest", "tools/mashup/tests", "-q", "--junitxml=/Users/sarthak/Desktop/mashup-media-extension-2026-11-06/checks/mashup-tests.xml"]),
    ("mashup-lint", ["uv", "run", "--project", "tools/mashup", "--locked", "--no-default-groups", "--extra", "mcp", "--with", "ruff", "ruff", "check", "tools/mashup"]),
    ("mashup-format", ["uv", "run", "--project", "tools/mashup", "--locked", "--no-default-groups", "--extra", "mcp", "--with", "ruff", "ruff", "format", "--check", "tools/mashup"]),
]
output = Path(__file__).parent / "checks"
output.mkdir(exist_ok=True)
report = {}
for name, command in checks:
    with (output / (name + ".log")).open("w") as stream:
        result = subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT, timeout=300)
    report[name] = {"passed": result.returncode == 0, "log": str(output / (name + ".log"))}
    (output / "results.json").write_text(json.dumps(report, indent=2))
    print(name + (" passed" if result.returncode == 0 else " FAILED"), flush=True)
    if result.returncode:
        raise SystemExit(result.returncode)
