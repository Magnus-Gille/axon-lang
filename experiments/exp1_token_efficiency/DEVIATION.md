# Exp 1: Token Efficiency — Pre-Registration Deviation Addendum

> Frozen before any scoring or analysis begins.
> Documents all deviations from the original pre-registration (experiments/PREREGISTRATION.md).
> Required by the deviation protocol at PREREGISTRATION.md:158-162.

## Context

Exp 1 reuses the 486 outputs collected during Exp 0 (3 models x 6 conditions x 9 tasks x 3 runs).
The pre-registration defines a shared "6 x 9 x N" design with experiments measuring different
endpoints from the same output corpus. This addendum locks all Exp 1-specific scoring and
analysis decisions before any scoring begins.

---

## Deviation 1: Dual-Track Element Definitions

### Original (PREREGISTRATION.md)
The pre-registration specifies "tokens per semantic unit" as the primary endpoint but does not
operationalize what constitutes a "semantic unit."

### Deviation
Two parallel element tracks are defined:

**Track A (Confirmatory)**: Uses the original `expected_elements` from `experiments/exp0_learnability/tasks/tasks.json` exactly as specified. These are coarse-grained (e.g., L2-03 has 5 elements, L3-03 has 5). This track preserves the pre-registered denominator.

**Track B (Exploratory)**: Uses an expanded atomic decomposition where each countable fact is one element (e.g., L2-03 → 9 elements, L3-03 → 22 elements). This track provides higher-resolution density measurement but is labeled exploratory because the element definitions were created after data collection.

### Rationale
The original elements were designed for learnability checking (Exp 0), not information density measurement. Coarse elements like `receivers_multiple` (counting 3 distinct workers as 1 element) are inappropriate for a density metric. However, expanding elements post-hoc creates researcher degrees of freedom. The dual-track approach addresses both concerns.

### Reporting
Both tracks are reported in full. Only Track A supports confirmatory inference. Track B is clearly labeled exploratory throughout.

---

## Deviation 2: Inclusion of Invalid Outputs

### Original (RESULTS.md:51)
Exp 0 reported token efficiency on "valid outputs only."

### Deviation
Exp 1 primary analysis includes all outputs (valid and invalid) in the token efficiency calculation. Invalid outputs are scored for semantic elements normally — an output that fails format validation but contains recognizable elements gets partial element credit.

### Exception
Outputs scoring 0 semantic elements are excluded from the ratio (tokens/elements = undefined). These are counted separately as "complete failures" in a two-part analysis:
- Part 1: P(complete failure) by condition
- Part 2: tokens/elements conditional on elements > 0

### Sensitivity Analysis
A valid-only analysis is reported alongside as a sensitivity check.

---

## Deviation 3: Outcome Variable

### Original (PREREGISTRATION.md:44)
The pre-registered Exp 1 model is `tokens ~ condition + ...` (raw token counts).

### Deviation
The primary analysis uses `log(tokens_per_unit) ~ condition + complexity_level + (1|task) + (1|model)`. Raw token counts are reported as a secondary analysis per the original pre-registration.

### Rationale
The ratio `tokens/elements` is the scientifically meaningful metric for information density. The log transform handles right-skew inherent in ratio outcomes and makes multiplicative effects additive.

### Reporting
Both analyses reported:
1. `log(tokens_per_unit) ~ condition + complexity_level + (1|task) + (1|model)` — primary (deviation)
2. `tokens ~ condition + complexity_level + (1|task) + (1|model)` — secondary (prereg-faithful)

---

## Deviation 4: Complexity Level Fixed Effect

### Original (PREREGISTRATION.md:111)
The pre-registered model includes `complexity_level` as a fixed effect.

### Status
This is NOT a deviation — the original plan draft incorrectly omitted it. The Exp 1 model includes `complexity_level` (3 levels: L1, L2, L3) as a fixed effect, matching the pre-registration.

---

## Locked Scoring Protocol

The following scoring rules are frozen before any judge calls.

