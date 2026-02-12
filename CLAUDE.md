# AXON — Agent eXchange Optimized Notation

A research language for agent-to-agent communication. Draft v0.1.

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
```

No external dependencies — stdlib Python only.

## Project Structure

- `spec/SPECIFICATION.md` — Formal grammar, type system, compliance tiers
- `src/axon_parser.py` — Reference parser (lexer + recursive descent)
- `examples/` — `.axon` files and English comparisons
- `RESEARCH.md` — Evidence-backed rationale (20+ sources)
- `debate/` — Adversarial review transcripts and outcomes

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

- 12 known parser bugs (see `debate/summary.md`)
- ~100 critique points raised, ~85% resolved
- 6-experiment validation plan designed but not yet implemented
- Core open question (Track A): does AXON beat controlled English + function calling? This is empirical — no premature claims.
- Methodology paper (Track B): publishable as registered pilot + prospective protocol paper if 6-item checklist is met

## Conventions

- Evidence claims use tiers: **Established** (replicated), **Supported** (directional), **Hypothesis** (plausible but unverified)
- Spec changes require EBNF grammar updates in `spec/SPECIFICATION.md` and parser updates in `src/axon_parser.py`
- Example files should parse cleanly — run `--check` on all three before committing
