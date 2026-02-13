# AXON — Agent eXchange Optimized Notation

A research language for agent-to-agent communication. v0.1-experimental.

## Quick Reference

```bash
# Parse & validate
python3 src/axon_parser.py examples/basic.axon

# Full AST output
python3 src/axon_parser.py --ast examples/advanced.axon

# Validate only (no output on success)
python3 src/axon_parser.py --check examples/real_world_scenarios.axon

# Stdin
echo 'QRY(@a>@b): status(@srv)' | python3 src/axon_parser.py -

# Tier validation (1=Core, 2=Interop, 3=Production)
python3 src/axon_validator.py --tier 1 examples/basic.axon
python3 src/axon_validator.py --tier 2 tests/conformance/valid_tier2.axon

# Conformance tests
python3 -m pytest tests/conformance/
python3 -m pytest tests/test_validator.py

# Exp 0 dry run
python3 experiments/exp0_learnability/run.py --dry-run
```

Parser and validator are stdlib Python only. Experiments require `tiktoken` (`pip install -r experiments/requirements.txt`).

## Project Structure

- `spec/SPECIFICATION.md` — Formal grammar, type system, compliance tiers
- `src/axon_parser.py` — Reference parser (lexer + recursive descent)
- `src/axon_validator.py` — 3-level conformance validator (syntax, tier compliance, semantics)
- `examples/` — `.axon` files and English comparisons
- `tests/conformance/` — Canonical conformance corpus (valid + invalid cases)
- `tests/test_validator.py` — Validator unit tests
- `experiments/` — Experiment infrastructure (Exp 0–5)
  - `experiments/lib/` — Shared utilities (token counter, condition adapters)
  - `experiments/exp0_learnability/` — Learnability gate experiment
  - `experiments/FAIRNESS.md` — Fairness protocol for 6-condition design
  - `experiments/PREREGISTRATION.md` — Pre-registered analysis plan
  - `experiments/MASSGEN_ADDENDUM.md` — Exploratory MassGen ecosystem-validity extension
- `RESEARCH.md` — Evidence-backed rationale (20+ sources)
- `debate/` — Adversarial review transcripts and outcomes

### 6 Experimental Conditions
1. Free-form English (baseline)
2. Structured English
3. Instruction-matched English
4. JSON Function Calling
5. FIPA-ACL
6. AXON

## Adversarial Debate Workflow

This project uses a **Claude Code + Codex adversarial review** process. The goal is to stress-test every significant decision through structured critique.

**Always use the `/debate-codex` skill** (defined in `.claude/skills/debate-codex/SKILL.md`) to run debates. It handles the full lifecycle: Codex CLI invocation, multi-round structure, and outcome recording.

### When to trigger a debate

- New spec sections or grammar changes
- Research claims or evidence assessments
- Experiment design and methodology
- Evaluation of results before drawing conclusions

The point is not consensus — it's surfacing blind spots. Documented disagreements are valuable.

## Two Research Tracks

This project pursues two independent but complementary research tracks:

- **Track A — AXON language evaluation**: Does AXON beat controlled English + function calling for agent-to-agent communication? Empirical question answered by the 6-experiment validation plan. See `debate/experiment-plan/STATUS.md`.
- **Track B — Adversarial methodology evaluation**: Does structured cross-model adversarial review (Claude↔Codex) catch more real issues than self-review? Answered by collecting structured data from every debate. See `debate/methodology-summary.md`.

Every debate feeds Track B. All future debates must capture: per-point metadata, self-review ablation, cost logging, and frozen artifact snapshots (see the `/debate-codex` skill for the full protocol).

## Current State

- Spec frozen at `v0.1-experimental` — 4 gate-blocking parser bugs fixed
- Conformance test corpus: 54 tests passing
- Validator: 3-level checker (syntax, tier compliance, semantics)
- **Exp 0 complete** (preliminary): AXON passes learnability gate on Sonnet (89%) and GPT-5.3 (100%), fails on Haiku (78% — matches JSON FC). See `experiments/exp0_learnability/RESULTS.md`.
- Exp 0 runner uses CLI tools (`claude -p`, `codex exec`) — zero API cost
- ~100 critique points raised, ~85% resolved
- Core open question (Track A): does AXON beat controlled English + function calling? Exp 0 is promising but preliminary.
- Methodology paper (Track B): publishable as registered pilot + prospective protocol paper if 6-item checklist is met
- **MassGen addendum** (exploratory): Frozen plan to replicate Exp 3 + Exp 4 through MassGen multi-agent orchestration after prereg experiments complete. Tests ecological validity — whether format advantages survive real orchestration. Activates only if prereg shows significant AXON advantage. See `experiments/MASSGEN_ADDENDUM.md` and `debate/massgen-integration-summary.md`.

## Conventions

- Evidence claims use tiers: **Established** (replicated), **Supported** (directional), **Hypothesis** (plausible but unverified)
- Spec changes require EBNF grammar updates in `spec/SPECIFICATION.md` and parser updates in `src/axon_parser.py`
- Example files should parse cleanly — run `--check` on all three before committing
