import json
from pathlib import Path
from datetime import datetime

class UpworkConnector:
    def __init__(self, c=None):
        self.cp = c or Path.home() / ".picoclaw" / "config.json"
        self.d = Path.home() / ".picoclaw" / "workspace" / "memory"
        self.d.mkdir(parents=True, exist_ok=True)
        self.lf = self.d / "upwork_leads.json"
        self.cr = self._load()

    def _load(self):
        if not self.cp.exists():
            return {}
        try:
            return json.loads(self.cp.read_text()).get("upwork", {})
        except:
            return {}

    def auth(self):
        return bool(self.cr.get("api_key") and self.cr.get("api_secret"))

    def search(self, q="python", cat=None, min_b=100):
        if not self.auth():
            print("UPWORK: No credentials. Mock mode.")
            return self._mock()
        print("UPWORK: Skeleton ready. Implement real API call.")
        return []

    def _mock(self):
        return [
            {"id": "tm1", "title": "Python Automation", "budget": 300, "hourly": None, "effort_hours": 8, "skills": ["python", "automation"], "client_history": {"total_hires": 3, "open_jobs": 1}, "url": "https://mock.upwork/1", "created_at": datetime.now().isoformat()},
            {"id": "tm2", "title": "API Integration", "budget": 800, "hourly": 50, "effort_hours": 20, "skills": ["python", "api", "rest"], "client_history": {"total_hires": 8, "open_jobs": 2}, "url": "https://mock.upwork/2", "created_at": datetime.now().isoformat()},
        ]

    def filter(self, jobs, min_b=100, req=None):
        req = req or ["python"]
        f = []
        for j in jobs:
            b = j.get("budget", 0) or 0
            h = j.get("hourly", 0) or 0
            hr = j.get("effort_hours", 40)
            v = b if b > 0 else h * hr
            if v < min_b:
                continue
            if not any(x in j.get("skills", []) for x in req):
                continue
            f.append(j)
        return f

    def store(self, jobs):
        e = json.loads(self.lf.read_text()) if self.lf.exists() else []
        ids = {x["id"] for x in e}
        n = [x for x in jobs if x["id"] not in ids]
        a = e + n
        self.lf.write_text(json.dumps(a, indent=2))
        return len(n), len(a)

    def run(self, q="python", min_b=100):
        j = self.search(q)
        f = self.filter(j, min_b)
        n, t = self.store(f)
        print(f"UPWORK: {n} new leads stored ({t} total).")

if __name__ == "__main__":
    uc = UpworkConnector()
    uc.run()
