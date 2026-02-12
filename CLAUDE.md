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

### How it works

For each major chunk of work (spec changes, experiment design, research claims):

1. **Claude Code** produces a draft (plan, spec section, evaluation, etc.)
2. **Codex is invoked headlessly** with a prompt to act as a grounded-but-adversarial reviewer — poking holes, demanding evidence, surfacing unstated assumptions
3. **Claude Code** responds to the critique, conceding valid points and defending where warranted
4. Repeat for 2-4 rounds until convergence or clear disagreement is documented
5. **Outcomes are recorded** in `debate/` with explicit lists of agreements, concessions, and unresolved disputes

### Prompting Codex

Run Codex CLI in headless mode. The adversarial prompt should:

- Ask Codex to critique the specific artifact (not generate alternatives)
- Instruct it to be skeptical but intellectually honest — no strawmanning
- Ground critique in evidence, not opinion
- Flag unsupported claims, missing baselines, and methodological gaps
- Acknowledge strengths before attacking weaknesses

### Recording outcomes

Each debate round should produce:

- `debate/<topic>-codex-critique.md` — Codex's critique
- `debate/<topic>-claude-response-N.md` — Claude's responses
- `debate/summary.md` — Updated with agreements/disagreements

### When to trigger a debate

- New spec sections or grammar changes
- Research claims or evidence assessments
- Experiment design and methodology
- Evaluation of results before drawing conclusions

The point is not consensus — it's surfacing blind spots. Documented disagreements are valuable.

## Current State

- 12 known parser bugs (see `debate/summary.md`)
- ~100 critique points raised, ~85% resolved
- 6-experiment validation plan designed but not yet implemented
- Core open question: does AXON beat controlled English + function calling? This is empirical — no premature claims.

## Conventions

- Evidence claims use tiers: **Established** (replicated), **Supported** (directional), **Hypothesis** (plausible but unverified)
- Spec changes require EBNF grammar updates in `spec/SPECIFICATION.md` and parser updates in `src/axon_parser.py`
- Example files should parse cleanly — run `--check` on all three before committing
