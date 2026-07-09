import json
from pathlib import Path
from datetime import datetime

class WisdomLayer:
    def __init__(self):
        self.d = Path.home() / ".picoclaw" / "workspace" / "memory"
        self.wd = Path.home() / ".picoclaw" / "workspace" / "wisdom"
        self.wd.mkdir(parents=True, exist_ok=True)
        self.wf = self.wd / "wisdom.json"
        self.hf = self.d / "deal_history.json"
        self.bf = self.d / "broker_deals.json"
    
    def load_history(self):
        if not self.hf.exists(): return []
        return json.loads(self.hf.read_text())
    
    def load_broker_deals(self):
        if not self.bf.exists(): return []
        return json.loads(self.bf.read_text())
    
    def distill(self):
        history = self.load_history()
        broker = self.load_broker_deals()
        all_deals = history + broker
        
        if not all_deals:
            return self._seed_wisdom()
        
        approved = [d for d in all_deals if d.get("recommendation") == "approve" or d.get("margin", 0) > 100]
        rejected = [d for d in all_deals if d.get("recommendation") == "reject" or d.get("margin", 0) <= 0]
        
        patterns = {
            "avg_margin_approved": sum(d.get("margin", 0) for d in approved) / len(approved) if approved else 0,
            "avg_margin_rejected": sum(d.get("margin", 0) for d in rejected) / len(rejected) if rejected else 0,
            "common_reject_reasons": self._reject_reasons(rejected),
            "high_value_skills": self._skill_frequency(approved),
        }
        
        wisdom = {
            "version": "0.1",
            "distilled_at": datetime.now().isoformat(),
            "total_deals_analyzed": len(all_deals),
            "patterns": patterns,
            "ethical_guardrails": [
                "Never subcontract to provider with reliability < 0.75",
                "Never accept deal with margin_pct > 75% without human review",
                "Always disclose subcontracting to client",
                "Never bid on job with client hires == 0 and budget > 1000",
                "Revenue serves the mission; the mission does not serve revenue"
            ],
            "recommendations": self._generate_recommendations(patterns, approved)
        }
        
        self.wf.write_text(json.dumps(wisdom, indent=2))
        return wisdom
    
    def _seed_wisdom(self):
        return {
            "version": "0.1",
            "distilled_at": datetime.now().isoformat(),
            "total_deals_analyzed": 0,
            "patterns": {},
            "ethical_guardrails": [
                "Never subcontract to provider with reliability < 0.75",
                "Never accept deal with margin_pct > 75% without human review",
                "Always disclose subcontracting to client",
                "Never bid on job with client hires == 0 and budget > 1000",
                "Revenue serves the mission; the mission does not serve revenue"
            ],
            "recommendations": [
                "Seed wisdom: prioritize deals with margin $100-$500",
                "Seed wisdom: avoid clients with 0 hires and >3 open jobs",
                "Seed wisdom: prefer providers with quality > 0.80"
            ]
        }
    
    def _reject_reasons(self, rejected):
        reasons = []
        for d in rejected:
            if d.get("risk", 0) > 0.5: reasons.append("high_risk")
            if d.get("margin", 0) < 50: reasons.append("low_margin")
            if d.get("effort", 40) > 60: reasons.append("high_effort")
        return list(set(reasons))
    
    def _skill_frequency(self, deals):
        skills = {}
        for d in deals:
            for s in d.get("skills", []):
                skills[s] = skills.get(s, 0) + 1
        return sorted(skills.items(), key=lambda x: x[1], reverse=True)[:5]
    
    def _generate_recommendations(self, patterns, approved):
        recs = []
        if patterns.get("avg_margin_approved", 0) > 200:
            recs.append("High-margin pattern detected: prioritize similar deals")
        if "high_risk" in patterns.get("common_reject_reasons", []):
            recs.append("Risk pattern detected: strengthen vetting")
        recs.append("Wisdom accumulates with every deal. Review weekly.")
        return recs
    
    def report(self):
        w = self.distill()
        print("=" * 40)
        print("WISDOM LAYER v" + w["version"])
        print("=" * 40)
        print(f"Deals analyzed: {w['total_deals_analyzed']}")
        print(f"Distilled: {w['distilled_at']}")
        print("\nEthical Guardrails:")
        for g in w["ethical_guardrails"]:
            print(f"  • {g}")
        print("\nRecommendations:")
        for r in w["recommendations"]:
            print(f"  → {r}")
        if w["patterns"]:
            print(f"\nAvg margin (approved): ${w['patterns'].get('avg_margin_approved', 0):.0f}")
            print(f"Top skills: {w['patterns'].get('high_value_skills', [])}")

if __name__ == "__main__":
    wl = WisdomLayer()
    wl.report()

