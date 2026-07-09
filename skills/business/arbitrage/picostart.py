import sys, subprocess
from pathlib import Path

SKILLS = Path.home() / ".picoclaw" / "skills"

def run(skill):
    script = SKILLS / f"{skill}.py"
    if not script.exists():
        print(f"Unknown: {skill}")
        print("Available: deal_validator, upwork_connector, sync_nexus, credential_manager")
        return
    subprocess.run(["python3", str(script)])

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: picostart <skill>")
        exit(1)
    run(sys.argv[1])
