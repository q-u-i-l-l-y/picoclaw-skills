#!/usr/bin/env python3
"""
PicoClaw v4.0 — picostart Python Hub v5
Enhanced with merge files and ingest commands.

Usage:
  picostart agent "<goal>"              # Plain-language agent
  picostart merge files                 # Merge workspace conflicts
  picostart ingest                      # Pull missing files from GitHub + ingest docs
  picostart ingest docs                 # Ingest local documents
  picostart ingest sync                 # Sync docs from GitHub repo
  picostart revenue                     # Revenue dashboard
  picostart milestones                  # Milestone status
  picostart vision                      # North Star vision
  picostart health                      # System health
  picostart reflect                     # Reasoning loop
  picostart tools                       # List tools
"""

import os
import sys
import json
import subprocess
import urllib.request
from pathlib import Path

PICO = Path.home() / '.picoclaw'
SKILLS = PICO / 'agent_core' / 'skills'
MEMORY = PICO / 'memory'
DOCS = PICO / 'Documents'

# GitHub config
REPO = 'q-u-i-l-l-y/picoclaw-skills'
BRANCH = 'main'
TOKEN = os.environ.get('GITHUB_TOKEN_QUILLYOS_WRITE', '')

HEADERS = {
    'Accept': 'application/vnd.github.v3+json'
}
if TOKEN:
    HEADERS['Authorization'] = 'token ' + TOKEN


def run_skill(skill_name, *args):
    """Run a skill with arguments."""
    skill_path = SKILLS / f"{skill_name}.py"
    if not skill_path.exists():
        print(f"Skill not found: {skill_name}")
        return 1
    cmd = ["python3", str(skill_path)] + list(args)
    return subprocess.run(cmd).returncode


def github_list_files(path=''):
    """List files in GitHub repo directory."""
    url = f'https://api.github.com/repos/{REPO}/contents/{path}?ref={BRANCH}'
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except Exception as e:
        print(f"GitHub API error: {e}")
        return []


def github_download_file(repo_path, local_path):
    """Download a single file from GitHub."""
    url = f'https://raw.githubusercontent.com/{REPO}/{BRANCH}/{repo_path}'
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
        local_path.parent.mkdir(parents=True, exist_ok=True)
        local_path.write_bytes(data)
        return True
    except Exception as e:
        print(f"  ✗ Failed: {repo_path} -> {e}")
        return False


def cmd_merge_files():
    """Merge workspace files into agent_core."""
    print("🔧 MERGE WORKSPACE FILES")
    print("=" * 50)

    merge_script = SKILLS / 'workspace_merge.py'
    if not merge_script.exists():
        print("Downloading workspace_merge.py...")
        github_download_file(
            'agent_core/skills/workspace_merge.py',
            merge_script
        )

    return run_skill('workspace_merge', '--execute')


def cmd_ingest(ingest_type='all'):
    """Ingest: pull missing files from GitHub + ingest documents."""
    print("📥 INGEST")
    print("=" * 50)

    if ingest_type in ('all', 'sync', 'github'):
        print("\n🔄 Checking GitHub for missing files...")

        # Define critical files to check
        critical_files = {
            'agent_core/skills/self_diagnosis.py': SKILLS / 'self_diagnosis.py',
            'agent_core/skills/reasoning_loop.py': SKILLS / 'reasoning_loop.py',
            'agent_core/skills/north_star_revenue_integration.py': SKILLS / 'north_star_revenue_integration.py',
            'agent_core/skills/agent_router.py': SKILLS / 'agent_router.py',
            'agent_core/skills/partner_agent.py': SKILLS / 'partner_agent.py',
            'agent_core/skills/document_ingestor.py': SKILLS / 'document_ingestor.py',
            'agent_core/skills/mcp_bridge_skill.py': SKILLS / 'mcp_bridge_skill.py',
            'picostart_v4.py': PICO / 'picostart_v4.py',
            'git_sync.py': Path.home() / 'git_sync.py',
        }

        pulled = 0
        for repo_path, local_path in critical_files.items():
            if not local_path.exists():
                print(f"  📥 Pulling: {repo_path}")
                if github_download_file(repo_path, local_path):
                    pulled += 1
                    print(f"  ✓ Downloaded: {local_path.name}")
            else:
                print(f"  ✓ Already have: {local_path.name}")

        print(f"\n  Pulled {pulled} missing files from GitHub")

    if ingest_type in ('all', 'docs', 'documents'):
        print("\n📄 Ingesting local documents...")

        ingestor = SKILLS / 'document_ingestor.py'
        if not ingestor.exists():
            print("  Downloading document_ingestor.py...")
            github_download_file(
                'agent_core/skills/document_ingestor.py',
                ingestor
            )

        # Run ingestor
        if ingestor.exists():
            result = subprocess.run(
                ['python3', str(ingestor)],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print("  ✓ Documents ingested")
                if result.stdout:
                    print(result.stdout[:500])
            else:
                print(f"  ⚠️  Ingestor output: {result.stderr[:200]}")
        else:
            print("  ✗ document_ingestor.py not available")

    if ingest_type in ('all', 'sync'):
        print("\n🔄 Syncing documents from GitHub repo...")

        # Check for Documents/ folder in repo
        repo_docs = github_list_files('Documents')
        if repo_docs:
            DOCS.mkdir(parents=True, exist_ok=True)
            pulled_docs = 0
            for item in repo_docs:
                if item.get('type') == 'file':
                    name = item['name']
                    local_doc = DOCS / name
                    if not local_doc.exists():
                        print(f"  📥 Pulling doc: {name}")
                        if github_download_file(f"Documents/{name}", local_doc):
                            pulled_docs += 1
            print(f"  Pulled {pulled_docs} documents from repo")
        else:
            print("  No Documents/ folder in repo")

    print("\n" + "=" * 50)
    print("✅ INGEST COMPLETE")
    print("\nNext: picostart agent 'what documents do I have'")
    return 0


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 0

    command = sys.argv[1]
    args = sys.argv[2:]

    # Agent router (plain language)
    if command == "agent" and args:
        goal = " ".join(args)
        return run_skill("agent_router", goal)

    # Merge workspace files
    if command == "merge" and args and args[0] == "files":
        return cmd_merge_files()

    # Ingest commands
    if command == "ingest":
        ingest_type = args[0] if args else 'all'
        return cmd_ingest(ingest_type)

    # Direct skill commands
    if command == "health":
        return run_skill("self_diagnosis", "--export-brief")

    if command == "revenue":
        return run_skill("north_star_revenue_integration")

    if command == "milestones":
        return run_skill("north_star_revenue_integration", "--milestones")

    if command == "vision":
        return run_skill("north_star_revenue_integration", "--vision")

    if command == "strategies":
        return run_skill("north_star_revenue_integration", "--strategies")

    if command == "recommend":
        return run_skill("north_star_revenue_integration", "--recommend")

    if command == "tools":
        return run_skill("self_diagnosis")

    if command == "config":
        import json
        auto = json.load(open(PICO / "config.autonomous.json"))
        print(json.dumps(auto, indent=2))
        return 0

    if command == "diagnose":
        return run_skill("self_diagnosis", "--export-brief")

    if command == "learn":
        insight = " ".join(args)
        return run_skill("reasoning_loop", "--learn", insight, "--category", "user_input")

    if command == "reflect":
        return run_skill("reasoning_loop", "--reflect")

    if command == "mesh" and args and args[0] == "health":
        return run_skill("self_diagnosis", "--export-brief")

    print(f"Unknown command: {command}")
    print("Run 'picostart' for help")
    return 1


if __name__ == "__main__":
    sys.exit(main())
