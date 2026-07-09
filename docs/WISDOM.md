# WISDOM LAYER
## QuillyOS Architecture v4.2

The Wisdom Layer is the fourth tier of the knowledge stack:

**Data → Information → Knowledge → Wisdom**

### Definition
Wisdom is the accumulated patterns, decisions, ethical reasoning, and long-term lessons distilled from the knowledge base and the system's operational history.

### Function
- Guides future decisions so the project continuously refines judgment
- Prevents repeated mistakes through pattern recognition
- Enforces ethical guardrails derived from the immutable North Star
- Transforms operational history into strategic advantage

### Source
- Skill: `picoclaw-skills/skills/business/arbitrage/wisdom_layer.py`
- Output: `~/.picoclaw/workspace/wisdom/wisdom.json`
- Canonical: `quillyos-knowledge-base/wisdom/WISDOM.md`

### Integration
- Ingests from `deal_history.json` and `broker_deals.json`
- Feeds into `broker_validator.py` as guardrail parameters
- Updates weekly via `picostart wisdom_layer`

### Ethical Guardrails (Immutable)
1. Never subcontract to provider with reliability < 0.75
2. Never accept deal with margin_pct > 75% without human review
3. Always disclose subcontracting to client
4. Never bid on job with client hires == 0 and budget > 1000
5. Revenue serves the mission; the mission does not serve revenue

### North Star Alignment
Wisdom ensures the ecosystem grows toward health and enduring human benefit rather than merely increasing technical capability or revenue extraction.

