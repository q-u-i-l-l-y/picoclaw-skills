# PICOCLAW // SKILLS
## Skill Repository for the QuillyOS Ecosystem
### Status: Living Document | Version 4.1

---

## PURPOSE

This repository contains the skills — packaged capabilities — that power the
QuillyOS ecosystem.

Every skill contains:
- `SKILL.md` — Specification and documentation
- `examples/` — Usage examples
- `tests/` — Test cases
- `manifest.json` — Machine-readable metadata

---

## STRUCTURE

```
picoclaw-skills/
├── skills/
│   ├── business/           — Business and revenue skills
│   ├── affiliate/          — Affiliate marketing skills
│   ├── arbitrage/          — Service arbitrage skills
│   ├── real_estate/        — Real estate wholesale skills
│   ├── freelance/          — Freelance network skills
│   ├── gumroad/            — Digital product skills
│   ├── coding/             — Software development skills
│   ├── termux/             — Termux environment skills
│   ├── raspberrypi/        — Raspberry Pi skills
│   ├── ollama/             — Ollama model management skills
│   ├── qwen/               — Qwen model skills
│   ├── telegram/           — Telegram bot skills
│   ├── crawler/            — Web crawling skills
│   ├── summarizer/         — Content summarization skills
│   ├── reasoner/           — Reasoning and inference skills
│   ├── planner/            — Task planning skills
│   ├── researcher/         — Research coordination skills
│   ├── writer/             — Content generation skills
│   ├── hardware/           — Hardware integration skills
│   ├── medical/            — Health mapping skills
│   ├── quantum/            — Quantum communication skills
│   ├── metamaterials/      — Metamaterials research skills
│   └── ethics/             — Ethics review skills
├── manifests/              — Skill registry manifests
└── docs/                   — Documentation
```

---

## PROGRESSIVE CAPABILITY

Skills are designed to scale across all compute tiers:

```
phone → Termux → PicoClaw → Raspberry Pi → clusters → future compute
```

The same skill manifest runs on all tiers. Capability increases. Protocol remains identical.

---

## SKILL MANIFEST

The master skill registry lives at `manifests/master.json`.

It tracks:
- **deployed** — Skills ready for execution
- **pending_credentials** — Skills awaiting API keys or tokens
- **not_built** — Skills specified but not yet implemented

---

## HEALTH-CENTRIC DESIGN

Skills are organized around health as the central pursuit:

- `skills/medical/` — Health mapping, biometric ingestion, predictive modeling
- `skills/metamaterials/` — Novel sensing for health monitoring
- `skills/quantum/` — Future health data interfaces
- `skills/business/` — Revenue generation to fund health research

---

*Generated: 2026-07-09*
*Canonical at: picoclaw-skills/README.md*
