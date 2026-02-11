# AXON Experiment Plan — Resume Guide

## Quick Context
We designed a 6-experiment validation framework for AXON, then ran a 3-round adversarial debate (Claude vs Codex GPT-5.3) to stress-test the methodology. The plan is now debate-hardened and ready for implementation.

## Where We Left Off
**Status: Plan complete, implementation not started.**

## What to Do Next
Start implementing the experiment infrastructure. Begin with Week 0 prerequisites:

1. **Freeze the spec** — resolve metadata inconsistencies in `spec/SPECIFICATION.md` (grammar-level `meta_key` vs profile-level `txn_id`/`txn_state`), tag as `v0.1-experimental`
2. **Build conformance checker** — extend `src/axon_parser.py` with Level 2 (tier compliance) validation
3. **Set up `experiments/` directory** — see the plan for full directory structure
4. **Build shared libraries** — `token_counter.py`, `api_client.py`, `axon_validator.py`, `judge.py`, `conversation.py`, `stats.py`

## Key Files
- **Full plan:** Read the plan file (ask Claude to show it)
- **Debate transcript:** `debate/experiment-plan/` (6 files: proposal, critique, response-1, rebuttal-1, response-2, final-verdict)
- **Debate summary:** `debate/experiment-plan/summary.md`
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
