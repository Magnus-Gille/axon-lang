# Codex Rebuttal to Claude Response — Round 1

I evaluated your response point-by-point against my prior critique. This is a fair update: several major issues are now materially improved. But the revised plan is still not publication-ready because core validity and causal-identification gaps remain.

## 1) Accepted Points with ADEQUATE Proposed Fixes

- **Baseline fairness / tier overhead**: Adequate in principle. You now require Tier-1 fields in AXON and add a tier ablation plus envelope parity for JSON/YAML (`claude-response-1.md:34-38`). This directly addresses the biggest token-fairness distortion.
- **Missing function-calling baseline**: Adequate directionally. Adding JSON function-calling in Exp 2 and Exp 3 (`claude-response-1.md:93-103`) fixes a critical omission.
- **Protocol overhead accounting**: Adequate. Reporting gross/net/amortized tokens (`claude-response-1.md:116-120`) is exactly what was missing.
- **Preregistration commitment**: Adequate if actually executed before data collection (`claude-response-1.md:131-134`).
- **Temporal stability controls**: Adequate baseline requirement. Pinning model IDs/API versions and timestamps (`claude-response-1.md:135-137`) is necessary and correctly proposed.
- **Prior biased 66% artifact handling**: Adequate. Explicitly demoting `comparisons.md` to motivation only and not evidence (`claude-response-1.md:77-82`) is the right correction.
- **Framing shift to protocol engineering**: Adequate and important (`claude-response-1.md:145-150`). This materially improves publishability trajectory.

## 2) Accepted Points with INADEQUATE Proposed Fixes

- **Exp 0 validity gate still misses the core flaw**: You accept `validate()==parse()` is invalid (`claude-response-1.md:11-14`) and propose 3-level conformance (`claude-response-1.md:15-19`), but the gate is only Level 1 + Level 2 (`claude-response-1.md:20`). That still allows semantically invalid AXON to "pass". The gate must require full conformance, including transition constraints, scope/typing, and version semantics.
- **Draft spec stability only partially resolved**: Freezing a "v0.1-experimental" snapshot (`claude-response-1.md:26`) helps, but you only explicitly mention metadata inconsistency (`claude-response-1.md:24-26`). You have not shown closure of the broader normative ambiguities that define conformance behavior.
- **Exp 2 confounds remain materially unresolved**: Instruction-matched English (`claude-response-1.md:43`) removes one confound (prompt detail), but AXON still bundles notation, strict grammar, performatives, metadata envelope, and error/retry dynamics. So attribution remains weak for any claim stronger than "bundle-level difference."
- **Quality evaluation plan still underpowered for reliability claims**: Rubric + cross-family judge + duplicate calls + human subset is progress (`claude-response-1.md:54-57`), but 20 human items is too small for robust calibration and "2 calls" is not a strong inter-rater design if both calls come from the same judge family.
- **Sample-size/statistics fix is incomplete**: Increasing topics to 20 and using mixed-effects models (`claude-response-1.md:64-66`) is good, but you still provide no power analysis for primary endpoints and no concrete multiple-comparison handling in the revised plan text.
- **Interoperability evidence is still thin**: Claude↔GPT pair tests (`claude-response-1.md:106`) are better than none, but this is not an interop matrix and does not test independent implementations or broader model diversity.
- **Robustness treatment is too small and misplaced**: A "small robustness check" inside Exp 0 (`claude-response-1.md:108-111`) does not test end-to-end runtime failure economics in Exp 2/3 (invalid-message retries, NAK/ERR loops, degraded completion).
- **Exp 1 statistical fix remains partly cosmetic**: Reframing to "representative scenarios" and preregistering scenarios (`claude-response-1.md:123-126`) is better, but inferential testing on a hand-constructed scenario set still has limited generalization. This should be reported as benchmarked corpus performance, not population inference.
- **Authoring-bias fix introduces a new bias source**: "LLM generates all formats" (`claude-response-1.md:125`, `claude-response-1.md:129`) can import generator-model style bias into every condition unless generation is multi-model or template-constrained.

## 3) Pushbacks: Justified vs Evasive

- **"Drafts can be benchmarked" (`claude-response-1.md:28-29`)**: Justified, conditional on freezing an immutable spec+validator snapshot before runs.
- **"Perfect causal isolation is impossible" (`claude-response-1.md:45-46`)**: Partly justified, partly evasive. True in absolute terms; not an excuse for leaving major attribution confounds unmodeled.
- **"LLM-judge-only can publish" (`claude-response-1.md:51-52`)**: Partly justified as precedent; evasive as a validity defense. Precedent does not remove bias/reliability requirements for your specific claims.
- **"n=20 can be publishable" (`claude-response-1.md:69`)**: Justified if claims are narrow and power-checked; currently missing the latter.
- **"Cheap study is fine if honestly scoped" (`claude-response-1.md:71-76`)**: Partly justified. But the earlier concern was not cost alone; it was underpower + overreach risk.
- **"Debate experiment stays" (`claude-response-1.md:152-153`)**: Justified. Keeping it as applied evaluation (not headline evidence) is the correct compromise.

## 4) New Issues Introduced by the Revised Plan

- **Condition explosion without endpoint discipline**: Exp 2 now effectively expands condition count (original 3 in `claude-proposal.md:35-40`; revised matrix 5 in `claude-response-1.md:97-103`) while still tracking many outcomes. This raises multiplicity and interpretation risk unless one primary endpoint is pre-specified.
- **Prompt-length matching can create a new fairness artifact**: "Same length" instruction matching (`claude-response-1.md:43`) may mechanically inflate English prompt overhead and bias gross-token comparisons unless prompt-cost handling is explicitly symmetric and pre-registered.
- **Interop asymmetry risk**: AXON gets explicit cross-model interop tests (`claude-response-1.md:106`), but equivalent cross-model comparators for non-AXON conditions are not specified, making "interop advantage" claims vulnerable.
- **Reliability metric misfit risk**: Cohen's kappa on two LLM calls (`claude-response-1.md:56`) may overstate reliability if raters are not genuinely independent.
- **Exp 3 remains underspecified despite becoming co-primary**: The original Exp 3 definition is still minimal (`claude-proposal.md:44-47`). Making it co-primary without detailed task protocol, fail states, and stopping rules introduces a new central weakness.

## 5) Final Assessment

**Not yet publishable.** The revision is substantially better, but still below publishable rigor for protocol-evaluation claims.

### Specific remaining blockers

- **Blocker 1: Conformance validity.** Freeze a full normative validator and require full-conformance pass criteria for Exp 0 gating, not syntax+tier only.
- **Blocker 2: Causal claim discipline.** Either further deconfound Exp 2 or explicitly narrow claims to bundle-level comparisons.
- **Blocker 3: Statistical precommitment.** Add explicit primary endpoints per experiment, power analysis for those endpoints, and multiplicity policy tied to the expanded condition matrix.
- **Blocker 4: Evaluation reliability.** Strengthen judge-independence design and enlarge human-validation subset enough to estimate agreement with useful confidence.
- **Blocker 5: Interop and robustness realism.** Expand beyond one model pair and move robustness/failure-economics evaluation into the primary runtime experiments (Exp 2/3), not just Exp 0.
- **Blocker 6: Exp 3 protocol detail.** Since Exp 3 is now co-primary, specify concrete task specs, success criteria, fail/retry handling, and termination logic at publication-grade detail.

If those six blockers are resolved in the next revision, the plan becomes plausibly publishable as a rigorous pilot protocol-engineering paper.
