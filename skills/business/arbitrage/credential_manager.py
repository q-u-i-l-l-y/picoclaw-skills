import json, os, stat
from pathlib import Path

class CredManager:
    def __init__(self):
        self.f = Path.home() / ".picoclaw" / "config.json"
        self.f.parent.mkdir(parents=True, exist_ok=True)

    def init(self):
        if self.f.exists():
            print(f"Config exists at {self.f}")
            return
        t = {
            "upwork": {"api_key": "", "api_secret": "", "user_id": ""},
            "stripe": {"api_key": "", "webhook_secret": ""},
            "freelancer": {"api_key": ""},
            "mls": {"api_key": ""},
            "github": {"token_write": ""},
            "rate_limits": {
                "upwork": {"rph": 100, "batch": 10},
                "freelancer": {"rph": 50, "batch": 5}
            },
            "cache": {"ttl": 3600, "max_mb": 50, "dir": "~/.picoclaw/cache"}
        }
        self.f.write_text(json.dumps(t, indent=2))
        os.chmod(self.f, 0o600)
        print(f"Created {self.f} (chmod 600). NEVER COMMIT THIS.")

    def load(self):
        if not self.f.exists():
            self.init()
        return json.loads(self.f.read_text())

    def get(self, svc, key=None):
        c = self.load()
        x = c.get(svc, {})
        return x if key is None else x.get(key)

    def set(self, svc, key, val):
        c = self.load()
        c.setdefault(svc, {})[key] = val
        self.f.write_text(json.dumps(c, indent=2))
        os.chmod(self.f, 0o600)
        print(f"Updated {svc}.{key}")

if __name__ == "__main__":
    CredManager().init()
