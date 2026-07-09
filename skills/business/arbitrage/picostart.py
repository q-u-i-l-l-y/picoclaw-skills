import sys, subprocess
from pathlib import Path

SKILLS = Path.home() / ".picoclaw" / "skills"

def run(skill):
    script = SKILLS / f"{skill}.py"
    if not script.exists():
        print(f"Unknown skill: {skill}")
        print("Available: deal_validator, upwork_connector, broker_validator, contract_generator, wisdom_layer, credential_manager, sync_nexus")
        return
    subprocess.run(["python3", str(script)])

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: picostart <skill>")
        print("Skills: deal_validator | upwork_connector | broker_validator | contract_generator | wisdom_layer | sync_nexus")
        exit(1)
    run(sys.argv[1])

