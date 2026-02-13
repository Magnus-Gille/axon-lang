# Exp 1 Plan Debate — Summary

## Participants
- **Claude** (Opus 4.6): Plan author and defender
- **Codex** (GPT-5.3): Adversarial reviewer

## Rounds
1. Claude draft → Codex critique → Claude response → Codex rebuttal
2. Self-review ablation: 7 points (2 major, 5 minor)

## Concessions Accepted by Both Sides

| # | Issue | Resolution |
|---|-------|------------|
| 1 | Element count mismatch with Exp 0 tasks.json | Create explicit deviation document with expanded element annotations and rationale |
| 2 | Must use 3-judge panel per FAIRNESS.md | Use full 3-judge protocol (Claude + GPT + tiebreaker) |
| 3 | Must add condition blinding for judges | Format-neutral preamble, no condition labels |
| 4 | Missing `complexity_level` fixed effect | Add to primary model per prereg |
| 5 | Statistical model needs distributional spec | Log-transform primary, raw ratio sensitivity, zero exclusion |
| 6 | Bootstrap resampling unit | Block bootstrap at task x model level |
| 7 | Data reuse defensible in principle | Standard multi-endpoint design, with deviation documentation |
| 8 | Element expansion conceptually justified | Atomic decomposition is correct for density; problem was silent redefinition |

## Defenses Accepted by Codex

- Data reuse from Exp 0 is defensible if deviations are documented
- Element expansion to atomic level is conceptually correct for a density metric

## Unresolved Issues

| # | Issue | Status |
|---|-------|--------|
| 1 | **Dual-track analysis requirement** — Must run BOTH prereg-faithful analysis (using Exp 0 element definitions) AND expanded atomic-element analysis (labeled exploratory) | Codex's final verdict — highest priority |
| 2 | **Human validation subset** — FAIRNESS.md requires 30-item human-scored subset; plan omits it | Codex raised in Round 2; Claude did not address |
| 3 | **Blinding is inherently limited** — Can't fully blind AXON syntax from JSON; format-neutral preamble is partial | Acknowledged by both; needs concrete normalization rules + non-circular bias check |
| 4 | **Prompt overhead** — Claude argues it's a fixed cost amortized over conversations; Codex says this isn't settled in a per-task benchmark | Genuine disagreement; resolve via breakeven analysis as secondary metric |
| 5 | **Power** — 81 per condition is between minimum (54) and target (162); Claude's "run more if needed" is a data-contingent rule | Not pre-specified as sequential design; acknowledge limitation |
| 6 | **Confirmatory vs exploratory status** — Post-hoc scoring machinery means Exp 1 cannot be purely confirmatory even with deviation filing | Both agree deviation filing is necessary; Codex argues it doesn't fully restore confirmatory status |

## New Issues from Round 2

1. Missing commitment to prereg-required dual reporting (both original and deviation analyses)
2. Estimand contradiction: include invalids in primary but exclude zeros from ratio
3. Bias-check proposal ("control for actual element presence") may be circular if ground truth comes from same judges
4. Human validation subset from FAIRNESS.md still missing

## Final Verdict (Both Positions)

**Codex**: The plan is promising but not confirmatory-grade. The single most important next step is to freeze a deviation addendum before any scoring that hard-locks: (1) a prereg-faithful analysis track, (2) an expanded atomic-element track labeled exploratory, and (3) final judge/blinding/human-subset/zero-handling rules.

**Claude**: Agrees with the dual-track approach. The expanded element taxonomy is necessary for meaningful density measurement, but the original prereg elements should be analyzed first as the confirmatory path. The expanded analysis adds scientific value as a pre-specified exploratory track.

**Consensus next step**: Write and freeze `experiments/exp1_token_efficiency/DEVIATION.md` before any judge scoring begins. This document must lock all scoring decisions and commit to dual-track analysis.

## Debate Files

1. `debate/exp1-plan-snapshot.md` — Frozen artifact snapshot
2. `debate/exp1-plan-claude-draft.md` — Claude's original plan
3. `debate/exp1-plan-claude-self-review.md` — Self-review ablation (7 points)
4. `debate/exp1-plan-codex-critique.md` — Codex Round 1 critique
5. `debate/exp1-plan-claude-response-1.md` — Claude's response
6. `debate/exp1-plan-codex-rebuttal-1.md` — Codex Round 2 rebuttal
7. `debate/exp1-plan-summary.md` — This file
8. `debate/exp1-plan-critique-log.json` — Structured critique log

## Costs

| Invocation | Tokens (in/out) | Wall-clock time | Model version |
|------------|-----------------|-----------------|---------------|
| Codex R1 (failed) | 53 / 415 | ~50min (network errors) | gpt-5.3-codex |
| Codex R1 (retry) | ~50k / ~2k | ~3min | gpt-5.3-codex |
| Codex R2 | 48 / 601 | ~2min | gpt-5.3-codex |

*Note: Codex R1 failed on first attempt due to network errors after completing analysis but before writing output. Retry succeeded.*
