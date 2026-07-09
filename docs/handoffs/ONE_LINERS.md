# PICOCLAW v4.0 — ONE-LINER REFERENCE SHEET
# Copy-paste ready for Termux and Agent prompts

## ── SYSTEM COMMANDS ──

# Full health check
picostart mesh health

# Self-diagnosis with export
python3 ~/.picoclaw/agent_core/skills/self_diagnosis.py --export-brief

# Reasoning state reflection
python3 ~/.picoclaw/agent_core/skills/reasoning_loop.py --reflect

# Show North Star context
python3 ~/.picoclaw/agent_core/skills/reasoning_loop.py --north-star

# Revenue + North Star dashboard
python3 ~/.picoclaw/agent_core/skills/north_star_revenue_integration.py

# List all local tools (after patch)
picostart tools

## ── AGENTIC EXECUTION ──

# Route through North Star to revenue engine
picostart agent "make money"

# Route through North Star with R&D gate check
picostart agent "research metamaterial sensors"

# Generic goal with full routing
picostart agent "diagnose system and suggest improvements"

## ── REASONING LOOP ──

# Record an observation
python3 ~/.picoclaw/agent_core/skills/reasoning_loop.py \
  --think "Affiliate site traffic dropped 20% this week" \
  --context "weekly_analytics"

# Record a learning
python3 ~/.picoclaw/agent_core/skills/reasoning_loop.py \
  --learn "Tavily search API returns better results than Brave for product reviews" \
  --category "api_performance" \
  --source "experiment"

# Suggest a new skill (auto-stages to workspace/skills/)
python3 ~/.picoclaw/agent_core/skills/reasoning_loop.py \
  --suggest-skill "upwork_proposal_generator" \
  --rationale "We need automated Upwork proposals to diversify revenue beyond affiliate"

## ── REVENUE ENGINE ──

# Log revenue event (auto-allocates 30% to R&D)
python3 ~/.picoclaw/agent_core/skills/north_star_revenue_integration.py \
  --log-revenue 150.00 \
  --source "amazon_affiliate"

# Adopt a strategy with North Star alignment
python3 ~/.picoclaw/agent_core/skills/north_star_revenue_integration.py \
  --adopt "fitness_tracker_niche" \
  --desc "Create affiliate site for fitness trackers with health data angle" \
  --phase phase_1_revenue_foundation

# Check phase gate before action
python3 ~/.picoclaw/agent_core/skills/north_star_revenue_integration.py \
  --check-gate "prototype_purchase"

# Get phase-aware recommendations
python3 ~/.picoclaw/agent_core/skills/north_star_revenue_integration.py --recommend

## ── SELF-DIAGNOSIS ──

# Full scan
python3 ~/.picoclaw/agent_core/skills/self_diagnosis.py

# Attempt auto-fixes
python3 ~/.picoclaw/agent_core/skills/self_diagnosis.py --fix

# Merge conflicting skill files
python3 ~/.picoclaw/agent_core/skills/self_diagnosis.py --merge-conflicts

## ── ENVIRONMENT SETUP ──

# Export all API keys for Go binary
set -a; source ~/.picoclaw/.env; set +a

# Verify Go binary sees keys
picoclaw status

# Quick Claude API call via key manager
python3 ~/.picoclaw/api_key_manager.py call "Summarize our North Star vision"

## ── MESH / CLUSTER ──

# Health check
picostart mesh health

# View tool registry
python3 -c "import json; lt=json.load(open('/data/data/com.termux/files/home/.picoclaw/config/local_tools.json')); [print(f'{n:<25} → {c.get("assigned_to") or "unassigned"}') for n,c in lt['tools'].items()]"

# Add spoke node (for Raspberry Pi cluster)
python3 -c "
import json
from pathlib import Path
lt = json.loads((Path.home() / '.picoclaw/config/local_tools.json').read_text())
lt['spoke_registry']['rpi-node-1'] = {
    'capabilities': ['python3', 'network', 'file_read', 'file_write'],
    'ip': '192.168.1.101',
    'status': 'ready',
    'assigned_tools': []
}
(Path.home() / '.picoclaw/config/local_tools.json').write_text(json.dumps(lt, indent=2))
print('Added rpi-node-1 to spoke registry')
"
