# AXON Experiment Plan — Resume Guide

## Quick Context
We designed a 6-experiment validation framework for AXON, then ran a 3-round adversarial debate (Claude vs Codex GPT-5.3) to stress-test the methodology. A second 2-round debate on publishability, use cases, and testability further refined the plan.

## Where We Left Off
**Status: Plan complete, implementation not started. Publishability and methodology debates complete — two research tracks clarified.**

## What to Do Next

### Critical path (from publishability debate)
The single most important step is to **build and freeze a preregistered, executable evaluation harness** that enforces semantic conformance and defines fairness constraints for all baselines — before running any experiments.

### Week 0 prerequisites (updated)

1. **Extend `validate()` beyond parse-only** — enforce tier compliance, performative transition rules, and metadata requirements. Current `validate()` (`src/axon_parser.py:803-809`) only checks syntax. Semantic claims require semantic validation.
2. **Freeze the spec** — resolve metadata inconsistencies (`meta_key` vs profile-level keys), tag as `v0.1-experimental`
3. **Define fairness constraints for all 5 conditions** — including symmetric FIPA-ACL adaptation budget (prompt/training budget fixed across conditions)
4. **Preregister endpoints** — primary: task success + token efficiency; secondary: niche benefits (auditability, composability, formal verifiability). Niche benefits must be preregistered, not added post-hoc.
5. **Operationalize "naturalness"** — define concrete metrics: error classes, recovery latency, schema-violation rates
6. **Set up `experiments/` directory** and build shared libraries (`token_counter.py`, `api_client.py`, `axon_validator.py`, `judge.py`, `conversation.py`, `stats.py`)

### Publishability constraints (debate-hardened)
- No numeric venue probability estimates — publication is conditional on completed experiments
- Token efficiency data (66% from 8 examples) is illustrative only, not evidential
- FIPA-ACL baseline is required, not optional
- Interop claims scoped to tested model pairs only

### Research Track B: Adversarial Methodology Paper

A separate 2-round debate established that the Claude↔Codex debate process itself is publishable as a **registered pilot + prospective protocol paper**. See `debate/methodology-summary.md` for full details.

**Publishability checklist (6 items, all required):**
1. Preregistered protocol — primary endpoints, stopping rules, analysis hierarchy
2. Frozen artifact snapshots — all review conditions run against same version, order randomized
3. Blinded multi-rater adjudication — not just project author; inter-rater reliability reported
4. Narrow scope claims — "Claude-authored artifacts reviewed by Codex in this project"
5. Drop human-comparison claims unless calibration arm included
6. Separate exploratory (retrospective 115 points) from confirmatory (prospective under protocol)

**Practical changes to all future debates:**
- Structured per-point metadata: ID, classification (valid/partial/invalid), impact, severity
- Self-review ablation: Claude critiques its own draft before Codex sees it
- Cost logging: tokens, API dollars, wall-clock time per invocation
- Artifact snapshots: freeze before any review condition

## Key Files
- **Full plan:** Read the plan file (ask Claude to show it)
- **Experiment debate:** `debate/experiment-plan/` (6 files + summary)
- **Publishability debate:** `debate/publishability-*.md` (4 files + summary)
- **Methodology debate:** `debate/methodology-*.md` (4 files + summary)
- **AXON parser:** `src/axon_parser.py`
- **AXON spec:** `spec/SPECIFICATION.md`

## Experiment Overview
| # | Name | Role | Status |
|---|------|------|--------|
| 0 | Learnability | Gate (must pass first) | Not started |
| 1 | Token Efficiency | Co-primary | Not started |
| 2 | Agent Debate | Applied evaluation | Not started |
| 3 | Coordination | Co-primary | Not started |
| 4 | Roundtrip Fidelity | Secondary | Not started |
| 5 | Scaling | Secondary | Not started |
