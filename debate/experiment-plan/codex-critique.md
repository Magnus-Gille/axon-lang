# Adversarial Critique of AXON Experimental Plan

*Reviewer: OpenAI Codex (GPT-5.3), running headless against Claude's proposal*

## 1. FATAL FLAWS (rejection-level)

- **Your core validity metric in Exp 0 is fundamentally wrong.** You use parser `validate()` as the gate metric, but `validate()` is just `parse()` success (`src/axon_parser.py:803-809`). It does **not** enforce AXON's normative constraints: compliance-tier required fields (`spec/SPECIFICATION.md:38-63`, `spec/SPECIFICATION.md:343-356`), performative transition rules (`spec/SPECIFICATION.md:130-139`), typing/operator admissibility (`spec/SPECIFICATION.md:321-327`), variable scope (`spec/SPECIFICATION.md:327`, `spec/SPECIFICATION.md:331-338`), or version handling semantics (`spec/SPECIFICATION.md:492-498`). So your gate does not test "can models produce valid AXON"; it tests "can models produce something parseable by a permissive parser." That is a construct-validity failure.

- **You are benchmarking a draft spec with unresolved internal inconsistencies and then treating results as publishable evidence.** The spec itself labels efficiency as hypothesis pending benchmarking (`spec/SPECIFICATION.md:5`, `spec/SPECIFICATION.md:517`) and even mixes incompatible metadata definitions (strict `meta_key` grammar at `spec/SPECIFICATION.md:253-258` vs profile fields like `txn_id`/`txn_state` in `spec/SPECIFICATION.md:532-543`). You are proposing performance claims before defining what "conformant AXON" even is.

- **Baseline fairness is broken in a way that can invalidate all efficiency claims.** AXON in your examples and plan is implicitly compared without mandatory operational envelope overhead. For multi-agent settings, Tier 2 is explicitly "recommended" and requires `re`, `ts`, `ctx` (`spec/SPECIFICATION.md:47-54`, `spec/SPECIFICATION.md:347-349`), and Tier 1 requires at least `id` and `%%` (`spec/SPECIFICATION.md:40-45`, `spec/SPECIFICATION.md:345-346`). If AXON omits these while English/JSON carry equivalent context, your token wins are artificially inflated.

- **Exp 2 confounds multiple interventions at once, so causal attribution is impossible.** AXON condition changes notation, grammar rigidity, explicit performatives, metadata conventions, and prompt instructions ("with spec in system prompt"). Structured English only partially controls one axis. If AXON wins, you still cannot tell whether gains came from symbolic compression, forced structure, tighter prompting, or shorter expected outputs.

- **LLM-judge-only quality evaluation is a major methodological liability for the primary claim.** You propose quality metrics (argument quality, semantic fidelity, conclusion quality) with no grounded rubric, no blind adjudication, no inter-rater reliability, and likely model-family bias if the judge shares priors with the debaters. That is weak evidence for any top-tier venue.

- **The sample sizes and statistical plan are not credible for the claims you want.** Exp 2 has 10 topics x 3 reps, yet outcomes are high variance and clustered by topic and seed. No power analysis, no mixed-effects modeling, no multiple-testing correction, no robustness checks. Exp 5 tries a power-law with only four `n` values (2/4/8/16), which is not enough to support exponent claims with confidence.

- **You are optimizing for a cheap story, not a defensible study.** "Minimum viable paper" at ~$20-30 (proposal line 58) is effectively an admission of underpowered experimentation. Reviewers will see this as pilot-scale evidence being overmarketed as publication-grade.

- **Your own prior comparison artifact is visibly biased and contaminates experiment design assumptions.** `examples/comparisons.md` uses caricatured verbose English, approximate token heuristics by character count, and declares a 66% average gain (`examples/comparisons.md:3`, `examples/comparisons.md:11-14`, `examples/comparisons.md:205-207`). If message construction follows the same style, Exp 1 is dead on arrival.

## 2. MAJOR CONCERNS

- **Task mismatch:** "Two Claude instances debating" is not clearly aligned to AXON's strongest design claims (protocol semantics, typed task coordination, explicit performatives). Debate quality is open-ended rhetoric, not structured coordination. You may be selecting a setting where AXON's intended advantages are weakest or unmeasurable.

- **Missing strongest baseline:** You still do not include the baseline your own research doc identifies as strongest: controlled English + function/tool calling (`RESEARCH.md:215-217`). "Structured English" is not equivalent to JSON mode / function calling guarantees.

