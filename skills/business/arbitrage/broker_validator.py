import json
from pathlib import Path
from datetime import datetime

class BrokerValidator:
    def __init__(self):
        self.d = Path.home() / ".picoclaw" / "workspace" / "memory"
        self.d.mkdir(parents=True, exist_ok=True)
        self.lf = self.d / "upwork_leads.json"
        self.pf = self.d / "provider_registry.json"
        self.of = self.d / "broker_deals.json"
        
    def load_leads(self):
        if not self.lf.exists(): return []
        return json.loads(self.lf.read_text())
    
    def load_providers(self):
        if not self.pf.exists():
            return self._mock_providers()
        return json.loads(self.pf.read_text())
    
    def _mock_providers(self):
        return [
            {"id": "p1", "name": "Offshore Dev A", "skills": ["python", "api"], "rate_hourly": 15, "quality": 0.85, "reliability": 0.90},
            {"id": "p2", "name": "Boutique Studio B", "skills": ["python", "ml", "api"], "rate_hourly": 45, "quality": 0.95, "reliability": 0.88},
            {"id": "p3", "name": "Data Entry VA", "skills": ["excel", "data"], "rate_hourly": 8, "quality": 0.70, "reliability": 0.75},
        ]
    
    def match_providers(self, lead):
        needed = lead.get("skills", [])
        providers = self.load_providers()
        matches = []
        for p in providers:
            skill_match = sum(1 for s in needed if s in p.get("skills", [])) / max(len(needed), 1)
            if skill_match < 0.5: continue
            hours = lead.get("effort_hours", 40)
            cost = p.get("rate_hourly", 0) * hours
            revenue = lead.get("budget", 0) or (lead.get("hourly", 0) or 0) * hours
            margin = revenue - cost
            margin_pct = (margin / revenue * 100) if revenue > 0 else 0
            matches.append({
                "lead_id": lead.get("id"),
                "lead_title": lead.get("title"),
                "provider_id": p.get("id"),
                "provider_name": p.get("name"),
                "revenue": round(revenue, 2),
                "cost": round(cost, 2),
                "margin": round(margin, 2),
                "margin_pct": round(margin_pct, 2),
                "skill_match": round(skill_match, 2),
                "quality": p.get("quality"),
                "reliability": p.get("reliability"),
                "risk_score": self._risk(lead, p, margin_pct),
                "requires_human": margin > 500 or p.get("reliability", 1) < 0.8 or lead.get("client_history", {}).get("total_hires", 0) < 3,
                "validated_at": datetime.now().isoformat()
            })
        return sorted(matches, key=lambda x: x["margin"], reverse=True)
    
    def _risk(self, lead, provider, margin_pct):
        r = 0.0
        if margin_pct < 20: r += 0.3
        if margin_pct > 70: r += 0.2  # too good to be true
        if provider.get("reliability", 1) < 0.8: r += 0.3
        if lead.get("client_history", {}).get("total_hires", 0) == 0: r += 0.2
        return min(r, 1.0)
    
    def validate_all(self):
        leads = self.load_leads()
        all_deals = []
        for lead in leads:
            deals = self.match_providers(lead)
            all_deals.extend(deals[:3])  # top 3 providers per lead
        all_deals.sort(key=lambda x: x["margin"], reverse=True)
        self.of.write_text(json.dumps(all_deals, indent=2))
        return all_deals
    
    def summary(self):
        deals = self.validate_all()
        auto = [d for d in deals if not d["requires_human"]]
        human = [d for d in deals if d["requires_human"]]
        print(f"Broker deals: {len(deals)}")
        print(f"  Auto-pilot: {len(auto)}")
        print(f"  Human gate: {len(human)}")
        print(f"  Top margin: ${deals[0]['margin'] if deals else 0}")
        for d in deals[:5]:
            gate = "HUMAN" if d["requires_human"] else "AUTO"
            print(f"  [{gate}] ${d['margin']:6.0f} ({d['margin_pct']:4.1f}%) | {d['lead_title'][:30]} → {d['provider_name']}")

if __name__ == "__main__":
    bv = BrokerValidator()
    bv.summary()

