# PicoClaw v4.0 — Quick Reference

## Deploy Now (Choose One Method)

### Method A: Git (Best for ongoing sync)
```bash
cd ~/.picoclaw
git init
git remote add origin https://github.com/q-u-i-l-l-y/picoclaw-skills.git
# Copy files, commit, push
```

### Method B: Self-Extracting Script (Fastest one-time)
```bash
# Transfer deploy_picoclaw_v4.py to Termux, then:
python3 deploy_picoclaw_v4.py
```

### Method C: Manual Python Write (Most control)
```bash
# Use python3 -c with open().write() for each file
# See SESSION_HANDOFF_v5.md for details
```

## Verify After Deploy
```bash
python3 ~/.picoclaw/agent_core/skills/self_diagnosis.py
python3 ~/.picoclaw/agent_core/skills/reasoning_loop.py --reflect
python3 ~/.picoclaw/agent_core/skills/north_star_revenue_integration.py
picostart agent "make money"
```

## Key Commands
| Command | Purpose |
|---------|---------|
| `picostart mesh health` | Full system health |
| `picostart agent "<goal>"` | Agentic execution via North Star |
| `picostart revenue` | Revenue dashboard |
| `picostart milestones` | Milestone status |
| `picostart vision` | North Star vision |
| `set -a; source ~/.picoclaw/.env; set +a` | Export API keys |
| `picoclaw status` | Go binary status |

## North Star
> Working hand in hand beyond revenue generation towards investment and R&D of the medical ENDS device to become a modular health and data mesh node interface system empowered by existing tech with heavy influence from metamaterial interaction.

**Phase:** 1 (Revenue Foundation) | **R&D Fund:** $0 / $5,000 | **Milestones:** 0/7 complete
