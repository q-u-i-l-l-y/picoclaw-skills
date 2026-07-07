#!/usr/bin/env python3
"""
PicoClaw North Star ↔ Revenue Engine Integration v4.0
Location: ~/.picoclaw/agent_core/skills/north_star_revenue_integration.py

Purpose:
  • Embed North Star vision as milestone in revenue engine
  • Revenue engine adopts strategies aligned with North Star
  • Auto-track R&D fund accumulation (30% default)
  • Phase-gate checking: prevent premature R&D spending
  • Strategy adoption with North Star alignment scoring
  • Plain-language routing: "make money" → revenue, "research metamaterials" → R&D gate check

Usage:
  python3 north_star_revenue_integration.py --milestones
  python3 north_star_revenue_integration.py --strategies
  python3 north_star_revenue_integration.py --adopt "<name>" --desc "..." --phase phase_1
  python3 north_star_revenue_integration.py --recommend
  python3 north_star_revenue_integration.py --log-revenue <amount> --source "<source>"
  python3 north_star_revenue_integration.py --check-gate <action>
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

PICOCLAW_ROOT = Path(os.path.expanduser("~/.picoclaw"))
CONFIG_AUTO = PICOCLAW_ROOT / "config.autonomous.json"
REVENUE_LOG = PICOCLAW_ROOT / "memory" / "revenue_log.jsonl"
STRATEGIES_LOG = PICOCLAW_ROOT / "memory" / "north_star_strategies.jsonl"

# 5-Phase Roadmap (IMMUTABLE)
PHASES = {
    "phase_1_revenue_foundation": {
        "name": "Revenue Foundation",
        "goal": "Generate sustainable affiliate income to fund R&D",
        "status": "ACTIVE",
        "exit_criteria": ["Amazon approved", "3 sites", "$500/mo", "auto pipeline"],
        "rd_allocation": 0.30,
        "monthly_target": 500
    },
    "phase_2_investment_pool": {
        "name": "Investment Pool",
        "goal": "Allocate 30% revenue to R&D fund",
        "status": "pending",
        "exit_criteria": ["$5K fund", "suppliers contacted", "patent research"],
        "rd_allocation": 0.30,
        "monthly_target": 0
    },
    "phase_3_prototype_dev": {
        "name": "Prototype Dev",
        "goal": "Build first medical ENDS prototype",
        "status": "pending",
        "exit_criteria": ["Working sensors", "metamaterial validated", "data pipeline"],
        "rd_allocation": 0.40,
        "monthly_target": 0
    },
    "phase_4_mesh_node_pilot": {
        "name": "Mesh Node Pilot",
        "goal": "Deploy first health data mesh node",
        "status": "pending",
        "exit_criteria": ["5-node mesh", "data integrity", "clinical partnership"],
        "rd_allocation": 0.40,
        "monthly_target": 0
    },
    "phase_5_modular_platform": {
        "name": "Modular Platform",
        "goal": "Open-source health mesh platform",
        "status": "pending",
        "exit_criteria": ["50+ contributors", "100+ deployments", "peer review"],
        "rd_allocation": 0.50,
        "monthly_target": 0
    }
}

# 7 Revenue Milestones mapped to North Star
MILESTONES = {
    "m1_affiliate_approval": {
        "name": "Amazon Associates Approval",
        "phase": "phase_1",
        "status": "in_progress",
        "target": "Amazon application approved",
        "north_star_alignment": "Revenue foundation for medical device R&D"
    },
    "m2_content_pipeline": {
        "name": "Content Pipeline Active",
        "phase": "phase_1",
        "status": "in_progress",
        "target": "14+ pieces of content",
        "north_star_alignment": "SEO traffic → affiliate revenue → R&D fund"
    },
    "m3_first_revenue": {
        "name": "First Revenue Event",
        "phase": "phase_1",
        "status": "pending",
        "target": "First affiliate commission",
        "north_star_alignment": "Proof of revenue model; begin R&D allocation"
    },
    "m4_rd_fund_5k": {
        "name": "R&D Fund $5,000",
        "phase": "phase_2",
        "status": "pending",
        "target": "$5,000 accumulated in R&D fund",
        "north_star_alignment": "First major R&D milestone; enables prototype procurement"
    },
    "m5_sensor_prototype": {
        "name": "Sensor Prototype Working",
        "phase": "phase_3",
        "status": "pending",
        "target": "First sensor array reads physiological data",
        "north_star_alignment": "Core medical ENDS device capability proven"
    },
    "m6_mesh_deployed": {
        "name": "5-Node Mesh Deployed",
        "phase": "phase_4",
        "status": "pending",
        "target": "5 nodes exchanging health data",
        "north_star_alignment": "Distributed health data mesh proven"
    },
    "m7_platform_open": {
        "name": "Platform Open Source",
        "phase": "phase_5",
        "status": "pending",
        "target": "GitHub repo public with 50+ contributors",
        "north_star_alignment": "North Star vision realized: modular health mesh for all"
    }
}

class NorthStarRevenueIntegration:
    def __init__(self):
        self.config = self._load_config()
        self.vision = self.config.get("vision", {})
        self.north_star = self.vision.get("north_star", {})
        self.current_phase = self.vision.get("current_phase", "phase_1_revenue_foundation")
        self.rd_fund = self.config.get("revenue", {}).get("rd_fund", {"total": 0.0, "allocation_percent": 30})

    def _load_config(self):
        if CONFIG_AUTO.exists():
            return json.loads(CONFIG_AUTO.read_text())
        return self._create_default_config()

    def _create_default_config(self):
        """Create default config with North Star locked in."""
        return {
            "version": "4.0",
            "vision": {
                "north_star": {
                    "locked": True,
                    "statement": "Working hand in hand beyond revenue generation towards investment and R&D of the medical ENDS device to become a modular health and data mesh node interface system empowered by existing tech with heavy influence from metamaterial interaction.",
                    "tagline": "From Affiliate Income → Medical Device R&D → Metamaterial Health Mesh",
                    "domains": [
                        "Medical ENDS Device — Electronic Nicotine Delivery System repurposed for health monitoring",
                        "Health Data Mesh — Distributed sensor network for physiological data",
                        "Metamaterial Interaction — Novel sensor arrays leveraging metamaterial properties",
                        "Modular Node Interface — Open, extensible hardware/software platform"
                    ]
                },
                "current_phase": "phase_1_revenue_foundation",
                "phase_history": []
            },
            "milestones": MILESTONES,
            "revenue": {
                "rd_fund": {
                    "allocation_percent": 30,
                    "total_accumulated": 0.0,
                    "monthly_allocations": []
                },
                "strategies": [],
                "monthly_revenue": 0.0
            },
            "safety": {
                "protected_paths": [
                    "agent_core/skills/affiliate_automation.py",
                    "agent_core/skills/revenue_mission_control.py",
                    "agent_core/skills/unified_config.py",
                    "agent_core/skills/north_star_agent.py",
                    "agent_core/skills/north_star_revenue_integration.py",
                    "agent_core/skills/self_diagnosis.py",
                    "agent_core/skills/reasoning_loop.py"
                ],
                "layers": {
                    "L1_governance": "vision locked, phase gates enforced",
                    "L2_income_shield": "read-only execution, append-only logs",
                    "L3_sandbox": "24hr burn-in before promotion"
                }
            }
        }

    def _save_config(self):
        backup = CONFIG_AUTO.with_suffix('.json.bak')
        if CONFIG_AUTO.exists():
            backup.write_text(CONFIG_AUTO.read_text())
        CONFIG_AUTO.write_text(json.dumps(self.config, indent=2))

    def get_vision(self):
        return {
            "statement": self.north_star.get("statement", ""),
            "tagline": self.north_star.get("tagline", ""),
            "locked": self.north_star.get("locked", False),
            "current_phase": self.current_phase,
            "phase_name": PHASES.get(self.current_phase, {}).get("name", "Unknown"),
            "domains": self.north_star.get("domains", [])
        }

    def get_milestones(self):
        return {
            "current_phase": self.current_phase,
            "milestones": MILESTONES,
            "completed": [k for k, v in MILESTONES.items() if v["status"] == "completed"],
            "in_progress": [k for k, v in MILESTONES.items() if v["status"] == "in_progress"],
            "pending": [k for k, v in MILESTONES.items() if v["status"] == "pending"]
        }

    def check_gate(self, action: str) -> dict:
        """Check if an action is allowed in current phase."""
        phase_info = PHASES.get(self.current_phase, {})

        # Define gate rules
        blocked_in_phase_1 = ["prototype_purchase", "supplier_contract", "clinical_trial", "mesh_deploy"]
        blocked_in_phase_2 = ["clinical_trial", "mesh_deploy", "open_source"]
        blocked_in_phase_3 = ["mesh_deploy", "open_source"]
        blocked_in_phase_4 = ["open_source"]

        blocked = {
            "phase_1_revenue_foundation": blocked_in_phase_1,
            "phase_2_investment_pool": blocked_in_phase_2,
            "phase_3_prototype_dev": blocked_in_phase_3,
            "phase_4_mesh_node_pilot": blocked_in_phase_4,
            "phase_5_modular_platform": []
        }

        is_blocked = action.lower() in [a.lower() for a in blocked.get(self.current_phase, [])]

        return {
            "action": action,
            "allowed": not is_blocked,
            "current_phase": self.current_phase,
            "phase_name": phase_info.get("name", ""),
            "reason": f"Action '{action}' is blocked in {phase_info.get('name', '')}" if is_blocked else f"Action '{action}' is permitted in current phase",
            "next_phase_unlock": self._get_next_phase()
        }

    def _get_next_phase(self):
        phases = list(PHASES.keys())
        idx = phases.index(self.current_phase) if self.current_phase in phases else -1
        return phases[idx + 1] if idx >= 0 and idx < len(phases) - 1 else None

    def log_revenue(self, amount: float, source: str = "affiliate", metadata: dict = None):
        """Log revenue event and auto-allocate to R&D fund."""
        phase_info = PHASES.get(self.current_phase, {})
        allocation_pct = self.rd_fund.get("allocation_percent", 30)
        rd_amount = amount * (allocation_pct / 100)

        event = {
            "timestamp": datetime.now().isoformat(),
            "amount": amount,
            "source": source,
            "rd_allocation": rd_amount,
            "rd_allocation_percent": allocation_pct,
            "phase": self.current_phase,
            "metadata": metadata or {}
        }

        # Update config
        revenue = self.config.setdefault("revenue", {})
        rd = revenue.setdefault("rd_fund", {"total_accumulated": 0.0, "monthly_allocations": []})
        rd["total_accumulated"] = rd.get("total_accumulated", 0.0) + rd_amount
        rd["monthly_allocations"].append({
            "timestamp": event["timestamp"],
            "amount": rd_amount,
            "source": source
        })
        revenue["monthly_revenue"] = revenue.get("monthly_revenue", 0.0) + amount
        self.config["revenue"] = revenue
        self._save_config()

        # Append to revenue log
        REVENUE_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(REVENUE_LOG, "a") as f:
            f.write(json.dumps(event) + "\n")

        # Check milestone completion
        self._check_milestone_trigger(event)

        return {
            "status": "logged",
            "amount": amount,
            "rd_allocated": rd_amount,
            "rd_total": rd["total_accumulated"],
            "milestone_check": "triggered"
        }

    def _check_milestone_trigger(self, event):
        """Check if revenue event triggers milestone completion."""
        rd_total = self.config.get("revenue", {}).get("rd_fund", {}).get("total_accumulated", 0)

        # m3: First revenue
        if event["amount"] > 0 and MILESTONES["m3_first_revenue"]["status"] == "pending":
            MILESTONES["m3_first_revenue"]["status"] = "completed"
            MILESTONES["m3_first_revenue"]["completed_at"] = datetime.now().isoformat()

        # m4: R&D fund $5K
        if rd_total >= 5000 and MILESTONES["m4_rd_fund_5k"]["status"] == "pending":
            MILESTONES["m4_rd_fund_5k"]["status"] = "completed"
            MILESTONES["m4_rd_fund_5k"]["completed_at"] = datetime.now().isoformat()

        self.config["milestones"] = MILESTONES
        self._save_config()

    def adopt_strategy(self, name: str, description: str, target_phase: str = None, alignment_score: float = None):
        """Adopt a revenue strategy with North Star alignment."""
        if target_phase is None:
            target_phase = self.current_phase

        # Calculate alignment if not provided
        if alignment_score is None:
            alignment_score = self._calculate_alignment(description)

        strategy = {
            "timestamp": datetime.now().isoformat(),
            "name": name,
            "description": description,
            "target_phase": target_phase,
            "alignment_score": alignment_score,
            "status": "active",
            "north_star_aligned": alignment_score >= 0.6
        }

        strategies = self.config.setdefault("revenue", {}).setdefault("strategies", [])
        strategies.append(strategy)
        self.config["revenue"]["strategies"] = strategies
        self._save_config()

        # Log to strategies file
        STRATEGIES_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(STRATEGIES_LOG, "a") as f:
            f.write(json.dumps(strategy) + "\n")

        return {
            "status": "adopted",
            "strategy": name,
            "alignment_score": alignment_score,
            "north_star_aligned": strategy["north_star_aligned"],
            "total_strategies": len(strategies)
        }

    def _calculate_alignment(self, description: str) -> float:
        """Score how well a strategy aligns with North Star vision."""
        keywords = {
            "medical": 0.3, "health": 0.3, "mesh": 0.3, "node": 0.2,
            "metamaterial": 0.4, "sensor": 0.3, "data": 0.2,
            "modular": 0.2, "ENDS": 0.4, "R&D": 0.3, "investment": 0.2,
            "revenue": 0.1, "affiliate": 0.1, "fund": 0.1
        }
        desc_lower = description.lower()
        score = 0.0
        for word, weight in keywords.items():
            if word in desc_lower:
                score += weight
        return min(1.0, score)

    def get_recommendation(self) -> dict:
        """Get phase-aware recommendation."""
        phase_info = PHASES.get(self.current_phase, {})
        rd_total = self.config.get("revenue", {}).get("rd_fund", {}).get("total_accumulated", 0)
        monthly = self.config.get("revenue", {}).get("monthly_revenue", 0)

        recs = {
            "phase": self.current_phase,
            "phase_name": phase_info.get("name", ""),
            "priority_actions": [],
            "north_star_reminder": self.north_star.get("tagline", ""),
            "rd_fund_status": f"${rd_total:.2f} accumulated (${5000 - rd_total:.2f} until Phase 2)" if self.current_phase == "phase_1_revenue_foundation" else f"${rd_total:.2f} accumulated"
        }

        if self.current_phase == "phase_1_revenue_foundation":
            recs["priority_actions"] = [
                "Monitor Amazon Associates approval email",
                "Generate 3 more content pieces (target: 14 total)",
                "Research niche site #2 for diversification",
                f"Current monthly revenue: ${monthly:.2f} / target: ${phase_info.get('monthly_target', 500)}"
            ]
        elif self.current_phase == "phase_2_investment_pool":
            recs["priority_actions"] = [
                "Begin supplier outreach for sensor components",
                "Conduct patent landscape search for health-monitoring ENDS",
                "Research metamaterial sensor components and suppliers",
                "Set up R&D fund accounting and tracking"
            ]
        elif self.current_phase == "phase_3_prototype_dev":
            recs["priority_actions"] = [
                "Build bill of materials for first sensor array",
                "Validate metamaterial interaction with physiological signals",
                "Establish data pipeline from sensors to mesh protocol",
                "Identify clinical advisor"
            ]
        elif self.current_phase == "phase_4_mesh_node_pilot":
            recs["priority_actions"] = [
                "Deploy 5-node mesh on target hardware (OrangePi/Raspberry Pi)",
                "Validate data integrity across mesh nodes",
                "Establish clinical partnership for data validation",
                "Draft quillyos_mesh.py health data extensions"
            ]
        elif self.current_phase == "phase_5_modular_platform":
            recs["priority_actions"] = [
                "Open-source all hardware designs and software",
                "Build contributor onboarding documentation",
                "Submit for peer review in relevant journals",
                "Scale to 100+ deployments"
            ]

        return recs

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--milestones", action="store_true")
    parser.add_argument("--strategies", action="store_true")
    parser.add_argument("--adopt", type=str, help="Adopt strategy name")
    parser.add_argument("--desc", type=str, default="", help="Strategy description")
    parser.add_argument("--phase", type=str, default=None, help="Target phase")
    parser.add_argument("--recommend", action="store_true")
    parser.add_argument("--log-revenue", type=float, help="Log revenue amount")
    parser.add_argument("--source", type=str, default="affiliate", help="Revenue source")
    parser.add_argument("--check-gate", type=str, help="Check if action allowed")
    parser.add_argument("--vision", action="store_true", help="Show North Star vision")
    args = parser.parse_args()

    nsri = NorthStarRevenueIntegration()

    if args.vision:
        print(json.dumps(nsri.get_vision(), indent=2))
    elif args.milestones:
        print(json.dumps(nsri.get_milestones(), indent=2))
    elif args.strategies:
        strategies = nsri.config.get("revenue", {}).get("strategies", [])
        print(json.dumps({"strategies": strategies, "count": len(strategies)}, indent=2))
    elif args.adopt:
        result = nsri.adopt_strategy(args.adopt, args.desc, args.phase)
        print(json.dumps(result, indent=2))
    elif args.recommend:
        print(json.dumps(nsri.get_recommendation(), indent=2))
    elif args.log_revenue is not None:
        result = nsri.log_revenue(args.log_revenue, args.source)
        print(json.dumps(result, indent=2))
    elif args.check_gate:
        print(json.dumps(nsri.check_gate(args.check_gate), indent=2))
    else:
        # Default: full dashboard
        print("\n⭐ NORTH STAR ↔ REVENUE INTEGRATION DASHBOARD")
        print("=" * 60)
        vision = nsri.get_vision()
        print(f"Vision: {vision['tagline']}")
        print(f"Phase:  {vision['phase_name']} ({vision['current_phase']})")
        print(f"Locked: {'✓' if vision['locked'] else '✗'}")
        print(f"\nR&D Fund: ${nsri.config.get('revenue', {}).get('rd_fund', {}).get('total_accumulated', 0):.2f}")
        print(f"Monthly:  ${nsri.config.get('revenue', {}).get('monthly_revenue', 0):.2f}")
        print(f"\nMilestones: {len([m for m in MILESTONES.values() if m['status'] == 'completed'])}/7 completed")
        print(f"Strategies: {len(nsri.config.get('revenue', {}).get('strategies', []))} active")
        rec = nsri.get_recommendation()
        print(f"\n🎯 Priority Actions:")
        for a in rec["priority_actions"]:
            print(f"   • {a}")

if __name__ == "__main__":
    main()
