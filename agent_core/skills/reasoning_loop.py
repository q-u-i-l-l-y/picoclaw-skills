#!/usr/bin/env python3
"""
PicoClaw Reasoning & Skill Learning Loop v4.0
Location: ~/.picoclaw/agent_core/skills/reasoning_loop.py

Purpose:
  • Read/write reasoning state to config.autonomous.json
  • Accumulate learnings across sessions (perpetual learning)
  • Self-diagnose and propose skill improvements
  • Feed insights into revenue engine and North Star milestones
  • Enable agentic self-improvement with minimal human input

Authorized Keys (read/write):
  reasoning.inference_state
  reasoning.learnings
  reasoning.session_log
  reasoning.skill_suggestions
  reasoning.performance_metrics

Forbidden Keys (read-only):
  vision.north_star
  milestones
  safety.protected_paths
  revenue.rd_fund

Usage:
  python3 ~/.picoclaw/agent_core/skills/reasoning_loop.py --think "<observation>"
  python3 ~/.picoclaw/agent_core/skills/reasoning_loop.py --learn "<insight>"
  python3 ~/.picoclaw/agent_core/skills/reasoning_loop.py --suggest-skill "<description>"
  python3 ~/.picoclaw/agent_core/skills/reasoning_loop.py --reflect
  python3 ~/.picoclaw/agent_core/skills/reasoning_loop.py --export-state
"""

import os
import sys
import json
import time
import hashlib
from pathlib import Path
from datetime import datetime

PICOCLAW_ROOT = Path(os.path.expanduser("~/.picoclaw"))
CONFIG_AUTO = PICOCLAW_ROOT / "config.autonomous.json"
MEMORY_DIR = PICOCLAW_ROOT / "memory"
REASONING_LOG = MEMORY_DIR / "reasoning_log.jsonl"
SKILL_SUGGESTIONS = MEMORY_DIR / "skill_suggestions.jsonl"

# Keys the reasoning agent CAN modify
READWRITE_KEYS = {
    "reasoning.inference_state",
    "reasoning.learnings",
    "reasoning.session_log",
    "reasoning.skill_suggestions",
    "reasoning.performance_metrics",
    "reasoning.last_reflection",
    "reasoning.confidence_scores",
}

# Keys that are IMMUTABLE (read-only, any modification rejected)
FORBIDDEN_KEYS = {
    "vision.north_star.statement",
    "vision.north_star.locked",
    "vision.north_star.tagline",
    "milestones",
    "safety.protected_paths",
    "safety.layers",
    "revenue.rd_fund.allocation_percent",
    "revenue.rd_fund.total_accumulated",
}

