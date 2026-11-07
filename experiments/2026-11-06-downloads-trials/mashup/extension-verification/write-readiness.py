import hashlib
import json
from pathlib import Path

root = Path(__file__).parent
bundle = root / "bundles/mashup-media-0.1.0-11d0b54bcc19778a43e7"
verification = root / ("verification-" + bundle.name)
manifest = json.loads((bundle / "bundle.json").read_text())
archive = Path(str(bundle) + ".tar.gz")
installed = json.loads((verification / "install-result.json").read_text())
report = {
    "schema": "fleet.mashup-local-readiness.v1",
    "sourceRevision": manifest["sourceRevision"], "sourceDirty": manifest["sourceDirty"],
    "bundle": str(bundle),
    "archive": {"path": str(archive), "bytes": archive.stat().st_size,
                "sha256": hashlib.sha256(archive.read_bytes()).hexdigest()},
    "runtime": installed["runtime"], "paceConfigurationProposal": installed["configuration"],
    "paceSkill": installed["paceSkill"], "verificationScript": installed["verificationScript"],
    "paceConnectionActivated": False,
    "verified": {"systemPythonBootstrap": True, "relocatedInstall": True, "repeatInstall": True,
                 "operatorStateUntouchedByInstaller": True, "actualInstalledRender": True,
                 "fullDecode": True, "actualPaceSkillParser": True,
                 "canonicalGuides": json.loads((verification / "installed-demo/submitted.json").read_text())["skillCount"]},
    "demo": json.loads((verification / "installed-demo/result.json").read_text()),
    "independentReview": "running", "pullRequest": "https://github.com/sass-maker/fleet-social/pull/26",
}
(root / "readiness.json").write_text(json.dumps(report, indent=2))
print(json.dumps(report["archive"], indent=2))
