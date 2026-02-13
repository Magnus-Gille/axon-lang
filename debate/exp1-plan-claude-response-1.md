# Exp 1 Plan — Claude Response to Codex Critique (Round 1)

## Concessions

### C1: Element count mismatch with Exp 0 task specs is a real problem
**Codex is right.** The Exp 0 `tasks.json` defines expected_elements as coarse-grained (e.g., L2-03 has 5 elements, L3-03 has 5), while my Exp 1 plan expands these to fine-grained counts (9 and 22 respectively). This is a post-hoc redesign of the denominator that changes which condition wins. I was solving the right problem (Exp 0's elements are too coarse for density measurement) but in the wrong way (silently redefining them).

**Fix**: Create an explicit `element_annotations.json` that documents the Exp 1-specific element decomposition, with a clear rationale for each expansion. Cross-reference Exp 0's original elements. File a formal pre-registration deviation per `PREREGISTRATION.md:159` before any scoring begins.

### C2: Must use 3-judge panel per FAIRNESS.md
**Codex is right.** The fairness protocol at `FAIRNESS.md:32-46` commits to 3-way judging with majority vote. My rationale that "element presence is near-binary" doesn't override a frozen commitment. Even if we believe 2 judges suffice, we should demonstrate it empirically rather than assume it.

**Fix**: Use the full 3-judge panel (Claude + GPT + random tiebreaker). Report inter-judge agreement. If agreement is >95% on the element checklist, note this as evidence that future experiments could safely use 2 judges.

### C3: Must add condition blinding for judges
**Codex is right.** `FAIRNESS.md:89-91` requires judges to evaluate without knowing which condition produced the output. My plan presents raw outputs with format signals intact (AXON syntax vs JSON vs English), making the condition immediately obvious.

**Fix**: For structured formats, present outputs with a format-neutral preamble: "The following is an agent message. Score whether each required element is present." The format will still be recognizable (can't fully blind AXON syntax from JSON), but we can avoid priming the judge with condition labels. Report a blinding analysis: does judge scoring correlate with condition after controlling for actual element presence?

### C4: Missing `complexity_level` fixed effect
**Codex is right.** The pre-registration at `PREREGISTRATION.md:111` specifies `outcome ~ condition + complexity_level + (1|task) + (1|model)`. My plan at line 260 drops `complexity_level`. Given the strong L1/L2/L3 heterogeneity (4 vs 11 vs 22 elements), this is a substantive omission.

**Fix**: Add `complexity_level` as a fixed effect in the primary model. Run both with and without as a sensitivity check.

### C5: Statistical model needs distributional specification
**Codex is right** that a ratio outcome with structural zeros needs pre-specified handling. Linear mixed-effects on a raw ratio is problematic: the ratio is bounded below by 0, potentially right-skewed, and undefined when elements = 0.

**Fix**: Pre-specify: (a) log-transform `tokens_per_unit` for the primary analysis (handles skew, makes multiplicative effects additive); (b) exclude zero-element outputs from ratio analysis, count them separately as "complete failures"; (c) run raw-ratio LMM as sensitivity analysis. Document before scoring begins.

### C6: Bootstrap resampling unit must be specified
**Codex is right** — naive row-level bootstrap breaks within-task and within-model correlations.

**Fix**: Block bootstrap resampling at the (task × model) level, preserving the dependency structure. Specify this before analysis.

## Partial Concessions

### P1: Post-hoc analytic flexibility — valid concern, but addressable
Codex flags that defining scoring machinery after data exists creates researcher degrees of freedom. This is a genuine risk. However, the key distinction is:
- Data **collection** happened in Exp 0 (frozen, can't be re-run differently)
- Scoring **rubric** is being defined now (before scoring, before analysis)

The pre-registration deviation protocol at `PREREGISTRATION.md:158-162` explicitly anticipates this: "Document deviation and rationale **before analyzing affected data**." As long as we lock the element rubric, judge protocol, and statistical model *before any scoring runs*, this is a legitimate deviation, not p-hacking.

**Action**: File a formal deviation document before scoring. Include: (a) the expanded element taxonomy with rationale, (b) the decision to include invalid outputs, (c) the 3-judge protocol specification. Freeze this document before any judge calls.

### P2: L3-03's 22-element decomposition — partially valid
Codex correctly notes that 22 elements (mostly metadata/threading) makes L3-03 a "metadata compression score" rather than a "semantic communication efficiency" score. This is a real concern for L3-03 specifically.

However, I disagree that this is purely inflation. The task instruction *explicitly requires* IDs, versions, timestamps, and reply-to links — these are real information that must be encoded, and different formats encode them at very different token costs. AXON's `[id:"m1", %%:1, re:"m2", ts:1234567890]` is far more compact than JSON's `{"id": "m1", "protocol_version": 1, "reply_to": "m2", "timestamp": 1234567890}`.

**Compromise**: Report L3-03 both ways: (a) all 22 elements including metadata, (b) content elements only (~10 elements excluding metadata/threading). This separates "format overhead for metadata" from "format efficiency for semantic content."

### P3: Sample size at 81 — adequate but not ideal
Codex correctly notes 81 < 162 (target). However, 81 > 54 (minimum per prereg). The question is whether 81 gives adequate power for the expected effect.

Exp 0 preliminary data shows AXON mean = 74.4 tokens vs JSON FC mean = 126.0 tokens — a 41% difference. For the density-adjusted metric, the effect may be even larger. This is well above a medium effect (d=0.5). Power at n=81 for a large effect (d=0.8) with 6 conditions exceeds 90%.

**Action**: Report post-hoc power analysis alongside results. If the observed effect is smaller than expected, flag that additional runs are needed and run them before drawing conclusions.

### P4: Element taxonomy vagueness ("some repo", "any")
Codex is right that phrases like "some repo identifier" and "Receiver (any)" are non-deterministic. However, these are presence checks, not correctness checks — the task instruction says "a specific repo branch and commit" without specifying actual values. The LLM invents values; we check whether *any* value was provided.

**Partial fix**: Rephrase as explicit presence criteria: "A repository identifier is present (any string/name)" rather than "Some repo identifier." For L3-02's "Receiver (any)", change to "A receiving agent is specified (any identifier)" with a note that the task doesn't constrain the receiver name.

## Defenses

### D1: Data reuse is methodologically sound
Codex says reuse is "only partially defensible." I disagree — it's the standard approach in multi-endpoint studies. The pre-registration defines a single "6 × 9 × N" design (`PREREGISTRATION.md:10`) with experiments measuring different endpoints from shared data. This is exactly how clinical trial pre-registrations work: one data collection, multiple pre-specified endpoints.

The changed estimand concern (including invalids) is valid but is a deviation to be documented, not a reason to reject reuse entirely. The core data (model outputs) are the same regardless of whether we score only valid or all outputs.

### D2: Prompt overhead as secondary (not primary) metric is appropriate
Codex flags that the primary metric ignores prompt overhead. However, prompt overhead is a **fixed cost** amortized over all messages in a conversation, while token efficiency is a **per-message variable cost**. In a 100-message conversation, the prompt is sent once; each message is a separate cost.

The appropriate analysis is: (a) report per-message efficiency as primary (this is what scales), (b) report prompt overhead as secondary, (c) compute breakeven point (at what conversation length does AXON's lower per-message cost offset its higher prompt cost?). This is already in the plan as a secondary metric.

### D3: Element expansion is necessary, not inflation
The Exp 0 `expected_elements` were designed for learnability checking ("did the model include a sender?"), not for information density measurement. `receivers_multiple` as a single element for 3 distinct workers is fundamentally wrong for a density metric — it would count "3 workers" the same as "1 worker." The expansion to 3 identity elements for 3 workers is a correction, not inflation.

The key principle (from the plan's "Atomicity" rule, line 56): each countable fact is one element. This is not post-hoc convenience — it's the definition the density metric requires.

## Revised Positions Table

| Issue | Original Position | Revised Position | Change Type |
|-------|-------------------|------------------|-------------|
| Judge panel | 2-judge | 3-judge per FAIRNESS.md | Concession |
| Blinding | Raw outputs | Format-neutral presentation + blinding analysis | Concession |
| Complexity level | Omitted from model | Include as fixed effect | Concession |
| Ratio handling | Unspecified | Log-transform primary, raw ratio sensitivity | Concession |
| Bootstrap unit | Unspecified | Block bootstrap at task×model level | Concession |
| Element counts | Silently expanded | Explicit deviation document with rationale | Concession |
| L3-03 elements | 22 elements | Report both 22 (full) and ~10 (content-only) | Partial concession |
| Sample size | "Sufficient" | Report power analysis, run more if underpowered | Partial concession |
| Taxonomy wording | Vague presence | Explicit presence criteria with examples | Partial concession |
| Post-hoc flexibility | Not addressed | File formal deviation before scoring | Partial concession |
| Data reuse | Fully defensible | Still defensible — standard multi-endpoint design | Defended |
| Prompt overhead | Secondary only | Secondary with breakeven analysis | Defended |
| Element expansion | Implicit | Necessary for density metric, not inflation | Defended |