### Judge Panel (3-way, per FAIRNESS.md:32-46)
- **Judge A**: Claude Sonnet 4.5 (via `claude -p`)
- **Judge B**: GPT-5.3 Codex (via `codex exec`)
- **Judge C**: Randomly selected from {Judge A, Judge B} per item
- **Agreement rule**: Majority vote (2/3). Items with 3-way disagreement flagged for human review.

### Blinding (per FAIRNESS.md:89-91)
- Judge prompt does NOT include condition name or format label
- Outputs presented with format-neutral preamble: "The following is an agent-to-agent communication message."
- Post-hoc blinding analysis: regress judge scores on condition indicator controlling for ground-truth element presence to detect systematic bias

### Human Validation Subset (per FAIRNESS.md:49-60)
- 30 items: 5 per condition
- Selection: 1 per complexity level (L1, L2, L3) + 2 edge cases per condition
- Scored independently by human rater before LLM judge scoring begins
- Used to calibrate LLM judges and detect format-specific biases
- Target: >90% per-element agreement between human and LLM majority vote

### Element Scoring Rules
For each output, the judge marks each required element as:
- **PRESENT**: Element is expressed accurately (score = 1)
- **ABSENT**: Element is not expressed (score = 0)
- **INCORRECT**: Element is expressed but factually wrong (score = 0)

### Presence Criteria (addressing taxonomy vagueness)
- Identity elements: Any string/name identifying an agent counts as present. No specific name required unless task specifies one.
- Content-facts with unspecified values (e.g., "a specific repo"): Any concrete value counts as present. The check is presence, not correctness of invented values.
- Justification/reasoning: Any explanatory text accompanying a decision counts as present.

### Calibration
- Score 36 outputs as ground truth (2 per condition x 3 complexity levels x 2 validity states)
- Run all 3 judges on calibration set
- Compute per-element agreement: judge vs ground truth
- Threshold: >90% agreement required before proceeding to full scoring
- If below threshold: refine judge prompt and re-calibrate (max 2 iterations)

---

## Locked Statistical Analysis

### Primary Model (Track A — Confirmatory)
```
log(tokens_per_unit_A) ~ condition + complexity_level + (1|task) + (1|model)
```
Where `tokens_per_unit_A` uses Track A (prereg) element counts.

### Primary Model (Track B — Exploratory)
```
log(tokens_per_unit_B) ~ condition + complexity_level + (1|task) + (1|model)
```
Where `tokens_per_unit_B` uses Track B (expanded atomic) element counts.

### Secondary Model (Prereg-Faithful)
```
tokens ~ condition + complexity_level + (1|task) + (1|model)
```
Raw token counts, matching PREREGISTRATION.md:44 exactly.

### Pairwise Comparisons
5 comparisons: AXON vs {free_english, structured_english, instruction_matched_english, json_fc, fipa_acl}
- Holm-Bonferroni correction (family-wise α = 0.05)
- Report both corrected and uncorrected p-values

### Effect Sizes
- Cohen's d for each pairwise comparison
- 95% bootstrap CI (10,000 resamples, BCa method)
- Block bootstrap: resample at (task × model) level to preserve dependency structure

### Two-Part Analysis for Invalid Outputs
- Part 1: Logistic model for P(elements = 0) ~ condition
- Part 2: Mixed model on subset where elements > 0

### Prompt Overhead (Secondary)
- Report system prompt token counts per condition (cl100k_base, o200k_base)
- Compute breakeven: messages_needed = prompt_overhead_difference / per_message_savings
- Not integrated into primary metric (prompt is fixed cost, per-message is variable)

### Encodings
All analyses run independently on cl100k_base (primary) and o200k_base (secondary).

### Visualizations
1. Box plot: raw tokens by condition
2. Box plot: tokens/element by condition (both tracks)
3. Scatter: element count vs tokens by condition (density curves)
4. Forest plot: pairwise effect sizes with CIs
5. Bar chart: prompt overhead by condition with breakeven annotation

---

## Sample Size

