# AISP Comparison Benchmark Design

> **Date**: 2026-02-27
> **Status**: Design phase
> **Pre-registration note**: AISP is added as an exploratory 7th condition, not part of the original pre-registered design. See `DEVIATION.md` for formal deviation notice.

---

## Overview

Three benchmarks evaluate AISP alongside AXON and existing conditions:

| Benchmark | What it measures | Effort |
|-----------|-----------------|--------|
| **A**: 7th Experimental Condition | Token efficiency in agent communication tasks | High (81 new cells) |
| **B**: Parsing & Validation Rigor | Error detection on malformed inputs | Low (20 test cases) |
| **C**: Methodology Rigor Audit | Research methodology quality | Low (rubric scoring) |

---

## Benchmark A: AISP as 7th Experimental Condition

### Design

Add AISP to the existing Exp 1 token efficiency experiment.

- **Conditions**: 7 (existing 6 + AISP)
- **Models**: 3 (Claude Haiku, Claude Sonnet, Codex)
- **Tasks**: 9 (L1-01 through L3-03, same as Exp 1)
- **Runs**: 3 per cell
- **New cells**: 3 × 9 × 3 = 81
- **Existing cells**: 486 (reused from Exp 1)
- **Total for analysis**: 567

### AISP System Prompt Design

The AISP system prompt must satisfy FAIRNESS.md constraints:
- **Token budget**: Within 8:1 ratio of the baseline free English prompt
- **Metadata equivalence**: Must support id, reply-to, timestamp, protocol version
- **One-shot format**: System prompt only (no fine-tuning)

**Prompt source material**: Derived from AISP's `CHEATSHEET.md` and `AI_GUIDE.md`, adapted for agent communication tasks.

**Challenge**: AISP is designed for document specifications, not agent messages. The prompt must bridge this gap by instructing models to use AISP notation for inter-agent communication — which is not AISP's intended use case. This is noted as a design limitation.

### Scoring Method

AISP outputs will be scored using the **judge panel method** (same as English conditions) because:
1. No AISP parser exists that produces an AST
2. The substring-matching validator cannot extract semantic elements
3. Judge-based scoring is the fair approach for formats without machine-extractable structure

Scoring contract entry:
```json
{
  "aisp": {
    "primary_method": "judge",
    "parser": "none — AISP has no parser that produces an AST",
    "extraction_rules": {
      "identity": "judge — check if sender/receiver agents are identified",
      "intent": "judge — check if communicative intent is expressed using AISP notation",
      "content-fact": "judge — check if specific values are present in AISP blocks",
      "structural": "judge — check if sequences/causation are expressed",
      "metadata": "judge — check if IDs/timestamps are present in any form",
      "threading": "judge — check if reply references exist"
    },
    "judge_fallback": "All elements scored by judge panel (no machine extraction possible)."
  }
}
```

### Statistical Analysis

AISP comparisons are **exploratory** (not confirmatory):

1. **Descriptive statistics**: Mean tok/unit for AISP alongside other conditions
2. **Pairwise comparison**: AXON vs AISP (Welch's t-test, Cohen's d, bootstrap CI)
3. **Holm-Bonferroni update**: 6 comparisons instead of 5 (AXON vs each of 6 conditions)
4. **Reporting**: Clearly labeled as "exploratory post-hoc comparison" in results

### Infrastructure Changes

| File | Change |
|------|--------|
| `experiments/lib/condition_adapter.py` | Add `"aisp"` to CONDITIONS, add `_validate_aisp()` |
| `experiments/exp0_learnability/prompts/aisp.txt` | NEW: AISP system prompt |
| `experiments/exp1_token_efficiency/scoring/scoring_contract.json` | Add `"aisp"` entry |
| `experiments/exp1_token_efficiency/analysis/analyze.py` | Add `"aisp"` to CONDITIONS |

---

## Benchmark B: Parsing & Validation Rigor

### Design

Feed 20 intentionally malformed inputs to both AXON's parser and AISP's validator. Measure detection capability.

### Test Cases

| Category | # | Description | Expected: AXON | Expected: AISP |
|----------|---|-------------|----------------|----------------|
| Missing required structure | 4 | Messages without routing, metadata, or content | REJECT | ACCEPT (no routing concept) |
| Type mismatches | 4 | Wrong types in expected positions (string where number expected) | REJECT | ACCEPT (no type checking) |
| Syntax errors | 4 | Unclosed delimiters, missing colons, bad escapes | REJECT | ACCEPT (no parsing) |
| Semantic violations | 4 | Undefined references, duplicate keys, invalid performatives | REJECT (Tier 2+) | ACCEPT (no semantic checking) |
| Edge cases | 4 | Empty input, whitespace only, 1MB input, binary data | REJECT | MIXED (empty may fail block check) |

### Metrics

For each test case:
1. **Detection**: Did the tool reject the input? (binary)
2. **Error specificity** (0-2): 0 = no error message, 1 = generic error, 2 = specific error with location
3. **Error location** (0-2): 0 = no location, 1 = approximate (line), 2 = precise (line + column)

### Scoring

- **Detection rate**: rejected / total (per tool)
- **Mean error specificity**: average of specificity scores
- **Mean error location precision**: average of location scores

### Predictions (testable)

