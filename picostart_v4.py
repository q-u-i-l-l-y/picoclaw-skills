#!/usr/bin/env python3
"""
PicoClaw v4.0 — picostart Python Hub
Replaces/extends the existing picostart command with plain-language support.

Usage:
  picostart agent "make money"              -> revenue engine
  picostart agent "check health"            -> self-diagnosis
  picostart agent "log revenue 150"         -> revenue log
  picostart agent "research metamaterials"  -> R&D gate check
  picostart agent "what phase"              -> milestones
  picostart agent "show vision"           -> North Star
  picostart agent "learn <insight>"       -> reasoning loop
  picostart agent "reflect"               -> reasoning reflection

  picostart mesh health                   -> system health
  picostart revenue                       -> revenue dashboard
  picostart milestones                    -> milestone status
  picostart vision                        -> North Star vision
  picostart tools                         -> tool registry
"""

import os
import sys
import subprocess
from pathlib import Path

PICO = Path.home() / '.picoclaw'
SKILLS = PICO / 'agent_core' / 'skills'

def run_skill(skill_name, *args):
    """Run a skill with arguments."""
    skill_path = SKILLS / f"{skill_name}.py"
    if not skill_path.exists():
        print(f"Skill not found: {skill_name}")
        return 1
    cmd = ["python3", str(skill_path)] + list(args)
    return subprocess.run(cmd).returncode

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

    # Direct skill commands
    if command == "mesh" and args and args[0] == "health":
        return run_skill("self_diagnosis", "--export-brief")

    if command == "revenue":
        if args and args[0] == "pipeline":
            return run_skill("north_star_revenue_integration")
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
        return run_skill("self_diagnosis")  # or direct read

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

    print(f"Unknown command: {command}")
    print("Run 'picostart' for help")
    return 1

if __name__ == "__main__":
    sys.exit(main())