- **No interoperability test despite interoperability framing:** AXON claims interop tiers, yet all experiments appear same-model/same-family. No cross-model matrix (Claude<->GPT<->open models), no parser portability, no independent implementation validation.

- **No reliability/robustness evaluation:** AXON defines protocol-level failures (`NAK`, `ERR`, version rejection) and recovery patterns (`spec/SPECIFICATION.md:449-455`, `spec/SPECIFICATION.md:457-475`, `spec/SPECIFICATION.md:492-498`), but experiments ignore malformed messages, partial compliance, retries, and degradation under error.

- **No measurement of protocol overhead in context windows:** If AXON requires repeated inclusion of spec/instructions to stay valid, cost accounting must include that control-plane overhead. If you exclude it, results are operationally misleading.

- **Statistical misfit in Exp 1:** Wilcoxon on a hand-authored fixed set of 40 messages is weak unless the set is sampled from a clear population and pre-registered. Otherwise p-values are decoration on deterministic engineering choices.

- **Potential data leakage / authoring bias:** Who writes "semantically equivalent" messages? If AXON proponents author both AXON and baselines, they can unconsciously compress AXON and bloat competitors.

- **No preregistration or anti-p-hacking guardrails:** Gate-based continuation (Exp 0 threshold to proceed) plus adaptive story pivot invites selective reporting.

- **No temporal stability controls:** Model/API versions drift; latency and cost metrics are unstable without date/version pinning and rerun strategy.

## 3. MINOR ISSUES

- "Semantic fidelity" is undefined in debate context (fidelity to what reference?).
- "Conclusion quality" is underspecified and likely topic-dependent.
- Latency measurements need network jitter controls and repeated call normalization.
- Temperature/top-p/seed settings are not specified; reproducibility will be poor.
- Six-turn fixed debates may create truncation artifacts and favor terse formats.
- Exp 3-5 are too underspecified to review seriously (task generation, success criteria, stopping conditions, fail states).
- Reporting plan lacks confidence intervals and effect-size interpretation thresholds.
- Parser line count ("934 lines") is not evidence of maturity.

## 4. WHAT'S GOOD

- Including a learnability gate before downstream claims is directionally right.
- Adding a Structured English control is the correct instinct for isolating structure effects.
- You explicitly acknowledge the "format restrictions may hurt reasoning" risk (proposal lines 42, 64), which is honest and important.
- Moving from toy char-count heuristics to real tokenizers in Exp 1 is necessary.
- You are at least attempting multi-agent and scaling experiments instead of stopping at static prompts.

## 5. SUGGESTED ADDITIONS

- **Conformance suite before any benchmark:** Build and report a validator that checks syntax + tier requirements + transition rules + typing constraints + version semantics. Parse-only is insufficient.
- **Tier-overhead ablation:** Evaluate AXON at Tier 1 vs Tier 2 vs Tier 3 (with mandatory metadata/signature fields) so efficiency claims reflect realistic deployment.
- **Baseline matrix that can survive review:**
  - Free English
  - Structured English
  - Controlled English + function calling / JSON mode
  - JSON+schema envelope
  - AXON
- **Budget-matched quality study:** Force equal output token budgets across conditions, then compare task quality. This isolates representational efficiency from "just write less" effects.
- **Cross-model interoperability:** Sender and receiver from different model families; judge independent from both.
- **Robustness battery:** malformed/partial messages, adversarial ambiguity prompts, missing metadata, unsupported version, and recovery behavior (`NAK`/retry).
- **Human + model evaluation:** Blind human raters for a subset; report inter-rater agreement and correlation with LLM-judge.
- **Pre-registration + fixed analysis plan:** hypotheses, primary endpoints, correction policy, exclusion rules, and stopping criteria.
- **Throughput + failure economics:** report not just token savings, but total cost including invalid-message retries, repair prompts, and control-plane overhead.

## 6. ALTERNATIVE FRAMING

Your current framing ("Does AXON improve debate?") is weak and easy to reject because debate quality is subjective and loosely tied to AXON's formal claims.

A stronger framing:

- **Primary question:** Under fixed semantic payload and reliability constraints, does AXON improve end-to-end task completion per token/cost compared to controlled-English and JSON-schema baselines?
- **Secondary question:** What is the adoption cost (learnability, failure rate, interoperability friction) of introducing AXON in mixed-model agent systems?

This reframes AXON as a **protocol engineering** contribution, not a rhetoric-format experiment. That is much closer to a publishable, falsifiable systems/NLP paper.
