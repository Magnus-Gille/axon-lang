# Week 0 Plan Critique (Codex)

## Strengths First
- The plan gets the high-level dependency direction mostly right: spec decisions before validator, validator before experiments (`debate/week0-plan-claude-draft.md:10`, `debate/week0-plan-claude-draft.md:23`, `debate/week0-plan-claude-draft.md:68`).
- Splitting validator work from the parser is architecturally clean and keeps parser minimalism intact (`debate/week0-plan-claude-draft.md:27`, `debate/week0-plan-claude-draft.md:43`).
- Level 1/2 as gate and Level 3 as reported metric is a pragmatic compromise given semantic underspecification (`debate/week0-plan-claude-draft.md:34`, `debate/week0-plan-claude-draft.md:39`).
- The self-review is not performative; it identifies real design gaps (freeze depth, Level 3 feasibility, premature infra) (`debate/week0-plan-claude-self-review.md:13`, `debate/week0-plan-claude-self-review.md:21`, `debate/week0-plan-claude-self-review.md:29`).

## 1. Spec Freeze Adequacy
**Verdict:** Fixing only `meta_key` is necessary but not sufficient for a credible freeze.

Additional inconsistencies likely to break experiment validity:
- Tier definition conflict: section 2 implies Tier 2 adds only `re/ts/ctx` and Tier 3 adds `sig/authz/tenant/err_ns` (`spec/SPECIFICATION.md:49`, `spec/SPECIFICATION.md:58`), but metadata table says `sig` and `authz` are optional in Tier 2 (`spec/SPECIFICATION.md:352`, `spec/SPECIFICATION.md:353`). Your Level 2 validator behavior will diverge unless this is resolved.
- Escape semantics mismatch: spec defines Unicode escapes `\u{XXXX}` (`spec/SPECIFICATION.md:489`), parser string logic does not decode that form (`src/axon_parser.py:125`, `src/axon_parser.py:137`). Freeze without reconciling this gives inconsistent string semantics across implementations.
- Identifier lexical mismatch: spec requires identifiers start with a letter (`spec/SPECIFICATION.md:230`, `spec/SPECIFICATION.md:231`), but parser path/ref/tag readers accept digit-first segments (`src/axon_parser.py:162`, `src/axon_parser.py:295`, `src/axon_parser.py:302`).
- Metadata type contract is not executable as written: grammar allows any expression for metadata values (`spec/SPECIFICATION.md:255`) while table claims concrete types (`spec/SPECIFICATION.md:345`, `spec/SPECIFICATION.md:355`). If types matter experimentally, freeze must say where they are enforced.
- Transition and typing rules are still partially prose-level, not mechanically decidable in a single-message validator (`spec/SPECIFICATION.md:136`, `spec/SPECIFICATION.md:137`, `spec/SPECIFICATION.md:325`, `spec/SPECIFICATION.md:327`).

Minimum freeze bar should include: tier-field reconciliation, identifier/escape lexical alignment with parser, metadata type-enforcement policy, and explicit scope of what is normative vs deferred.

## 2. Validator Design
**Verdict:** The 3-level shape is sound, but the current Level 2/3 definitions are incomplete for Week 0 claims.

What is solid:
- Layering parse-tier-semantic is clean (`debate/week0-plan-claude-draft.md:29`, `debate/week0-plan-claude-draft.md:30`, `debate/week0-plan-claude-draft.md:34`).

What is weak:
- Level 2 currently reads as required-field presence only (`debate/week0-plan-claude-draft.md:30` to `debate/week0-plan-claude-draft.md:34`). Missing required checks:
- metadata type checks (e.g., `id` string, `%%` number) (`spec/SPECIFICATION.md:345`, `spec/SPECIFICATION.md:346`)
- protocol version support semantics (`spec/SPECIFICATION.md:494`)
- duplicate metadata keys (parser silently overwrites via dict assignment) (`src/axon_parser.py:530`, `src/axon_parser.py:542`)
- response-link integrity (`re` points to known prior `id`) when validating multi-message docs (`spec/SPECIFICATION.md:347`)
- Level 3 transition checking is only partially feasible with current spec and likely noisy for Exp 0 single-message samples, matching Claude’s own concern (`debate/week0-plan-claude-self-review.md:22`, `debate/week0-plan-claude-self-review.md:27`).

