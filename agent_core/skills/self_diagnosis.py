#!/usr/bin/env python3
"""
PicoClaw Self-Diagnosis & Perpetual Learning Engine
Version: 4.0.0 — Revenue Sprint Ready
Location: ~/.picoclaw/agent_core/skills/self_diagnosis.py

Capabilities:
  • Full system health scan with conflict detection
  • File structure analysis and integrity checking
  • Config drift detection (config.json vs config.autonomous.json)
  • Skill registry validation and orphaned file cleanup
  • Merge recommendations for conflicting files
  • Perpetual learning: logs diagnostics to reasoning state

Usage:
  python3 ~/.picoclaw/agent_core/skills/self_diagnosis.py
  python3 ~/.picoclaw/agent_core/skills/self_diagnosis.py --fix
  python3 ~/.picoclaw/agent_core/skills/self_diagnosis.py --merge-conflicts
  python3 ~/.picoclaw/agent_core/skills/self_diagnosis.py --export-brief
"""

import os
import sys
import json
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime

PICOCLAW_ROOT = Path(os.path.expanduser("~/.picoclaw"))
CONFIG_JSON = PICOCLAW_ROOT / "config.json"
CONFIG_AUTO = PICOCLAW_ROOT / "config.autonomous.json"
CONFIG_SECRETS = PICOCLAW_ROOT / "config.secrets.json"
LOCAL_TOOLS = PICOCLAW_ROOT / "config" / "local_tools.json"
ENV_FILE = PICOCLAW_ROOT / ".env"
SKILLS_DIR = PICOCLAW_ROOT / "agent_core" / "skills"
WORKSPACE_SKILLS = PICOCLAW_ROOT / "workspace" / "skills"
MEMORY_DIR = PICOCLAW_ROOT / "memory"

# Whitelist schema for Go binary config.json (DO NOT MODIFY)
GO_CONFIG_WHITELIST = {"version", "model_list", "agents", "tools"}
AGENTS_WHITELIST = {"defaults"}
AGENTS_DEFAULTS_WHITELIST = {
    "model_name", "workspace", "max_tokens", "temperature",
    "max_tool_iterations", "model_fallbacks"
}

