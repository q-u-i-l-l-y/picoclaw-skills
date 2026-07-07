#!/usr/bin/env python3
"""
PicoClaw v4.0 — Plain-Language Agent Router
Location: ~/.picoclaw/agent_core/skills/agent_router.py

Enables natural language commands:
  picostart agent "make money"              -> revenue engine
  picostart agent "check health"            -> self-diagnosis
  picostart agent "learn from this"         -> reasoning loop
  picostart agent "show vision"           -> North Star
  picostart agent "research metamaterials"  -> R&D gate check
  picostart agent "what phase are we in"    -> milestone status
  picostart agent "log revenue 50"          -> revenue log
  picostart agent "diagnose and learn"      -> self-diagnosis + reasoning

Usage:
  python3 ~/.picoclaw/agent_core/skills/agent_router.py "<goal>"
"""

import os
import sys
import json
import subprocess
from pathlib import Path

PICOCLAW_ROOT = Path(os.path.expanduser("~/.picoclaw"))
SKILLS_DIR = PICOCLAW_ROOT / "agent_core" / "skills"

class AgentRouter:
    def __init__(self):
        self.routes = self._build_routes()

    def _build_routes(self):
        """Map intent keywords to skill commands."""
        return {
            "revenue": {
                "keywords": ["make money", "earn", "revenue", "income", "affiliate", "sales", "commission", "pipeline"],
                "command": ["python3", str(SKILLS_DIR / "north_star_revenue_integration.py")],
                "description": "Revenue engine + North Star dashboard"
            },
            "log_revenue": {
                "keywords": ["log revenue", "record income", "add revenue", "made money", "earned"],
                "command": None,  # handled specially
                "description": "Log revenue event with R&D allocation"
            },
            "health": {
                "keywords": ["health", "diagnose", "status", "check system", "scan", "integrity"],
                "command": ["python3", str(SKILLS_DIR / "self_diagnosis.py"), "--export-brief"],
                "description": "Self-diagnosis engine"
            },
            "learn": {
                "keywords": ["learn", "remember", "insight", "observation", "think"],
                "command": None,  # handled specially
                "description": "Reasoning loop - record learning"
            },
            "reflect": {
                "keywords": ["reflect", "review", "summary", "state", "learnings"],
                "command": ["python3", str(SKILLS_DIR / "reasoning_loop.py"), "--reflect"],
                "description": "Reasoning loop reflection"
            },
            "vision": {
                "keywords": ["vision", "north star", "goal", "mission", "purpose", "direction"],
                "command": ["python3", str(SKILLS_DIR / "north_star_revenue_integration.py"), "--vision"],
                "description": "North Star vision"
            },
            "milestones": {
                "keywords": ["milestone", "phase", "progress", "roadmap", "where are we"],
                "command": ["python3", str(SKILLS_DIR / "north_star_revenue_integration.py"), "--milestones"],
                "description": "Milestone status"
            },
            "recommend": {
                "keywords": ["recommend", "suggest", "what should", "next step", "priority", "action"],
                "command": ["python3", str(SKILLS_DIR / "north_star_revenue_integration.py"), "--recommend"],
                "description": "Phase-aware recommendations"
            },
            "gate_check": {
                "keywords": ["research", "prototype", "supplier", "clinical", "mesh deploy", "open source", "can i"],
                "command": None,  # handled specially
                "description": "R&D phase gate check"
            },
            "adopt": {
                "keywords": ["adopt strategy", "adopt", "strategy", "new niche"],
                "command": None,  # handled specially
                "description": "Adopt revenue strategy"
            },
            "tools": {
                "keywords": ["tools", "skills", "registry", "what can you do", "capabilities"],
                "command": ["python3", "-c", "import json; lt=json.load(open(str(Path.home()/'.picoclaw/config/local_tools.json'))); [print(f\'{n:<25} -> {c.get(\'assigned_to\') or \"unassigned\"}\') for n,c in lt[\'tools\'].items()]"],
                "description": "List local tools"
            },
        }

    def classify(self, goal: str) -> dict:
        """Classify user intent and return route."""
        goal_lower = goal.lower()

        # Check for revenue logging pattern
        import re
        revenue_match = re.search(r'log\s+revenue\s+(\d+(?:\.\d+)?)', goal_lower)
        if revenue_match:
            amount = float(revenue_match.group(1))
            return {
                "intent": "log_revenue",
                "command": ["python3", str(SKILLS_DIR / "north_star_revenue_integration.py"), "--log-revenue", str(amount), "--source", "manual"],
                "description": f"Log revenue ${amount}"
            }

        # Check for gate check pattern
        gate_keywords = ["prototype", "supplier", "clinical", "mesh", "open source", "purchase", "contract"]
        for kw in gate_keywords:
            if kw in goal_lower:
                return {
                    "intent": "gate_check",
                    "command": ["python3", str(SKILLS_DIR / "north_star_revenue_integration.py"), "--check-gate", kw],
                    "description": f"Check if '{kw}' is allowed in current phase"
                }

        # Check for learning pattern
        if goal_lower.startswith(("learn", "remember", "think")):
            insight = goal[goal_lower.find(" ")+1:] if " " in goal else goal
            return {
                "intent": "learn",
                "command": ["python3", str(SKILLS_DIR / "reasoning_loop.py"), "--learn", insight, "--category", "user_input", "--source", "agent_router"],
                "description": "Record learning"
            }

        # Check for adopt strategy pattern
        if "adopt" in goal_lower or "strategy" in goal_lower:
            return {
                "intent": "adopt",
                "command": ["python3", str(SKILLS_DIR / "north_star_revenue_integration.py"), "--adopt", goal, "--desc", "Adopted via agent router", "--phase", "phase_1_revenue_foundation"],
                "description": "Adopt strategy"
            }

        # Standard keyword matching
        best_match = None
        best_score = 0

        for intent, route in self.routes.items():
            if intent in ["log_revenue", "gate_check", "learn", "adopt"]:
                continue
            score = sum(1 for kw in route["keywords"] if kw in goal_lower)
            if score > best_score:
                best_score = score
                best_match = intent

        if best_match and best_score > 0:
            route = self.routes[best_match]
            return {
                "intent": best_match,
                "command": route["command"],
                "description": route["description"]
            }

        # Default: show help
        return {
            "intent": "help",
            "command": None,
            "description": "Show available commands"
        }

    def execute(self, goal: str):
        """Classify and execute the goal."""
        route = self.classify(goal)

        print("\n🎯 AGENT ROUTER")
        print("=" * 50)
        print(f"Goal:    {goal}")
        print(f"Intent:  {route['intent']}")
        print(f"Action:  {route['description']}")
        print("=" * 50)

        if route["intent"] == "help":
            self._show_help()
            return

        if route["command"]:
            print(f"\n▶ Executing: {' '.join(route['command'])}\n")
            result = subprocess.run(route["command"], capture_output=False, text=True)
            return result.returncode

        return 0

    def _show_help(self):
        print("\n📋 AVAILABLE COMMANDS:")
        print("-" * 50)
        for intent, route in self.routes.items():
            print(f"  {intent:<20} -> {route['description']}")
        print("\nExamples:")
        print('  picostart agent "make money"')
        print('  picostart agent "check health"')
        print('  picostart agent "log revenue 150"')
        print('  picostart agent "research metamaterials"')
        print('  picostart agent "what phase are we in"')
        print('  picostart agent "learn affiliate SEO is working"')


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 agent_router.py \"<goal\">")
        print("  Example: python3 agent_router.py \"make money\"")
        sys.exit(1)

    goal = sys.argv[1]
    router = AgentRouter()
    router.execute(goal)


if __name__ == "__main__":
    main()
