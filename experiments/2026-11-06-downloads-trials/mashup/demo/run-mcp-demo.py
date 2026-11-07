import asyncio
import json
from pathlib import Path
import subprocess
import time

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parent
WORKTREE = Path('/Users/sarthak/Library/Application Support/Fleet/Agent Workspaces.noindex/worktrees/fleet-social-media-extension-20261106')
PYTHON = WORKTREE / 'tools/mashup/.venv/bin/python'
ROOTS = [Path('/Users/sarthak') / name for name in [
    '.codex/skills', '.codex/skills/.system', '.agents/skills', '.agent-config/skills',
    '.local/share/agent-config/skills', 'Desktop/fleet/saas-maker/tooling/skills',
]]
ARGS = ['-m', 'mashup.extension.mcp', '--state-dir', str(ROOT / 'state'), '--input-root', str(ROOT / 'assets')]
for root in dict.fromkeys(path.resolve() for path in ROOTS if path.is_dir()):
    ARGS += ['--skills-root', str(root)]
CONFIG = json.loads(subprocess.check_output([str(PYTHON), *ARGS, '--print-pace-config'], text=True))
(ROOT / 'pace-mcp.json').write_text(json.dumps(CONFIG, indent=2))
PARAMETERS = StdioServerParameters(**CONFIG['mcpServers']['mashup-media'], cwd='/tmp')


async def call(session, name, arguments=None):
    async with asyncio.timeout(20):
        response = await session.call_tool(name, arguments or {})
    if response.isError:
        raise RuntimeError(str(response.content))
    assert response.structuredContent is not None, 'Pace needs structuredContent and readable text'
    assert any(getattr(item, 'text', '') for item in response.content)
    return response.structuredContent


async def submit():
    async with stdio_client(PARAMETERS) as streams:
        async with ClientSession(*streams) as session:
            await session.initialize()
            tools = [tool.name for tool in (await session.list_tools()).tools]
            skills = (await call(session, 'skills_list'))['skills']
            names = {skill['name'] for skill in skills}
            assert {'code-video', 'cinetic', 'raea', 'raea-bevy', 'local-voiceover', 'agent-desktop'} <= names
            provenance = {
                'creator': 'Original procedural demonstration for the owner',
                'license': 'creator-owned', 'licenseUrl': 'urn:rights:creator-owned',
                'rightsConfirmed': True,
            }
            background = await call(session, 'asset_register', {
                'path': str(ROOT / 'assets/moving-landscape.mp4'),
                'rights': {**provenance, 'title': 'Original moving landscape', 'sourceUrl': 'urn:fleet:original:procedural-landscape'},
            })
            foreground = await call(session, 'asset_register', {
                'path': str(ROOT / 'assets/dancing-mascot.mov'),
                'rights': {**provenance, 'title': 'Original dancing mascot', 'sourceUrl': 'urn:fleet:original:procedural-dancing-mascot'},
            })
            plan = await call(session, 'render_plan', {'composition': {
                'background': background['id'], 'foreground': foreground['id'],
                'duration': 8.0, 'preset': 'landscape', 'fps': 30,
                'x': 0.65, 'y': 0.58, 'width': 0.4, 'loop': True, 'motion': 'orbit',
            }})
            validated = await call(session, 'render_validate', {'plan_id': plan['planId']})
            assert validated['valid'] and validated['approval']['status'] == 'proposed'
            request = {
                'plan_id': plan['planId'],
                'approval': {'status': 'approved', 'approvedBy': 'Owner-requested original demo', 'planHash': plan['planHash']},
                'idempotency_key': 'owner-original-dance-demo-20261106',
            }
            job = await call(session, 'render_start', request)
            repeated = await call(session, 'render_start', request)
            assert job['jobId'] == repeated['jobId']
            (ROOT / 'submitted.json').write_text(json.dumps({
                'tools': tools, 'skillCount': len(skills), 'requiredSkills': sorted(names & {'code-video','cinetic','raea','raea-bevy','local-voiceover','agent-desktop'}),
                'plan': plan, 'job': job, 'deduplicationVerified': True,
            }, indent=2))
            print('Submitted', job['jobId'], 'with', len(skills), 'canonical skills available', flush=True)
            return job['jobId']


async def finish(job_id):
    async with stdio_client(PARAMETERS) as streams:
        async with ClientSession(*streams) as session:
            await session.initialize()
            started = time.monotonic()
            while time.monotonic() - started < 180:
                job = await call(session, 'job_status', {'job_id': job_id})
                if job['state'] in {'succeeded', 'failed', 'cancelled'}:
                    assert job['state'] == 'succeeded', job
                    result = await call(session, 'job_result', {'job_id': job_id})
                    (ROOT / 'result.json').write_text(json.dumps(result, indent=2))
                    print(json.dumps(result, indent=2))
                    return
                await asyncio.sleep(0.25)
            raise RuntimeError('Demo did not finish within the bounded render deadline')


async def main():
    job = await submit()
    await finish(job)


asyncio.run(main())
