# Experimental Fairness Protocol

> Ensures no condition is systematically advantaged in the AXON evaluation experiments.

## 1. Symmetric Prompt Budget

All 6 conditions receive system prompts balanced on:

| Condition | Prompt | Budget Control |
|-----------|--------|----------------|
| Free-form English | Minimal framing | Baseline — shortest prompt |
| Structured English | Format template + example | Matched to AXON element count |
| Instruction-matched English | Speech acts + metadata template | Matched to AXON spec coverage |
| JSON Function Calling | JSON schema + field descriptions | Matched to AXON type coverage |
| FIPA-ACL | Performative list + ACL syntax | Matched to AXON performative count |
| AXON | Spec subset + syntax reference | Reference condition |

**Measurement**: Token count per prompt across `cl100k_base` and `o200k_base` encodings. Maximum allowed ratio between shortest and longest prompt: 8:1 (reflecting genuine information density differences, not unfair padding).

## 2. Metadata Envelope Equivalence

Every condition must encode equivalent metadata capabilities:
- Message identification (id)
- Reply threading (reply-to)
- Timestamps
- Protocol versioning

If a condition lacks native support for a metadata concept, the prompt must explain how to express it in that format.

## 3. LLM Judge Protocol

### 3-way Judging
Each output is evaluated by 3 independent LLM judges:
1. **Judge A**: Claude (Sonnet or Opus)
2. **Judge B**: GPT-4 family
3. **Judge C**: One of Judge A or B (randomly selected per item)

### Judge Instructions
Judges evaluate on a shared rubric:
- **Correctness**: Does the output express all required elements? (0-3)
- **Format compliance**: Is the output in the correct format for the condition? (0-3)
- **Completeness**: Are metadata and structural requirements met? (0-3)
- **Clarity**: Is the intent unambiguous to a receiving agent? (0-3)

### Agreement Threshold
- Primary metric uses majority vote (2/3 agreement)
- Items with 3-way disagreement are flagged for human review

## 4. Human Validation Subset

A 30-item subset (5 per condition) is independently scored by human raters to:
- Calibrate LLM judges against human judgment
- Detect systematic LLM judge biases for/against specific formats
- Validate the rubric's discriminative power

### Selection Criteria
Items are selected to cover:
- All 3 complexity levels (L1, L2, L3)
- At least 1 edge case per condition
- Both "clearly correct" and "borderline" outputs

## 5. Cross-Model Testing Scope

To avoid model-specific confounds, Exp 0 tests learnability across:
- At least 2 model families (e.g., Claude + GPT-4)
- At least 2 model sizes per family where available
- Temperature fixed at 0.0 for reproducibility
- 3 runs per (model, condition, task) to measure variance

## 6. Failure and Repair Metrics Symmetry

When measuring error rates and repair capabilities:
- **Error classes** are defined condition-independently:
  - Structural errors (wrong format entirely)
  - Missing required elements
  - Type mismatches
  - Semantic errors (wrong performative, wrong routing)
- **Recovery**: If an initial output fails validation, the LLM receives the same error feedback format across all conditions
- **Repair budget**: Same number of retry attempts (1) across all conditions

## 7. FIPA-ACL Adaptation Budget

FIPA-ACL is a legacy format not optimized for modern LLMs. To ensure fair comparison:
- The FIPA-ACL prompt receives a complete but concise syntax reference
- The prompt includes the same number of examples as other structured conditions
- FIPA-ACL results are reported both individually and as part of the "structured format" category
- Adaptation burden (prompt length needed to achieve equivalent learnability) is itself a measured outcome

## 8. Blinding

- Task descriptions are condition-neutral (no format-specific language in task instructions)
- LLM judges evaluate outputs without knowing which condition produced them (outputs are presented format-normalized where possible)
- Human validators receive outputs in randomized order without condition labels

## 9. Pre-commitment

This fairness protocol is frozen before any experimental runs. Changes after data collection require:
1. Documentation of the change and rationale
2. Re-running affected analyses
3. Reporting both original and modified results
