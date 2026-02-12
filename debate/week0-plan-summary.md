# Week 0 Plan Debate — Summary

## Participants & Rounds
- **Claude** (author): Proposed implementation plan for Week 0 prerequisites
- **Codex** (adversarial reviewer): 2 rounds of critique
- **Rounds:** Draft → Self-review → Codex R1 critique → Claude response → Codex R2 rebuttal

## Concessions Accepted by Both Sides

| Point | Claude Conceded | Codex Accepted |
|-------|----------------|----------------|
| Spec freeze needs tier-field reconciliation | Yes | Yes — "hard blocker" |
| Level 2 needs type checks, duplicate detection, version check | Yes | Yes — "real improvement" |
| Defer heavy experiment infrastructure | Yes | Yes — "solid correction" |
| Add secondary endpoints to preregistration | Yes | Yes — "concrete omission fixed" |
| Reorder: executable harness before docs | Yes | Yes — "correct critical-path shift" |
| Mark `\u{XXXX}` as reserved, not implemented | Yes | (Accepted implicitly) |
| Separate validator module is architecturally correct | N/A (defense) | Yes — "valid defense" |
| Level 3 non-gating is correct | N/A (defense) | Yes — "pragmatic choice" |

## Defenses Accepted by Codex
1. Separate validator module vs modifying parser — architecturally superior
2. Level 3 as non-gating diagnostics — correct given semantic underspecification
3. Response-link integrity scoped to multi-message docs — fair constraint

## Unresolved Issues (Require Human Decision)

### 1. FIPA-ACL baseline
- **Claude's position:** JSON function calling subsumes FIPA-ACL; will document rationale in FAIRNESS.md
- **Codex's position:** This is unilateral reinterpretation; needs project governance approval
- **Decision needed:** Is the FIPA-ACL omission acceptable with documented rationale, or must it be a separate condition?

### 2. Identifier legality strategy
- **Claude's position:** Document parser's permissive behavior as normative for v0.1
- **Codex's position:** Acceptable only if explicit, testable, and paired with forward-compatibility plan
- **Decision needed:** Fix the parser to match spec (letter-first), or update spec to match parser (allow digit-first)?

### 3. Duplicate metadata keys — warning vs error
- **Claude's position:** Warning in validator
- **Codex's position:** Should be error for Exp 0 gating (affects reproducibility)
- **Decision needed:** Error or warning?

## New Issues from Round 2
1. **Internal contradiction:** Plan says both "parser behavior is normative" and "identifier legality is gate-affecting, fix now" — needs one decision
2. **Ordering risk:** Parser fixes should come before or alongside validator build, not after
3. **Known Gaps appendix needs acceptance semantics:** Bug classification should define how each class affects Exp 0 eligibility

## Codex's Final Verdict
**Produce a machine-checkable conformance corpus** — valid and invalid AXON cases with expected outcomes — that encodes freeze decisions on tiers, identifiers, escapes, duplicate keys, and version semantics. Parser + Level 2 validator must pass this corpus as the Week 0 exit gate.

## Both Sides Agree On
The revised plan is "materially better" than the original. The main remaining work is resolving the 3 human-decision points above and producing the conformance corpus.

## Debate Files
1. `debate/week0-plan-claude-draft.md` — Artifact snapshot
2. `debate/week0-plan-claude-self-review.md` — Self-review ablation
3. `debate/week0-plan-codex-critique.md` — Codex Round 1
4. `debate/week0-plan-claude-response-1.md` — Claude response
5. `debate/week0-plan-codex-rebuttal-1.md` — Codex Round 2
6. `debate/week0-plan-summary.md` — This file
7. `debate/week0-plan-critique-log.json` — Structured critique log