class ReasoningLoop:
    def __init__(self):
        self.config = self._load_config()
        self.reasoning = self.config.get("reasoning", {})

    def _load_config(self):
        if CONFIG_AUTO.exists():
            return json.loads(CONFIG_AUTO.read_text())
        return {"reasoning": {}}

    def _save_config(self):
        """Write config back to disk with atomic backup."""
        # Backup existing
        if CONFIG_AUTO.exists():
            backup = CONFIG_AUTO.with_suffix('.json.bak')
            backup.write_text(CONFIG_AUTO.read_text())
        CONFIG_AUTO.write_text(json.dumps(self.config, indent=2))

    def _validate_path(self, key_path: str) -> bool:
        """Check if a dot-notation path is allowed for writing."""
        # Check against forbidden prefixes
        for forbidden in FORBIDDEN_KEYS:
            if key_path.startswith(forbidden) or forbidden.startswith(key_path):
                return False
        return any(key_path.startswith(allowed) or allowed.startswith(key_path) 
                   for allowed in READWRITE_KEYS)

    def _get_nested(self, obj, path: str):
        """Get value at dot-notation path."""
        keys = path.split('.')
        for k in keys:
            if isinstance(obj, dict) and k in obj:
                obj = obj[k]
            else:
                return None
        return obj

    def _set_nested(self, obj, path: str, value):
        """Set value at dot-notation path, creating intermediates."""
        keys = path.split('.')
        for k in keys[:-1]:
            if k not in obj:
                obj[k] = {}
            obj = obj[k]
        obj[keys[-1]] = value

    def think(self, observation: str, context: str = ""):
        """Record an observation into inference state."""
        if not self._validate_path("reasoning.inference_state"):
            return {"error": "Forbidden: cannot write to inference_state"}

        entry = {
            "timestamp": datetime.now().isoformat(),
            "observation": observation,
            "context": context,
            "confidence": 0.7,
            "type": "inference"
        }

        state = self.reasoning.get("inference_state", [])
        state.append(entry)
        # Keep last 100 entries
        self.reasoning["inference_state"] = state[-100:]
        self.config["reasoning"] = self.reasoning
        self._save_config()

        # Also append to reasoning log
        REASONING_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(REASONING_LOG, "a") as f:
            f.write(json.dumps(entry) + "\n")

        return {"status": "recorded", "inference_count": len(state)}

    def learn(self, insight: str, category: str = "general", source: str = "user"):
        """Record a learning/insight for perpetual accumulation."""
        if not self._validate_path("reasoning.learnings"):
            return {"error": "Forbidden: cannot write to learnings"}

        entry = {
            "timestamp": datetime.now().isoformat(),
            "insight": insight,
            "category": category,
            "source": source,
            "hash": hashlib.sha256(insight.encode()).hexdigest()[:12]
        }

        learnings = self.reasoning.get("learnings", [])
        learnings.append(entry)
        self.reasoning["learnings"] = learnings
        self.config["reasoning"] = self.reasoning
        self._save_config()

        # Log it
        with open(REASONING_LOG, "a") as f:
            f.write(json.dumps({**entry, "type": "learning"}) + "\n")

        return {"status": "learned", "total_learnings": len(learnings)}

    def suggest_skill(self, description: str, rationale: str = "", auto_stage: bool = True):
        """Suggest a new skill based on observed need."""
        if not self._validate_path("reasoning.skill_suggestions"):
            return {"error": "Forbidden: cannot write to skill_suggestions"}

        suggestion = {
            "timestamp": datetime.now().isoformat(),
            "description": description,
            "rationale": rationale,
            "status": "proposed",
            "auto_stage": auto_stage
        }

        suggestions = self.reasoning.get("skill_suggestions", [])
        suggestions.append(suggestion)
        self.reasoning["skill_suggestions"] = suggestions
        self.config["reasoning"] = self.reasoning
        self._save_config()

        # Also write to staging file for review
        SKILL_SUGGESTIONS.parent.mkdir(parents=True, exist_ok=True)
        with open(SKILL_SUGGESTIONS, "a") as f:
            f.write(json.dumps(suggestion) + "\n")

        # If auto_stage, create a stub in workspace/skills/
        if auto_stage:
            skill_name = description.lower().replace(' ', '_').replace('-', '_')[:30]
            stub_path = PICOCLAW_ROOT / "workspace" / "skills" / f"{skill_name}.py"
            stub_path.parent.mkdir(parents=True, exist_ok=True)
            stub = f'''#!/usr/bin/env python3
            """
            [STAGED] {description}
            Rationale: {rationale}
            Suggested: {datetime.now().isoformat()}
            Status: AWAITING REVIEW - 24hr burn-in before promotion to agent_core/skills/
            """
            # TODO: Implement skill logic
            # TODO: Add to config/local_tools.json if tool-worthy
            # TODO: Run self_diagnosis.py --merge-conflicts after promotion

            def main():
                print(f"[STAGED SKILL] {description}")
                print("This skill has been auto-staged by the reasoning loop.")
                print("Review, implement, and promote to agent_core/skills/ after validation.")

            if __name__ == "__main__":
                main()
            '''
            stub_path.write_text(stub)
            suggestion["stub_path"] = str(stub_path)

        return {"status": "suggested", "skill_name": skill_name if auto_stage else None, 
                "total_suggestions": len(suggestions)}

    def reflect(self):
        """Generate a reflection on accumulated learnings and state."""
        learnings = self.reasoning.get("learnings", [])
        inferences = self.reasoning.get("inference_state", [])
        suggestions = self.reasoning.get("skill_suggestions", [])

        reflection = {
            "timestamp": datetime.now().isoformat(),
            "total_learnings": len(learnings),
            "total_inferences": len(inferences),
            "total_suggestions": len(suggestions),
            "pending_suggestions": [s for s in suggestions if s.get("status") == "proposed"],
            "categories": {}
        }

        # Categorize learnings
        for l in learnings:
            cat = l.get("category", "general")
            reflection["categories"][cat] = reflection["categories"].get(cat, 0) + 1

        self.reasoning["last_reflection"] = reflection
        self.config["reasoning"] = self.reasoning
        self._save_config()

        return reflection

    def export_state(self):
        """Export full reasoning state as JSON."""
        return {
            "timestamp": datetime.now().isoformat(),
            "reasoning": self.reasoning,
            "authorized_keys": list(READWRITE_KEYS),
            "forbidden_keys": list(FORBIDDEN_KEYS)
        }

    def get_north_star_context(self):
        """Read North Star for reasoning context (read-only)."""
        vision = self.config.get("vision", {})
        ns = vision.get("north_star", {})
        phase = vision.get("current_phase", "unknown")
        milestones = self.config.get("milestones", {})

        return {
            "vision": ns.get("statement", ""),
            "phase": phase,
            "locked": ns.get("locked", False),
            "milestones_summary": {
                k: v.get("status", "unknown") 
                for k, v in milestones.items()
            }
        }

