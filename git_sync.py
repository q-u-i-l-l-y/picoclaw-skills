#!/usr/bin/env python3
"""
PicoClaw v4.0 — GitHub Sync Script (ENV-ONLY, no hardcoded secrets)
Usage:
  export GITHUB_TOKEN_QUILLYOS_WRITE=your_token_here
  python3 git_sync.py
"""

import os
import base64
import json
import urllib.request
from pathlib import Path

TOKEN = os.environ.get('GITHUB_TOKEN_QUILLYOS_WRITE')
if not TOKEN:
    print("ERROR: Set GITHUB_TOKEN_QUILLYOS_WRITE environment variable")
    print("  export GITHUB_TOKEN_QUILLYOS_WRITE=ghp_xxxxxxxx")
    exit(1)

REPO = 'q-u-i-l-l-y/picoclaw-skills'
BRANCH = 'main'
AUTHOR = {'name': 'PicoClaw Bot', 'email': 'bot@quillyos.dev'}

PICO = Path.home() / '.picoclaw'
SYNC_MAP = {
    'agent_core/skills/self_diagnosis.py': PICO / 'agent_core/skills/self_diagnosis.py',
    'agent_core/skills/reasoning_loop.py': PICO / 'agent_core/skills/reasoning_loop.py',
    'agent_core/skills/north_star_revenue_integration.py': PICO / 'agent_core/skills/north_star_revenue_integration.py',
    'deploy_picoclaw_v4.py': PICO / 'deploy_picoclaw_v4.py',
}

HEADERS = {
    'Authorization': 'token ' + TOKEN,
    'Accept': 'application/vnd.github.v3+json',
    'Content-Type': 'application/json'
}


def download_file(repo_path, local_path):
    """Download a file from GitHub repo."""
    url = 'https://raw.githubusercontent.com/' + REPO + '/' + BRANCH + '/' + repo_path
    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read()
            local_path.parent.mkdir(parents=True, exist_ok=True)
            local_path.write_bytes(content)
            print("  DOWNLOADED: " + str(local_path))
            return True
    except Exception as e:
        print("  FAIL: " + repo_path + " -> " + str(e))
        return False


def main():
    print("PICOCLAW <- GITHUB PULL")
    print("   Repo: " + REPO)
    print("   Branch: " + BRANCH)
    print("=" * 60)

    success = 0
    failed = 0

    for repo_path, local_path in SYNC_MAP.items():
        if download_file(repo_path, local_path):
            success += 1
        else:
            failed += 1

    print("=" * 60)
    print("Pull complete: " + str(success) + " files, " + str(failed) + " failed")

    if failed == 0:
        print("\nVerify with:")
        print("  python3 ~/.picoclaw/agent_core/skills/self_diagnosis.py")
        print("  python3 ~/.picoclaw/agent_core/skills/reasoning_loop.py --reflect")
        print("  python3 ~/.picoclaw/agent_core/skills/north_star_revenue_integration.py")


if __name__ == '__main__':
    main()
