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
  - `experiments/exp1_token_efficiency/` — Token efficiency evaluation
  - `experiments/exp2_parse_accuracy/` — Parse accuracy under perturbation (noise robustness)
  - `experiments/exp3_compositionality/` — Composition operator evaluation (co-primary with Exp 1)
  - `experiments/exp3_compositionality/phase2/` — Round-trip decomposition (cross-model)
  - `experiments/exp5_cross_model/` — Cross-model generalization analysis
  - `experiments/exp_aisp_comparison/` — AISP competitive analysis benchmarks (A, B, C complete)
  - `experiments/exp_json_contracts/` — JSON+Contracts (SEMAP-inspired, exploratory)
  - `experiments/exp_m5_falsification/` — Falsification campaign on local open models (M5); round-trip fidelity, capability-floor finding (REPORT.md, VENUES.md)
  - `experiments/FAIRNESS.md` — Fairness protocol for 8-condition design
  - `experiments/PREREGISTRATION.md` — Pre-registered analysis plan
  - `experiments/MASSGEN_ADDENDUM.md` — Exploratory MassGen ecosystem-validity extension
- `paper/` — Paper outline and related work drafts
- `RESEARCH.md` — Evidence-backed rationale (20+ sources)
- `debate/` — Adversarial review transcripts and outcomes

### 8 Experimental Conditions
1. Free-form English (baseline)
2. Structured English
3. Instruction-matched English
4. JSON Function Calling
5. FIPA-ACL
6. AXON
7. AISP (exploratory, post-pre-registration — see `experiments/exp_aisp_comparison/DEVIATION.md`)
8. JSON+Contracts (exploratory, SEMAP-inspired — see `experiments/exp_json_contracts/DEVIATION.md`)

## Adversarial Debate Workflow

This project uses a **Claude Code + Codex adversarial review** process. The goal is to stress-test every significant decision through structured critique.

**Always use the `/debate-codex` skill** (global, in `~/.claude/skills/`) to run debates. It handles the full lifecycle: Codex CLI invocation, multi-round structure, and outcome recording. Note: debate files in this project are tracked in git (they are research data for Track B).

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
- Conformance test corpus: 69 tests passing
- Validator: 3-level checker (syntax, tier compliance, semantics)
- **Exp 0 complete**: AXON passes learnability gate on all 3 models (3x replications). See `experiments/exp0_learnability/RESULTS.md`.
- **Exp 1 complete**: 486 outputs scored + statistical analysis. AXON #1 in tok/unit (15.4 mean, ~32% better than JSON FC). See `experiments/exp1_token_efficiency/RESULTS.md`.
- **Exp 2 complete**: Parse accuracy under perturbation. 1,656 outputs. AXON 16.2% preservation (strict syntax = fragile). See `experiments/exp2_parse_accuracy/RESULTS.md`.
- **Exp 3 complete**: Compositionality — 567 outputs, full judge scoring. **AXON ranks last (67.0%)** — English conditions dominate (94-96%). See `experiments/exp3_compositionality/RESULTS.md`.
- **Exp 3 Phase 2 complete**: Round-trip decomposition. 177 cross-model calls, 99% parseable. See `experiments/exp3_compositionality/phase2/`.
- **Exp 5 complete**: Cross-model variance. AXON lowest SD (0.048 composition). See `experiments/exp5_cross_model/RESULTS.md`.
- **JSON+Contracts complete**: 81 cells. 51.6% composition rate — contracts help but don't match AXON. See `experiments/exp_json_contracts/RESULTS.md`.
- **M5 falsification complete** (2026-06-26, branch `axon-m5-falsification` / PR #2): first eval on **local open models** via round-trip fidelity. AXON **falsified as a general format** (last on fidelity 0.85, only 64% parse-valid) but **earns a niche on large/code-tuned models** (~40% fewer tokens at matched fidelity, on the Pareto frontier). **Capability floor is sender-side** (Spearman(capability, AXON fidelity)=+1.00; easy to read, hard to write). Constrained-decoding rescue is partial (validity≠correctness). Scorer validated vs frontier judge (r=0.875). See `experiments/exp_m5_falsification/REPORT.md`; venues in `VENUES.md`.
- **AISP comparison complete**: All benchmarks (A, B, C, 1, 2, 3). AISP 5.1x more tokens than AXON. See `experiments/exp_aisp_comparison/RESULTS.md`.
- Exp 0/1/3 runner uses CLI tools (`claude -p`, `codex exec`) — zero API cost
- ~100 critique points raised, ~85% resolved
- **Paper reframing needed**: Original thesis (intrinsic compositionality > extrinsic) not supported by judge-scored data. See `STATUS.md`.
- **Ecosystem landscape** (Mar 2026): 15+ protocols mapped across 5 layers. AXON = Layer 3 (content format). See `debate/ecosystem-landscape-2026.md`.

## Conventions

- Evidence claims use tiers: **Established** (replicated), **Supported** (directional), **Hypothesis** (plausible but unverified)
- Spec changes require EBNF grammar updates in `spec/SPECIFICATION.md` and parser updates in `src/axon_parser.py`
- Example files should parse cleanly — run `--check` on all three before committing
