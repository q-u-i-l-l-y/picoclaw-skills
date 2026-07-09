import json, os
from pathlib import Path
from datetime import datetime

class DealValidator:
    def __init__(self):
        self.d = Path.home() / ".picoclaw" / "workspace" / "memory"
        self.d.mkdir(parents=True, exist_ok=True)
        self.lf = self.d / "upwork_leads.json"
        self.of = self.d / "validated_deals.json"
        self.hf = self.d / "deal_history.json"

    def load(self):
        if not self.lf.exists():
            return self.mock()
        return json.loads(self.lf.read_text())

    def mock(self):
        return [
            {"id": "m1", "title": "Python API Dev", "budget": 500, "hourly": None, "effort_hours": 20, "skills": ["python", "api"], "client_history": {"total_hires": 5, "open_jobs": 2}},
            {"id": "m2", "title": "Data Entry", "budget": 50, "hourly": None, "effort_hours": 5, "skills": ["excel"], "client_history": {"total_hires": 0, "open_jobs": 5}},
            {"id": "m3", "title": "ML Training", "budget": 2000, "hourly": 75, "effort_hours": 40, "skills": ["python", "ml"], "client_history": {"total_hires": 12, "open_jobs": 1}},
        ]

    def score(self, l):
        b = l.get("budget", 0) or 0
        h = l.get("hourly", 0) or 0
        hr = l.get("effort_hours", 40)
        v = b if b > 0 else h * hr
        m = min(v * 0.7, 100)
        e = l.get("effort_hours", 40)
        c = l.get("client_history", {})
        r = 0.0
        if c.get("total_hires", 0) == 0: r += 0.4
        if c.get("open_jobs", 0) > 3: r += 0.3
        if (l.get("budget", 0) or 0) < 100: r += 0.2
        r = min(r, 1.0)
        hb = min(c.get("total_hires", 0) * 2, 20)
        sc = (m * 0.4) + ((100 - min(e, 100)) * 0.2) + ((100 - r * 100) * 0.3) + (hb * 0.1)
        return {
            "lead_id": l.get("id"), "title": l.get("title"),
            "margin": round(m, 2), "effort": e, "risk": round(r, 2),
            "history_bonus": round(hb, 2), "score": round(sc, 2),
            "recommendation": "approve" if sc > 60 else "review" if sc > 40 else "reject",
            "validated_at": datetime.now().isoformat()
        }

    def validate(self):
        ls = self.load()
        rs = sorted([self.score(x) for x in ls], key=lambda x: x["score"], reverse=True)
        self.of.write_text(json.dumps(rs, indent=2))
        h = json.loads(self.hf.read_text()) if self.hf.exists() else []
        h.extend(rs)
        self.hf.write_text(json.dumps(h[-1000:], indent=2))
        return rs

if __name__ == "__main__":
    dv = DealValidator()
    r = dv.validate()
    print(f"Validated {len(r)} leads")
    for x in r:
        print(f"  {x['recommendation'].upper():8} | {x['score']:5.1f} | {x['title']}")