Recommendation:
- Keep Level 3 as non-gating lints, but explicitly classify checks as `deterministic` vs `context-required` vs `spec-ambiguous`.
- Strengthen Level 2 to include structural + type + version + duplicate-key checks; otherwise "tier-compliant" remains weakly defined.

## 3. Experiment Scaffolding Timing
**Verdict:** Full experiment library build now is premature; minimal scaffolding now is justified.

Why:
- The plan itself labels these as "working stubs" not battle-tested (`debate/week0-plan-claude-draft.md:84`).
- Self-review correctly flags speculative abstraction risk before gate outcome is known (`debate/week0-plan-claude-self-review.md:29`, `debate/week0-plan-claude-self-review.md:32`).

What to do now:
- Build only what Exp 0 needs: validator integration, condition adapters, token accounting, result logging.
- Defer `api_client.py`, `judge.py`, and full `stats.py` until Exp 0 passes and data pathways stabilize.

This still respects STATUS requirement to set up `experiments/` and shared libs (`debate/experiment-plan/STATUS.md:21`) without overcommitting architecture.

## 4. Missing Pieces vs STATUS.md
**Verdict:** The plan misses or underspecifies multiple explicit Week 0 prerequisites.

Gaps:
- STATUS says extend `validate()` beyond parse-only (`debate/experiment-plan/STATUS.md:16`), but plan avoids modifying parser and creates a separate validator (`debate/week0-plan-claude-draft.md:43`). That may be fine technically, but it is a direct mismatch to stated prerequisite wording.
- FIPA-ACL baseline is required (`debate/experiment-plan/STATUS.md:26`), and fairness should include symmetric FIPA adaptation budget (`debate/experiment-plan/STATUS.md:18`), but plan’s 5 conditions omit FIPA-ACL (`debate/week0-plan-claude-draft.md:51`, `debate/week0-plan-claude-draft.md:52`).
- Prereg secondary endpoints required in STATUS (auditability, composability, formal verifiability) are absent from plan prereg endpoints (`debate/experiment-plan/STATUS.md:19`, `debate/week0-plan-claude-draft.md:60`, `debate/week0-plan-claude-draft.md:63`).
- Critical path calls for a preregistered **executable evaluation harness** before experiments (`debate/experiment-plan/STATUS.md:12`); current plan describes docs and stubs, not a concrete harness artifact with acceptance criteria.

## 5. Risk of Freezing Bugs
**Verdict:** Deferring all 12 known parser bugs until after Exp 0 is high risk and likely contaminates gate results.

Reasoning:
- Plan admits these are grammar-parser mismatches (`debate/week0-plan-claude-draft.md:19`). That is exactly the class of bug that changes pass/fail outcomes in Level 1 parse gating (`debate/week0-plan-claude-draft.md:29`).
- Current parser already demonstrates out-of-spec acceptance patterns due permissive lexical/meta behavior (`src/axon_parser.py:162`, `src/axon_parser.py:295`, `src/axon_parser.py:528`, `src/axon_parser.py:803`).

Consequence:
- Exp 0 can produce false positives (invalid-by-spec messages counted valid) and false negatives (spec-valid patterns rejected by parser if any unresolved mismatch remains), which weakens the learnability gate as evidence.

Pragmatic compromise:
- Do not fix everything pre-gate.
- But fix or quarantine **gate-affecting mismatches** now: lexer/tokenization, identifier legality, metadata parse/type handling, and any examples in spec corpus that parser cannot round-trip.

## 6. Prioritization
**Verdict:** Current ordering is close, but not optimal.

Better order:
1. Freeze spec with explicit acceptance criteria and known-gap registry (not just `meta_key`).
2. Build validator Level 1+2 with deterministic checks only; define Level 3 as non-gating diagnostics.
3. Create executable Exp 0 harness (minimal) and run against a canonical conformance corpus.
4. Finalize fairness/prereg docs after harness shape is concrete (include FIPA baseline and secondary endpoints).
5. Defer heavy shared experiment libraries until after Exp 0 gate.

Rationale:
- This matches STATUS critical path emphasis on executable harness (`debate/experiment-plan/STATUS.md:12`) while reducing wasted infra if Exp 0 fails.

## Bottom Line
The plan is directionally good but under-scoped for a true freeze and over-scoped on premature infrastructure. The biggest correction is to separate "stable enough for Exp 0 gating" from "full experimental platform," and to resolve spec/parser mismatches that directly alter validity outcomes before claiming a frozen artifact.
