import json, urllib.request
from pathlib import Path

cfg = json.loads((Path.home() / ".picoclaw" / "config.json").read_text())
token = cfg.get("github", {}).get("token_write", "")
if not token: print("No token"); exit(1)

headers = {"Authorization": f"token {token}"}
repos = ["quillyos-foundation", "quillyos-nexus", "quillyos-knowledge-base",
         "picoclaw-skills", "picoclaw-dev", "quillyos-n8n", "quillyos-roadmap"]

for repo in repos:
    url = f"https://raw.githubusercontent.com/q-u-i-l-l-y/{repo}/main/nexus_matrix.json"
    out = Path.home() / ".picoclaw" / f"{repo}_matrix.json"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as r:
            out.write_bytes(r.read())
        print(f"OK  {repo}")
    except Exception as e:
        print(f"ERR {repo}: {e}")