- Current: 81 observations per condition (3 models × 9 tasks × 3 runs)
- Pre-registered minimum: 54 (met)
- Pre-registered target: 162 (not met)
- If observed effect for primary endpoint is d < 0.5, additional runs will be collected before drawing conclusions (documented as sequential decision rule, not post-hoc)

---

## Checksums

This document is frozen at the time of creation. Any subsequent changes must be appended as amendments with rationale, not edits to existing text.

Frozen: 2026-02-13

---

## Amendment 1: Hybrid Scoring Governance (2026-02-13)

> Appended per deviation protocol. Does not modify any frozen text above.
> Rationale: Senior research advisor feedback + Claude↔Codex adversarial debate (see `debate/advisor-feedback-summary.md`).

### Problem

The original scoring protocol (§ Locked Scoring Protocol above) sends all outputs to a 3-judge LLM panel regardless of condition. This creates a construct-validity vulnerability: the primary endpoint denominator (semantic element count) is condition-invariant only if LLM judges are equally reliable across formats. For structured formats (AXON, JSON FC, FIPA-ACL), automated extraction is feasible and more objective.

### Amendment: Per-Condition Scoring Contract

Scoring now uses a **hybrid approach**: automated extraction where feasible, LLM judges where required.

#### Machine-Scored Conditions (AXON, JSON FC, FIPA-ACL)
- **Primary method**: Automated semantic element extraction via format-specific parsers
- Extractors defined in `scoring/extractors.py`
- Each element scored as PRESENT/ABSENT based on parser output
- No LLM involvement in primary scoring for these conditions

#### Judge-Scored Conditions (Free English, Structured English, Instruction-matched English)
- **Primary method**: 3-judge LLM panel (unchanged from above)
- All elements scored by judges per the original protocol
- Judge prompt, blinding, and agreement rules unchanged

#### Scoring Contract Details
- Full contract in `scoring/scoring_contract.json`
- For each condition: specifies extraction method per element category (identity, intent, content-fact, structural, metadata, threading)
- English conditions: all judge-scored
- Structured conditions: all machine-scored (with text-search fallback for content-fact elements)

### Cross-Validation Protocol

To ensure machine scoring and judge scoring are comparable:

1. **Machine-judge cross-validation subset**: 30 structured-format outputs (10 per format) also scored by the 3-judge panel
   - Selection: stratified by task (1 per task × 3 formats + 1 extra per format from L3)
   - Agreement threshold: ≥90% per-element agreement between machine and judge majority vote
   - If below threshold: review extraction rules, fix bugs, expand subset

2. **Human validation subset**: 30 items (5 per condition) scored by human rater (unchanged)
   - Expansion trigger: if any condition drops below 80% human-machine/judge agreement, expand to 10 items for that condition (max 60 total)
   - Trigger is pre-locked; no post-hoc flexibility

### Reporting Requirements

1. Report extraction method per condition in methods section
2. Report machine-judge agreement rates on cross-validation subset
3. Report human-judge agreement rates on human validation subset
4. Flag any element where machine and judge disagree on >10% of cross-validation outputs
5. Report primary metric using:
   - Machine-extracted element counts for structured formats
   - Judge-scored element counts for English formats
6. Sensitivity analysis: all-judge scoring on cross-validation subset (demonstrates equivalence)

### Impact on Primary Endpoint

The primary endpoint formula is unchanged: `log(tokens_per_unit) ~ condition + complexity_level + (1|task) + (1|model)`.

The denominator source differs by condition family:
- Structured formats: machine-extracted element count
- English formats: judge-scored element count

This is methodologically stronger than all-judge scoring because:
- It removes LLM-judge variability from 3/6 conditions
- It makes the denominator objectively verifiable for structured formats
- It reduces total judge calls by ~50%, enabling faster scoring
- Cross-validation demonstrates that machine and judge scoring agree

### Paper A Framing

Per advisor feedback and debate consensus: the active publication target is **Paper A: "Benchmarking agent communication formats for LLM-to-LLM communication"**. AXON is one candidate format; the primary contribution is the controlled evaluation methodology and results. Language design claims are supporting context, not the headline.

Frozen: 2026-02-13
