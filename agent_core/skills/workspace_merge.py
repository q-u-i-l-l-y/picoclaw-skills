#!/usr/bin/env python3
"""
PicoClaw v4.0 — Workspace Merge & Cleanup
Location: ~/.picoclaw/agent_core/skills/workspace_merge.py

Merges workspace/skills/ into agent_core/skills/ and resolves conflicts.
Handles the 109 skill name conflicts by deduplicating and archiving.

Usage:
  python3 workspace_merge.py --dry-run     # Preview changes
  python3 workspace_merge.py --execute   # Actually merge
  python3 workspace_merge.py --archive   # Move conflicts to archive/
"""

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime

PICO = Path.home() / '.picoclaw'
AGENT_CORE = PICO / 'agent_core' / 'skills'
WORKSPACE = PICO / 'workspace' / 'skills'
ARCHIVE = PICO / 'archive' / 'skills'
MEMORY = PICO / 'memory'

def get_all_files(directory):
    """Get all .py files in directory recursively."""
    files = {}
    if not directory.exists():
        return files
    for f in directory.rglob('*.py'):
        rel = f.relative_to(directory)
        files[str(rel)] = f
    return files

def analyze_conflicts():
    """Analyze conflicts between agent_core and workspace."""
    agent_files = get_all_files(AGENT_CORE)
    workspace_files = get_all_files(WORKSPACE)

    conflicts = []
    unique_workspace = []
    unique_agent = []

    for name, path in workspace_files.items():
        if name in agent_files:
            conflicts.append({
                'name': name,
                'workspace': str(path),
                'agent_core': str(agent_files[name]),
                'workspace_size': path.stat().st_size,
                'agent_size': agent_files[name].stat().st_size
            })
        else:
            unique_workspace.append({'name': name, 'path': str(path)})

    for name, path in agent_files.items():
        if name not in workspace_files:
            unique_agent.append({'name': name, 'path': str(path)})

    return {
        'conflicts': conflicts,
        'unique_workspace': unique_workspace,
        'unique_agent': unique_agent,
        'total_workspace': len(workspace_files),
        'total_agent': len(agent_files)
    }

def merge_workspace(execute=False):
    """Merge workspace skills into agent_core."""
    analysis = analyze_conflicts()

    print("🔧 WORKSPACE MERGE ANALYSIS")
    print("=" * 60)
    print(f"   Workspace files: {analysis['total_workspace']}")
    print(f"   Agent core files: {analysis['total_agent']}")
    print(f"   Conflicts: {len(analysis['conflicts'])}")
    print(f"   Unique to workspace: {len(analysis['unique_workspace'])}")
    print(f"   Unique to agent_core: {len(analysis['unique_agent'])}")
    print("=" * 60)

    if not execute:
        print("\n⚠️  DRY RUN — No changes made")
        print("   Run with --execute to merge")
        return

    # Create archive directory
    ARCHIVE.mkdir(parents=True, exist_ok=True)

    actions = {
        'merged': 0,
        'archived': 0,
        'skipped': 0,
        'errors': []
    }

    # Handle conflicts: keep agent_core version, archive workspace version
    for conflict in analysis['conflicts']:
        try:
            # Archive the workspace version
            archive_path = ARCHIVE / Path(conflict['name']).name
            shutil.copy2(conflict['workspace'], archive_path)
            actions['archived'] += 1
            print(f"   📦 Archived: {conflict['name']}")
        except Exception as e:
            actions['errors'].append(f"Archive error {conflict['name']}: {e}")

    # Move unique workspace files to agent_core
    for item in analysis['unique_workspace']:
        try:
            dest = AGENT_CORE / Path(item['name']).name
            shutil.copy2(item['path'], dest)
            actions['merged'] += 1
            print(f"   ✅ Merged: {item['name']}")
        except Exception as e:
            actions['errors'].append(f"Merge error {item['name']}: {e}")

    # Log the merge
    log = {
        'timestamp': datetime.now().isoformat(),
        'action': 'workspace_merge',
        'conflicts_resolved': len(analysis['conflicts']),
        'files_merged': actions['merged'],
        'files_archived': actions['archived'],
        'errors': actions['errors']
    }

    log_file = MEMORY / 'workspace_merge_log.jsonl'
    log_file.parent.mkdir(parents=True, exist_ok=True)
    with open(log_file, 'a') as f:
        f.write(json.dumps(log) + '\n')

    print("\n" + "=" * 60)
    print(f"✅ MERGE COMPLETE")
    print(f"   Merged: {actions['merged']}")
    print(f"   Archived: {actions['archived']}")
    print(f"   Errors: {len(actions['errors'])}")

    if actions['errors']:
        print(f"\n   Errors:")
        for e in actions['errors']:
            print(f"      ⚠️  {e}")

    print(f"\n   Next: Run 'picostart agent \"check health\"' to verify")

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nCurrent status:")
        analysis = analyze_conflicts()
        print(f"   Conflicts: {len(analysis['conflicts'])}")
        print(f"   Unique workspace: {len(analysis['unique_workspace'])}")
        return

    cmd = sys.argv[1]

    if cmd == '--dry-run':
        merge_workspace(execute=False)
    elif cmd == '--execute':
        merge_workspace(execute=True)
    elif cmd == '--archive':
        # Just archive all workspace files without merging
        ARCHIVE.mkdir(parents=True, exist_ok=True)
        files = get_all_files(WORKSPACE)
        for name, path in files.items():
            dest = ARCHIVE / Path(name).name
            shutil.copy2(path, dest)
            print(f"   📦 Archived: {name}")
        print(f"\n✅ Archived {len(files)} files to {ARCHIVE}")
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)

if __name__ == '__main__':
    main()