def main():
    import argparse
    parser = argparse.ArgumentParser(description="PicoClaw Reasoning Loop")
    parser.add_argument("--think", type=str, help="Record an observation")
    parser.add_argument("--context", type=str, default="", help="Context for observation")
    parser.add_argument("--learn", type=str, help="Record a learning/insight")
    parser.add_argument("--category", type=str, default="general", help="Learning category")
    parser.add_argument("--source", type=str, default="user", help="Learning source")
    parser.add_argument("--suggest-skill", type=str, help="Suggest a new skill")
    parser.add_argument("--rationale", type=str, default="", help="Rationale for skill suggestion")
    parser.add_argument("--no-auto-stage", action="store_true", help="Don't auto-stage skill stub")
    parser.add_argument("--reflect", action="store_true", help="Generate reflection")
    parser.add_argument("--export-state", action="store_true", help="Export reasoning state")
    parser.add_argument("--north-star", action="store_true", help="Show North Star context")
    args = parser.parse_args()

    loop = ReasoningLoop()

    if args.think:
        result = loop.think(args.think, args.context)
        print(json.dumps(result, indent=2))
    elif args.learn:
        result = loop.learn(args.learn, args.category, args.source)
        print(json.dumps(result, indent=2))
    elif args.suggest_skill:
        result = loop.suggest_skill(args.suggest_skill, args.rationale, not args.no_auto_stage)
        print(json.dumps(result, indent=2))
    elif args.reflect:
        result = loop.reflect()
        print(json.dumps(result, indent=2))
    elif args.export_state:
        result = loop.export_state()
        print(json.dumps(result, indent=2))
    elif args.north_star:
        result = loop.get_north_star_context()
        print(json.dumps(result, indent=2))
    else:
        # Default: show summary
        reflection = loop.reflect()
        print("\n🧠 PICOCLAW REASONING LOOP STATE")
        print("=" * 50)
        print(f"Learnings:      {reflection['total_learnings']}")
        print(f"Inferences:     {reflection['total_inferences']}")
        print(f"Suggestions:    {reflection['total_suggestions']}")
        print(f"Pending:        {len(reflection['pending_suggestions'])}")
        if reflection['categories']:
            print(f"\nCategories:")
            for cat, count in reflection['categories'].items():
                print(f"  • {cat}: {count}")
        print(f"\nLast reflection: {reflection['timestamp']}")

if __name__ == "__main__":
    main()
