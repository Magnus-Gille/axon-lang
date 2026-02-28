# CFP v2 Debate Summary

**Date:** 2026-02-16
**Participants:** Claude Opus 4.6, Codex GPT-5.3
**Rounds:** 2
**Topic:** Improving two Agentic Dev Days 2026 CFP proposals (30-min talk + lightning talk)

## Context

This is the second CFP debate. The first (cfp-suitability) concluded "submit lightning only; 30-min talk premature without benchmarks." Since then, Exp 0 (learnability) and Exp 1 (token efficiency, 486 outputs) are both complete with statistically significant results. The user submitted two draft proposals for review.

## Concessions accepted by both sides

1. **Six formats, five listed** — copy error in Talk 1 abstract. Fixed by listing all six.
2. **"Every framework" universal claim** — unsupported by data. Replaced with specific problem framing.
3. **"Break" overstates** — data shows tradeoffs, not blanket failure. Softened to "hit their limits."
4. **p-values removed from abstract** — specific statistical claims moved to talk content. Abstract uses effect sizes and directional language only.
5. **Self-review comparative claim** — Talk 2 softened to "initial single-model review missed" until self-review catch rate is computed from critique logs.
6. **Critique point total** — "115+ critique points" dropped unless verified from auditable logs before submission.

## Defenses accepted by Codex

1. **Conditional compactness claim** — "English variants were similarly compact when outputs succeeded" is accurate per two-part analysis. Valid with explicit caveat.
2. **Talk 2 de-coupling** — revised abstract is method-first, AXON minimal. Adequate separation.

## Unresolved disagreements

1. **"Confirmed across three independent statistical approaches"** — Claude proposed as replacement for raw p-values. Codex flagged as a new overclaim (Holm-corrected pairwise is marginal). Final version dropped this language entirely.
2. **30-minute Q&A fragility** — Codex says Talk 1 is "fragile under adversarial Q&A." Claude says knowable caveats are manageable. Both agree the abstract must not overclaim; the in-talk presentation handles nuance.

## New issues from Round 2

- Codex flagged that removing all stats from the abstract without acknowledging hybrid scoring and pending cross-validation could still leave a credibility gap. Final Talk 1 addresses this by being specific about tradeoffs ("including where AXON doesn't win").
- Talk 2 depends on uncomputed self-review comparison data. This is a pre-submission action item.

## Final verdict

Both sides converge: **proposals are submission-ready with the fixes applied.** The final versions incorporate all concessions.

## Action items

| Item | Owner | Status |
|------|-------|--------|
| Verify exact critique-point count from debate logs | Magnus | Before submission |
| Compute self-review catch rate from caught_by_self_review fields | Magnus | Before submission (optional — Talk 2 works without it) |
| Complete Exp 1 cross-validation (30 items) | Magnus | Before conference |
| Complete human validation subset (30 items) | Magnus | Before conference |

## Debate files

- `debate/cfp-v2-snapshot.md` — frozen proposals and context
- `debate/cfp-v2-claude-draft.md` — Claude's initial improved versions
- `debate/cfp-v2-claude-self-review.md` — Claude's self-critique
- `debate/cfp-v2-codex-critique.md` — Codex Round 1 critique
- `debate/cfp-v2-claude-response-1.md` — Claude's response
- `debate/cfp-v2-codex-rebuttal-1.md` — Codex Round 2 rebuttal
- `debate/cfp-v2-final-talk1.md` — Final Talk 1 proposal
- `debate/cfp-v2-final-talk2.md` — Final Talk 2 proposal
- `debate/cfp-v2-summary.md` — This file
- `debate/cfp-v2-critique-log.json` — Structured critique log

## Costs

| Invocation | Wall-clock time | Model version |
|------------|-----------------|---------------|
| Codex R1   | ~3m             | gpt-5.3-codex |
| Codex R2   | ~3m             | gpt-5.3-codex |
