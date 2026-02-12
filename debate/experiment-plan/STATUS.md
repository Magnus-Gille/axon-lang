# AXON Experiment Plan — Resume Guide

## Quick Context
We designed a 6-experiment validation framework for AXON, then ran a 3-round adversarial debate (Claude vs Codex GPT-5.3) to stress-test the methodology. A second 2-round debate on publishability, use cases, and testability further refined the plan.

## Where We Left Off
**Status: Exp 0 (learnability gate) complete — passes on 2/3 models. Week 0 prerequisites done.**

## What Happened

### Week 0 (completed 2026-02-12)
All prerequisites implemented: spec frozen at v0.1-experimental, parser bugs fixed, 3-level validator built, conformance test corpus (54 tests passing), Exp 0 infrastructure operational.

### Exp 0: Learnability Gate (completed 2026-02-12)
Ran 6 conditions x 9 tasks x 3 models (Claude Haiku, Claude Sonnet, GPT-5.3 Codex). CLI-based runner using existing subscriptions — zero API cost. See `experiments/exp0_learnability/RESULTS.md` for full analysis.

**Gate result**: PASS on Sonnet (89%) and GPT-5.3 (100%), FAIL on Haiku (78%). AXON matches JSON FC compliance on every model — the relative criterion is met everywhere. Only the absolute 80% threshold blocks Haiku.

**Key findings**: (1) AXON is not uniquely hard — JSON FC fails at equal rates; (2) AXON beats FIPA-ACL on Sonnet (89% vs 78%); (3) prompt engineering improved Haiku by 22pp; (4) AXON is 30% more compact than JSON FC; (5) all "failures" are semantically correct but syntactically strict.

## What to Do Next

### Immediate
1. **Decide gate disposition**: Exp 0 passes on 2/3 models. Proceed with larger models only, or iterate prompt/parser for small-model support?
2. **Run 3x replications**: Current results are single-run. Preregistration requires 3 runs per cell for variance estimation.
3. **Consider parser relaxation**: Two error classes (`ident{record}`, `&` in routing) are reasonable syntax the parser could accept.

### Next experiments
After gate disposition is decided, Exp 1 (Token Efficiency) and Exp 3 (Compositionality) are co-primary and should run next.

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
| 0 | Learnability | Gate (must pass first) | **PASS** (2/3 models, preliminary 1-run) |
| 1 | Token Efficiency | Co-primary | Not started |
| 2 | Agent Debate | Applied evaluation | Not started |
| 3 | Coordination | Co-primary | Not started |
| 4 | Roundtrip Fidelity | Secondary | Not started |
| 5 | Scaling | Secondary | Not started |