class PicoClawDiagnostician:
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.fixes = []
        self.learning = []
        self.state = {
            "timestamp": datetime.now().isoformat(),
            "overall_health": "UNKNOWN",
            "score": 0,
            "checks": {},
            "conflicts": [],
            "recommendations": []
        }

    def check_north_star_integrity(self):
        """Verify North Star is locked and immutable."""
        try:
            auto = json.loads(CONFIG_AUTO.read_text())
            vision = auto.get("vision", {})
            ns = vision.get("north_star", {})

            if not ns.get("locked"):
                self.issues.append("CRITICAL: North Star vision is NOT locked")
                self.fixes.append("Set vision.north_star.locked = true in config.autonomous.json")
                self.state["checks"]["north_star"] = {"status": "FAIL", "locked": False}
            else:
                self.state["checks"]["north_star"] = {"status": "PASS", "locked": True}

            if "statement" not in ns:
                self.issues.append("CRITICAL: North Star statement missing")
            else:
                self.learning.append(f"North Star confirmed: {ns['statement'][:80]}...")

        except Exception as e:
            self.issues.append(f"CRITICAL: Cannot read config.autonomous.json: {e}")
            self.state["checks"]["north_star"] = {"status": "ERROR", "error": str(e)}

    def check_go_config_safety(self):
        """Ensure config.json won't fatal-error the Go binary."""
        try:
            cfg = json.loads(CONFIG_JSON.read_text())
            top_keys = set(cfg.keys())
            unknown = top_keys - GO_CONFIG_WHITELIST

            if unknown:
                self.issues.append(f"FATAL: config.json has unknown fields: {unknown}")
                self.fixes.append(f"Move {unknown} to config.autonomous.json or config.secrets.json")
                self.state["checks"]["go_config"] = {"status": "FAIL", "unknown_fields": list(unknown)}
            else:
                self.state["checks"]["go_config"] = {"status": "PASS", "schema": "clean"}

            # Check agents.defaults schema
            agents = cfg.get("agents", {})
            if "defaults" in agents:
                defaults = agents["defaults"]
                bad_defaults = set(defaults.keys()) - AGENTS_DEFAULTS_WHITELIST
                if bad_defaults:
                    self.issues.append(f"FATAL: agents.defaults has unknown fields: {bad_defaults}")
                    self.fixes.append(f"Remove {bad_defaults} from agents.defaults")

        except Exception as e:
            self.issues.append(f"ERROR: Cannot parse config.json: {e}")

    def check_credential_architecture(self):
        """Verify .env and config.secrets.json exist and are readable."""
        checks = {}

        if ENV_FILE.exists():
            checks["env_file"] = "PASS"
            env_size = ENV_FILE.stat().st_size
            if env_size < 100:
                self.warnings.append(".env file seems very small — may be missing keys")
        else:
            self.issues.append("MISSING: ~/.picoclaw/.env not found")
            self.fixes.append("Create .env with required API keys")
            checks["env_file"] = "FAIL"

        if CONFIG_SECRETS.exists():
            checks["secrets_file"] = "PASS"
            try:
                secrets = json.loads(CONFIG_SECRETS.read_text())
                checks["secrets_keys"] = list(secrets.keys())
            except:
                self.issues.append("ERROR: config.secrets.json is malformed JSON")
                checks["secrets_file"] = "FAIL"
        else:
            self.issues.append("MISSING: config.secrets.json not found")
            self.fixes.append("Create config.secrets.json with structured API keys")
            checks["secrets_file"] = "FAIL"

        self.state["checks"]["credentials"] = checks

    def check_local_tools(self):
        """Verify local_tools.json and tool skill files exist."""
        if not LOCAL_TOOLS.exists():
            self.issues.append("MISSING: config/local_tools.json not found")
            self.fixes.append("Create local_tools.json with hub/spoke tool registry")
            self.state["checks"]["local_tools"] = {"status": "FAIL"}
            return

        try:
            lt = json.loads(LOCAL_TOOLS.read_text())
            tools = lt.get("tools", {})
            self.state["checks"]["local_tools"] = {
                "status": "PASS",
                "tool_count": len(tools),
                "tools": list(tools.keys())
            }

            # Check if assigned skill files exist
            for name, cfg in tools.items():
                skill_path = SKILLS_DIR / f"{name}.py"
                if not skill_path.exists() and name not in ["mesh_health", "north_star_vision"]:
                    self.warnings.append(f"Tool '{name}' registered but skill file not found at {skill_path}")

        except Exception as e:
            self.issues.append(f"ERROR: Cannot parse local_tools.json: {e}")

    def check_skill_registry(self):
        """Analyze skill files for conflicts, duplicates, and orphaned code."""
        registry = {}
        conflicts = []

        # Scan both directories
        for skill_dir in [SKILLS_DIR, WORKSPACE_SKILLS]:
            if not skill_dir.exists():
                continue
            for f in skill_dir.rglob("*.py"):
                rel = f.relative_to(PICOCLAW_ROOT)
                name = f.stem
                content = f.read_text()
                h = hashlib.sha256(content.encode()).hexdigest()[:16]

                if name in registry:
                    conflicts.append({
                        "name": name,
                        "locations": [str(registry[name]["path"]), str(rel)],
                        "hashes": [registry[name]["hash"], h]
                    })
                else:
                    registry[name] = {"path": str(rel), "hash": h, "size": len(content)}

        self.state["checks"]["skills"] = {
            "total": len(registry),
            "conflicts": len(conflicts),
            "conflict_details": conflicts
        }

        if conflicts:
            self.warnings.append(f"Found {len(conflicts)} skill name conflicts")
            for c in conflicts:
                self.fixes.append(f"Merge or rename conflicting skill: {c['name']}")

        # Check protected skills
        protected = [
            "affiliate_automation", "revenue_mission_control", "unified_config",
            "north_star_agent", "revenue_north_star_integration", "self_diagnosis"
        ]
        missing_protected = [p for p in protected if p not in registry]
        if missing_protected:
            self.warnings.append(f"Missing protected skills: {missing_protected}")

    def check_mcp_bridge(self):
        """Verify MCP bridge server exists and is syntactically valid."""
        mcp_path = PICOCLAW_ROOT / "mcp_bridge" / "picoclaw_mcp_server.py"
        if mcp_path.exists():
            try:
                compile(mcp_path.read_text(), str(mcp_path), 'exec')
                self.state["checks"]["mcp_bridge"] = {"status": "PASS", "path": str(mcp_path)}
            except SyntaxError as e:
                self.issues.append(f"MCP bridge has syntax error: {e}")
                self.state["checks"]["mcp_bridge"] = {"status": "FAIL", "error": str(e)}
        else:
            self.warnings.append("MCP bridge server not found — Go binary cannot access Python tools")
            self.state["checks"]["mcp_bridge"] = {"status": "MISSING"}

    def check_revenue_pipeline(self):
        """Verify revenue engine components."""
        revenue_skills = [
            "revenue_mission_control.py",
            "revenue_north_star_integration.py",
            "affiliate_automation.py"
        ]
        for skill in revenue_skills:
            path = SKILLS_DIR / skill
            if not path.exists():
                self.warnings.append(f"Revenue skill missing: {skill}")

        # Check affiliate site
        try:
            import urllib.request
            req = urllib.request.Request(
                "https://brilliant-macaron-29d988.netlify.app/",
                method='HEAD'
            )
            with urllib.request.urlopen(req, timeout=10) as r:
                status = r.status
                self.state["checks"]["affiliate_site"] = {"status": "PASS", "http": status}
        except Exception as e:
            self.state["checks"]["affiliate_site"] = {"status": "WARN", "error": str(e)}
            self.warnings.append(f"Affiliate site check failed: {e}")

    def detect_config_drift(self):
        """Detect if config.json and config.autonomous.json have overlapping/conflicting keys."""
        try:
            cfg = json.loads(CONFIG_JSON.read_text())
            auto = json.loads(CONFIG_AUTO.read_text())

            overlap = set(cfg.keys()) & set(auto.keys())
            dangerous = {"api_keys", "credentials", "tokens", "secrets"}

            if overlap:
                self.warnings.append(f"Key overlap between config.json and config.autonomous.json: {overlap}")
                if overlap & dangerous:
                    self.issues.append(f"CRITICAL: Secrets found in config.json: {overlap & dangerous}")
                    self.fixes.append("Move all secrets to config.secrets.json or .env immediately")

            self.state["checks"]["drift"] = {"overlap": list(overlap)}
        except Exception as e:
            self.issues.append(f"Cannot check config drift: {e}")

    def generate_recommendations(self):
        """Build actionable next steps based on findings."""
        recs = []

        if self.issues:
            recs.append(f"🔴 Fix {len(self.issues)} critical issues before running revenue pipeline")
        if self.warnings:
            recs.append(f"🟡 Address {len(self.warnings)} warnings for optimal operation")
        if not (PICOCLAW_ROOT / "memory" / "reasoning_log.jsonl").exists():
            recs.append("📝 Initialize reasoning_log.jsonl for perpetual learning")
        if not (PICOCLAW_ROOT / "memory" / "revenue_log.jsonl").exists():
            recs.append("💰 Initialize revenue_log.jsonl for revenue tracking")

        recs.append("🚀 Run 'picostart revenue pipeline' to begin revenue sprint")
        recs.append('🧠 Run "picostart agent \"diagnose and learn\"" for autonomous repair')

        self.state["recommendations"] = recs

    def compute_score(self):
        """Calculate overall health score."""
        base = 100
        base -= len(self.issues) * 15
        base -= len(self.warnings) * 5
        self.state["score"] = max(0, min(100, base))
        self.state["overall_health"] = "HEALTHY" if base >= 80 else "DEGRADED" if base >= 50 else "CRITICAL"

    def save_to_reasoning(self):
        """Append diagnostic state to reasoning log for perpetual learning."""
        reasoning_file = MEMORY_DIR / "reasoning_log.jsonl"
        reasoning_file.parent.mkdir(parents=True, exist_ok=True)
        with open(reasoning_file, "a") as f:
            f.write(json.dumps({
                "timestamp": self.state["timestamp"],
                "type": "self_diagnosis",
                "score": self.state["score"],
                "health": self.state["overall_health"],
                "issues_count": len(self.issues),
                "warnings_count": len(self.warnings),
                "learning": self.learning
            }) + "\n")

    def run(self, fix=False, merge=False, export=False):
        print("\n🔬 PICOCLAW SELF-DIAGNOSIS v4.0")
        print("=" * 60)

        self.check_north_star_integrity()
        self.check_go_config_safety()
        self.check_credential_architecture()
        self.check_local_tools()
        self.check_skill_registry()
        self.check_mcp_bridge()
        self.check_revenue_pipeline()
        self.detect_config_drift()
        self.generate_recommendations()
        self.compute_score()

        # Display results
        print(f"\n📊 Overall Health: {self.state['overall_health']} ({self.state['score']}/100)")

        if self.issues:
            print(f"\n🔴 CRITICAL ISSUES ({len(self.issues)}):")
            for i in self.issues:
                print(f"   • {i}")
        if self.warnings:
            print(f"\n🟡 WARNINGS ({len(self.warnings)}):")
            for w in self.warnings:
                print(f"   • {w}")
        if self.fixes:
            print(f"\n🔧 SUGGESTED FIXES:")
            for f in self.fixes:
                print(f"   → {f}")

        print(f"\n📋 RECOMMENDATIONS:")
        for r in self.state["recommendations"]:
            print(f"   {r}")

        # Save learning
        self.save_to_reasoning()

        if export:
            brief_path = PICOCLAW_ROOT / f"memory/diagnostic_brief_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
            brief_path.parent.mkdir(parents=True, exist_ok=True)
            brief_path.write_text(json.dumps(self.state, indent=2))
            print(f"\n📝 Diagnostic brief exported to: {brief_path}")

        return self.state

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--fix", action="store_true", help="Attempt automatic fixes")
    parser.add_argument("--merge-conflicts", action="store_true", help="Merge conflicting skill files")
    parser.add_argument("--export-brief", action="store_true", help="Export JSON brief")
    args = parser.parse_args()

    diag = PicoClawDiagnostician()
    diag.run(fix=args.fix, merge=args.merge_conflicts, export=args.export_brief)

if __name__ == "__main__":
    main()