1. AXON parser will reject ≥18/20 malformed inputs (90%+ detection)
2. AISP validator will accept ≥16/20 malformed inputs (≤20% detection)
3. AXON will achieve mean error specificity ≥1.5
4. AISP will achieve mean error specificity ≤0.5

### Implementation

```python
# Pseudocode for Benchmark B runner
MALFORMED_INPUTS = [...]  # 20 test cases defined in test_cases.json

for test_case in MALFORMED_INPUTS:
    # Test AXON
    axon_result = run_axon_parser(test_case["input"])
    record_result("axon", test_case["id"], axon_result)

    # Test AISP
    aisp_result = run_aisp_validator(test_case["input"])
    record_result("aisp", test_case["id"], aisp_result)
```

For AISP testing: `npx aisp-validator <input_file>` or programmatic import of the npm package.

---

## Benchmark C: Methodology Rigor Audit

### Design

A 10-item research methodology rubric applied to both projects. Each item scored 0-2.

### Rubric

| # | Item | 0 | 1 | 2 |
|---|------|---|---|---|
| 1 | Pre-registration | None | Informal plan | Formal pre-registration with frozen analysis plan |
| 2 | Controlled comparison | None | Single baseline | Multiple controlled baselines |
| 3 | Blinding | None | Partial blinding | Full blinding (judges don't know condition) |
| 4 | Multiple models | None | 1 model | 3+ models |
| 5 | Replication | None | 2 runs | 3+ runs per cell |
| 6 | Statistical analysis | None | Descriptive only | Inferential with multiple comparison correction |
| 7 | Adversarial review | None | Self-review | Structured cross-model adversarial review |
| 8 | Fairness protocol | None | Informal considerations | Documented protocol with specific constraints |
| 9 | Quantified claims with CIs | None | Point estimates only | Effect sizes with confidence intervals |
| 10 | Negative result commitment | None | Implied | Explicit pre-commitment to publish null results |

### Scoring

| Item | AXON | Justification | AISP | Justification |
|------|------|---------------|------|---------------|
| 1. Pre-registration | 2 | PREREGISTRATION.md frozen before data collection | 0 | No pre-registration |
| 2. Controlled comparison | 2 | 5 controlled baselines (3 English + JSON FC + FIPA-ACL) | 0 | Comparison to undefined "traditional prose" |
| 3. Blinding | 2 | FAIRNESS.md: judges don't see condition labels | 0 | No evaluation procedure |
| 4. Multiple models | 2 | 3 models (Haiku, Sonnet, Codex) | 0 | No experiments with any model |
| 5. Replication | 2 | 3 runs per cell, 3x Exp 0 replications | 0 | No experiments |
| 6. Statistical analysis | 2 | Welch's t, Holm-Bonferroni, Cohen's d, bootstrap CIs, mixed-effects | 0 | No statistics |
| 7. Adversarial review | 2 | Claude↔Codex structured debates, ~100 critique points | 0 | No review process |
| 8. Fairness protocol | 2 | FAIRNESS.md: prompt budgets, metadata equivalence, 3-judge panel | 0 | No protocol |
| 9. Quantified claims + CIs | 2 | "~32%, d=-0.43, CI [-0.73, -0.13]" | 0 | "97x" with no CI, no methodology |
| 10. Negative result commitment | 2 | Explicit in PREREGISTRATION.md | 0 | No commitment |
| **Total** | **20/20** | | **0/20** | |

### Interpretation

The rubric measures adherence to standard research methodology practices. A score of 0/20 does not mean AISP is worthless — it means AISP's claims are unaccompanied by standard evidence. The rubric itself becomes a finding: it demonstrates the difference between marketing claims and research-backed claims in the agent communication space.

### Independence

The rubric items are drawn from standard research methodology checklists (pre-registration, blinding, replication, etc.). They are not designed to favor AXON — any project following standard methodology would score well. The rubric could be applied to any project in this space.

---

## Execution Timeline

| Step | Benchmark | Estimated Time | Dependencies |
|------|-----------|---------------|--------------|
| 1 | C: Methodology audit | 30 min | None (documentation review) |
| 2 | B: Malformed input tests | 2-3 hrs | AISP validator installed |
| 3 | A: Infrastructure changes | 2-3 hrs | None |
| 4 | A: System prompt design | 1-2 hrs | AISP documentation review |
| 5 | A: Generate 81 cells | 3-4 hrs | Steps 3-4 complete |
| 6 | A: Score with judges | 2-3 hrs | Step 5 complete |
| 7 | A: Statistical analysis | 1 hr | Step 6 complete |

**Critical path**: Steps 1-2 can run in parallel with Steps 3-4.

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| AISP isn't designed for agent messages | Models may struggle to produce AISP for communication tasks | Document as design limitation; this itself is a finding |
| AISP system prompt is too long | Unfair token overhead | Cap at FAIRNESS.md 8:1 ratio; report overhead separately |
| AISP produces outputs that look like English with some Unicode | Hard to score consistently | Judge panel handles this; cross-validate with human scoring |
| "Adding a 7th condition is post-hoc" | Threatens statistical credibility | Clear DEVIATION.md labeling; separate from confirmatory analysis |
| AISP validator is too trivial for Benchmark B | Results are obvious | Predictions documented a priori; obvious results are still publishable findings |
