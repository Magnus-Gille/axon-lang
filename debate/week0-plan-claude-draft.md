# Week 0 Prerequisites — Implementation Plan (Debate Draft)

*Snapshot of artifact under review. Source: `/Users/magnus/.claude/plans/valiant-chasing-falcon.md`*

## Context
The AXON project has 6 experiments designed but none started. Week 0 must complete first: freeze the spec, build a real validator, document fairness constraints, and scaffold the experiments directory. Without this, Experiment 0 (the learnability gate) cannot run.

## Implementation Order

### Phase 1: Freeze the Spec
**File:** `spec/SPECIFICATION.md`

1. **Fix metadata key inconsistency** — The EBNF restricts `meta_key` to a closed set, but profiles (Appendix B) use `txn_id`/`txn_state` and the parser accepts any identifier. Resolution: make grammar open-ended (`meta_key = core_meta_key | identifier`) and add prose clarifying that profiles extend the key namespace.

2. **Add version header** — Mark as `v0.1-experimental` with date at top of spec.

3. **Git tag** — Tag the commit as `v0.1-experimental`.

> **Not in scope:** The 12 known parser bugs are grammar-parser mismatches, not runtime errors. Fixing them would change what "valid AXON" means, conflicting with freezing. They'll be triaged separately after Exp 0.

---

### Phase 2: Build the Validator
**New file:** `src/axon_validator.py` (~300 lines)
**New file:** `tests/test_validator.py` (~200 lines)

A 3-level conformance checker, separate from the parser (preserves the parser's stdlib-only, no-deps property):

- **Level 1 — Syntactic:** Wraps `parse()`. Already done by the parser.
- **Level 2 — Tier compliance:** Checks metadata fields against tier requirements:
  - Tier 1: `id`, `%%`
  - Tier 2: adds `re`, `ts`, `ctx`
  - Tier 3: adds `sig`, `authz`, `tenant`, `err_ns`
- **Level 3 — Semantic (reported, not gating):**
  - Performative transition rules (CFM/DNY only to truth-apt, ACC/REJ only to proposals)
  - Unit category compatibility (no comparing `ms` to `usd`)
  - Variable reference warnings

Per debate agreement: Level 1+2 = gate for Exp 0. Level 3 = reported metric.

**CLI:** `python3 src/axon_validator.py --tier 2 examples/basic.axon`

**Does NOT modify** `src/axon_parser.py` — experiments call the validator directly.

---

### Phase 3: Fairness & Preregistration Docs
**New files:** `experiments/FAIRNESS.md`, `experiments/PREREGISTRATION.md`

**FAIRNESS.md** — Documents symmetric constraints across the 5 conditions:
1. Free-form English, 2. Structured English, 3. Instruction-matched English, 4. JSON function calling, 5. AXON
- Prompt token budget parity
- Metadata envelope equivalence per condition
- 3-way LLM judge protocol (2 model families, anchored rubric)
- 30-item human validation subset
- Cross-model testing scope (Claude↔GPT)
- Failure/repair metrics tracked symmetrically

**PREREGISTRATION.md** — Primary endpoints, power analysis, statistical plan:
- Exp 0 gate: ≥80% parse success at few-shot
- Exp 1 co-primary: median token ratio
- Exp 3 co-primary: task success rate
- Naturalness operationalized as: error classes, recovery latency, schema-violation rates
- Holm-Bonferroni correction, mixed-effects models, bootstrap CIs

---

### Phase 4: Experiments Directory Scaffolding
**New files under `experiments/`:**

```
experiments/
  __init__.py
  requirements.txt        # tiktoken, anthropic, openai, scipy, statsmodels
  lib/
    __init__.py
    token_counter.py      # cl100k_base + o200k_base wrapper (~60 lines)
    api_client.py         # Unified Claude/GPT client with cost tracking (~120 lines)
    judge.py              # Multi-call LLM judge with anchored rubric (~150 lines)
    stats.py              # Wilcoxon, mixed-effects, Bonferroni, bootstrap (~120 lines)
    conversation.py       # Turn manager, validation, retry, logging (~150 lines)
```

These are **working stubs with real interfaces** — complete type signatures, docstrings, and core logic, but not battle-tested against live APIs yet. Enough to start writing Exp 0.

---

### Phase 5: Update Project Docs
**File:** `CLAUDE.md` — Add validator usage to Quick Reference, add experiments directory to Project Structure.

---

## Verification
1. `python3 src/axon_validator.py --tier 1 examples/basic.axon` — reports tier compliance
2. `python3 src/axon_validator.py --tier 2 --semantic examples/advanced.axon` — reports tier + semantic issues
3. `python3 -m pytest tests/test_validator.py` — all tests pass
4. `python3 src/axon_parser.py --check examples/*.axon` — no regressions from spec changes
5. All new files lint-clean and import correctly
