# Week 0 Plan Round 2 Rebuttal (Codex)

Claude’s response is materially better than the original draft. Several concessions are real, technically relevant, and improve Week 0 credibility. The remaining weaknesses are now mostly about unresolved decision points, not complete blind spots.

## 1) Genuine Concessions That Are Adequate

1. Tier-definition reconciliation was conceded clearly and correctly.
This was a hard blocker for validator determinism, and conceding it before freeze is the right move.

2. Level 2 validator expansion is a real improvement.
Adding type checks, duplicate-key detection, version checks, and multi-message `re` integrity addresses the original “field presence only” weakness.

3. Heavy experiment infra deferral is a solid correction.
Narrowing Week 0 scaffolding to Exp 0 essentials removes unnecessary architecture risk.

4. Secondary endpoints were genuinely conceded.
Adding auditability/composability/formal-verifiability to prereg scope fixes a concrete omission.

5. Prioritization moved in the right direction.
Putting executable Exp 0 work ahead of polished docs is the correct critical-path shift.

## 2) Defenses That Are Valid

1. Separate validator module vs modifying parser is a valid defense.
The critique was about validation capability, not code placement. Keeping parser minimal and putting conformance checks in a dedicated validator is architecturally cleaner.

2. Keeping Level 3 non-gating is still correct.
Given current semantic underspecification, treating transition/typing checks as diagnostics rather than gates remains the pragmatic choice.

3. Response-link integrity being multi-message-only is a fair scope constraint.
It should exist, but it should not block single-message Exp 0 cases.

## 3) Defenses or Partial Concessions That Still Dodge the Core Point

1. FIPA-ACL handling is still mostly a dodge.
Saying “JSON FC subsumes FIPA” is an argument, not a baseline. STATUS-level baseline requirements are about comparability, not just structural modernity. If FIPA is omitted, the plan needs explicit acceptance from project governance, not unilateral reinterpretation in FAIRNESS.md.

2. “Identifier parser behavior is normative for v0.1” is under-specified.
This can be acceptable as a temporary freeze rule, but only if it is explicit, testable, and paired with a forward-compatibility plan. Otherwise it converts known parser permissiveness into accidental language design.

3. Duplicate keys as a warning is likely too weak for a gate.
Because parser overwrites silently, duplicate metadata keys undermine reproducibility. For Exp 0 gating, this should likely be an error (or at least a fail-level diagnostic), not a soft warning.

## 4) New Issues Introduced by the Response

1. Internal contradiction on identifier mismatches.
Section 1 implies “document parser behavior as normative,” while Section 5 implies “identifier legality is gate-affecting and should be fixed now.” Those are different strategies. Week 0 needs one explicit decision path.

2. Ordering risk in revised phases.
The revised order puts validator build before gate-affecting parser fixes. Since Level 1 wraps parser behavior, parser changes can invalidate validator assumptions/tests. Either parser fix and validator implementation must be iterative, or parser-fix criteria must be finalized before validator acceptance.

3. “Known Gaps” appendix still lacks acceptance semantics.
Classifying bugs is useful, but there is no explicit rule for how each class affects Exp 0 pass/fail eligibility. Without that, the gap registry is documentation, not governance.

## Final Verdict: Single Most Important Next Step

Define and execute a **machine-checkable Week 0 conformance contract** before further expansion.

Concretely: produce a canonical conformance corpus (valid/invalid AXON cases with expected outcomes) that encodes the freeze decisions on tiers, identifiers, escapes, duplicate keys, and version semantics; then make parser + Level 2 validator pass that corpus as the Week 0 exit gate.

This single step forces closure on the remaining ambiguities, resolves the parser-vs-spec tension in executable form, and prevents Exp 0 from being built on an unstable definition of “valid AXON.”
