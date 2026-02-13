# Debate Summary: MassGen Integration into AXON Experiments

**Topic**: Should MassGen (multi-agent consensus framework) be integrated into AXON's experimental setup?
**Participants**: Claude (Opus 4.6) vs. Codex (GPT-5.3)
**Rounds**: 2 (draft + self-review, R1 critique, R1 response, R2 rebuttal)
**Date**: 2026-02-13

## Concessions Accepted by Both Sides

| Point | Conceded by | Accepted by |
|-------|-------------|-------------|
| MassGen as 7th condition is a category error (format vs. orchestration) | Claude (draft) | Codex (R1) |
| Exp 5 in preregistration is cross-model variance, NOT 128-agent scaling | Claude (R1 response) | Codex (R2) |
| "~100 lines of Python" for multi-agent orchestration is unsupported | Claude (R1 response) | Codex (R2) |
| Status-quo bias exists in Claude's all-negative initial assessment | Claude (R1 response) | Codex (R2) |
| "Lab first, ecosystem second" sequencing is methodologically coherent | Codex (R2) | — |
| Scoping demand for exploratory phase is valid | Codex (R2) | — |

## Defenses Accepted by Codex

- **D2**: MassGen as 7th condition remains wrong (fully valid)
- **PC2**: Pre-registered experiments should run in isolation first (mostly valid)
- **PC3**: Exploratory phase needs concrete scoping (valid)

## Unresolved Issues

1. **Exploratory phase scoping**: Claude accepts an exploratory MassGen phase "in principle" but hasn't defined which experiments, how many runs, or success criteria. Codex calls this a "promissory note."
2. **Decision-point ambiguity**: "After primary analyses complete" is undefined — after Exp 0 gate? After Exp 0-5? After publication?
3. **Variance budget**: Claude's noise objection to MassGen-as-infrastructure is directionally correct but unquantified. No sensitivity analysis exists.
4. **Track B timeline**: Both agree multi-model consensus review is interesting for Track B but neither defines a concrete trigger for when to add it.

## New Issues from Later Rounds

1. No prereg-deviation workflow has been committed to for the exploratory phase
2. Burden-shift: Claude demands scoping from Codex without proposing a competing scope
3. C2 replacement: the bad LOC estimate was retracted but not replaced with even a coarse engineering decomposition

## Final Positions

**Claude's revised position**: Do not integrate MassGen into pre-registered experiments (Exp 0-5). Accept an exploratory ecosystem-validity phase using MassGen as controlled infrastructure after primary analyses, but scope it concretely first.

**Codex's verdict**: Conditionally sound. Methodologically coherent on major points. Operationally incomplete until a frozen one-page Exploratory MassGen Addendum is created specifying: fixed version/config, selected experiments (minimum Exp 3+4), unchanged 6 conditions, analysis split protocol, and variance contingency rule.

**Codex's single most actionable recommendation**: Write the Exploratory MassGen Addendum now, before any exploratory runs, to convert the promissory acceptance into an executable plan.

## Debate Files

1. `debate/massgen-integration-claude-draft.md` — Claude's initial assessment
2. `debate/massgen-integration-claude-self-review.md` — Self-review ablation
3. `debate/massgen-integration-codex-critique.md` — Codex Round 1 critique
4. `debate/massgen-integration-claude-response-1.md` — Claude's response
5. `debate/massgen-integration-codex-rebuttal-1.md` — Codex Round 2 rebuttal
6. `debate/massgen-integration-summary.md` — This file
7. `debate/massgen-integration-critique-log.json` — Structured critique log

## Costs

| Invocation | Tokens (in/out) | API cost | Wall-clock time | Model version |
|------------|-----------------|----------|-----------------|---------------|
| Codex R1   | ~18k / ~3k      | $0.00    | ~90s            | gpt-5.3-codex |
| Codex R2   | ~24k / ~3k      | $0.00    | ~60s            | gpt-5.3-codex |
