import argparse
import asyncio
import hashlib
import json
from importlib.metadata import version
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def run(config_path, output):
    config = json.loads(config_path.read_text())["mcpServers"]["mashup-media"]
    parameters = StdioServerParameters(**config, cwd="/tmp")

    async def call(session, name, arguments):
        response = await asyncio.wait_for(session.call_tool(name, arguments), 20)
        assert not response.isError, response
        assert response.structuredContent is not None
        assert any(getattr(item, "text", "") for item in response.content)
        return response.structuredContent

    assets = Path("/Users/sarthak/Desktop/media-extension-demo-2026-11-06/assets")
    async with stdio_client(parameters) as (read, write), ClientSession(read, write) as session:
        await asyncio.wait_for(session.initialize(), 20)
        catalog = await call(session, "skills_list", {})
        names = {item["name"] for item in catalog["skills"]}
        required = {"agent-desktop", "cinetic", "code-video", "local-voiceover", "raea", "raea-bevy", "mashup-media"}
        assert required <= names, required - names
        ids = []
        for name in ("moving-landscape.mp4", "dancing-mascot.mov"):
            item = await call(session, "asset_register", {
                "path": str(assets / name),
                "rights": {"title": name, "creator": "Original procedural demo",
                           "sourceUrl": "urn:fleet:original-dance-demo:20261106",
                           "license": "creator-owned", "licenseUrl": "urn:fleet:creator-owned",
                           "rightsConfirmed": True},
            })
            ids.append(item["id"])
        plan = await call(session, "render_plan", {"composition": {
            "background": ids[0], "foreground": ids[1], "duration": 8.0,
            "preset": "landscape", "fps": 30, "x": 0.65, "y": 0.58,
            "width": 0.4, "loop": True, "motion": "orbit",
        }})
        validated = await call(session, "render_validate", {"plan_id": plan["planId"]})
        assert validated["approval"]["status"] == "proposed"
        request = {"plan_id": plan["planId"], "idempotency_key": plan["planId"],
                   "approval": {"status": "approved", "approvedBy": "Owner-requested original demo",
                                "planHash": plan["planHash"]}}
        job = await call(session, "render_start", request)
        assert (await call(session, "render_start", request))["jobId"] == job["jobId"]
        (output / "submitted.json").write_text(json.dumps({"job": job, "plan": plan,
            "skillCount": len(catalog["skills"]), "requiredSkills": sorted(required)}, indent=2))
    async with stdio_client(parameters) as (read, write), ClientSession(read, write) as session:
        await asyncio.wait_for(session.initialize(), 20)
        for _ in range(360):
            status = await call(session, "job_status", {"job_id": job["jobId"]})
            if status["state"] in {"succeeded", "failed", "cancelled"}:
                break
            await asyncio.sleep(0.25)
        assert status["state"] == "succeeded", status
        result = await call(session, "job_result", {"job_id": job["jobId"]})
    video = Path(result["video"]["path"])
    assert hashlib.sha256(video.read_bytes()).hexdigest() == result["video"]["sha256"]
    receipt = json.loads(Path(result["receipt"]["path"]).read_text())
    assert receipt["approval"]["attestation"] == "mcp-client"
    assert receipt["validation"]["approvalAuthority"] == "mcp-client-attested"
    assert receipt["runtime"]["revision"] == "mashup-extension@" + version("mashup")
    (output / "dancing-overlay.mp4").write_bytes(video.read_bytes())
    (output / "result.json").write_text(json.dumps(result, indent=2))
    print(json.dumps({"installedRenderVerified": True, "skillCount": len(catalog["skills"]),
                      "video": str(output / "dancing-overlay.mp4")}, indent=2))


parser = argparse.ArgumentParser()
parser.add_argument("--config", type=Path, required=True)
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
args.output.mkdir(parents=True, exist_ok=True)
asyncio.run(run(args.config, args.output))
