#!/usr/bin/env python3
import os
import pathlib
import subprocess
import sys

os.umask(0o077)
binary = '/Users/sarthak/.local/share/codevetter-agent-cli/21b73b4dac6f8653397e59d8836db02c0b818939-release/bin/codevetter'
result = subprocess.run([binary, *sys.argv[1:]], capture_output=True)
pathlib.Path(__file__).with_suffix('.stderr').write_bytes(result.stderr)
sys.stdout.buffer.write(result.stdout)
sys.stderr.buffer.write(result.stderr)
sys.exit(result.returncode)
