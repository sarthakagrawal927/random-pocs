import argparse
import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--bundle", type=Path, required=True)
args = parser.parse_args()
root = Path(__file__).parent
bundle = args.bundle.resolve(strict=True)
output = root / ("verification-" + bundle.name)
output.mkdir()
relocated = output / "relocated bundle"
shutil.copytree(bundle, relocated)
destination = Path("/Users/sarthak/Library/Application Support/Fleet/Extensions/mashup-media")
state = Path("/Users/sarthak/Library/Application Support/Fleet/Media/Mashup")
roots = ["/Users/sarthak/.codex/skills", "/Users/sarthak/.codex/skills/.system",
         "/Users/sarthak/.agents/skills", "/Users/sarthak/.agent-config/skills",
         "/Users/sarthak/.local/share/agent-config/skills",
         "/Users/sarthak/Desktop/fleet/saas-maker/tooling/skills"]
arguments = ["--destination", str(destination), "--state-dir", str(state),
             "--input-root", "/Users/sarthak/Desktop/media-extension-demo-2026-11-06/assets"]
for canonical_root in dict.fromkeys(str(Path(path).resolve()) for path in roots):
    arguments += ["--skills-root", canonical_root]
environment = {"PATH": os.environ["PATH"], "PYTHONPATH": "/nonexistent/should-not-be-used"}


def state_files():
    return {str(path.relative_to(state)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in state.rglob("*") if path.is_file()} if state.exists() else {}


def install(path):
    result = subprocess.run(["/usr/bin/python3", str(path / "install.py"), *arguments],
                            cwd="/tmp", env=environment, text=True, capture_output=True,
                            check=True, timeout=180)
    return json.loads(result.stdout)


before = state_files()
installed = install(relocated)
assert installed["action"] == "installed"
assert state_files() == before, "Installing must not touch operator state"
retained = relocated.with_name("retained bundle")
relocated.rename(retained)
reused = install(retained)
assert reused["action"] == "reused"
assert reused["configuration"] == installed["configuration"]
assert state_files() == before, "Verifying must not resume operator state"
(output / "install-result.json").write_text(json.dumps(installed, indent=2))
(output / "reuse-result.json").write_text(json.dumps(reused, indent=2))
config = json.loads(Path(installed["configuration"]).read_text())["mcpServers"]["mashup-media"]
assert str(retained) not in json.dumps(config)
assert "worktrees" not in json.dumps(config)
subprocess.run([config["command"], str(root / "verify-installed.py"), "--config",
                installed["configuration"], "--output", str(output / "installed-demo")],
               cwd="/tmp", env={"PATH": config["env"]["PATH"]}, check=True, timeout=120)
print(json.dumps({"systemPythonBootstrapVerified": True, "relocatedInstallVerified": True,
                  "repeatInstallVerified": True, "configuration": installed["configuration"]}, indent=2))
