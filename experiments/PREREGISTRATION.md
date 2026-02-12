# Experiment Pre-Registration

> Pre-registered analysis plan for the AXON evaluation experiments (Track A).
> Frozen before data collection begins.

## Study Overview

**Research Question**: Does AXON provide measurable advantages over controlled English, JSON function calling, and FIPA-ACL for agent-to-agent communication?

**Design**: 6 conditions × 9 tasks × N models, within-subjects (same model evaluated across all conditions).

### Conditions
1. Free-form English (baseline)
2. Structured English
3. Instruction-matched English
4. JSON Function Calling
5. FIPA-ACL
6. AXON

---

## Experiment 0: Learnability Gate

### Primary Endpoint
**Zero-shot format compliance rate**: Proportion of LLM outputs that pass condition-specific validation after seeing only the system prompt.

**Pass criterion**: AXON compliance rate must be ≥ 80% and not statistically worse than JSON FC (one-sided test, α = 0.05). If AXON fails this gate, remaining experiments are not run until the spec/prompt is revised.

### Secondary Endpoints
- Token count per valid output (cl100k_base encoding)
- Time to first valid output (latency)
- Error class distribution per condition
- Prompt token overhead per condition

---

## Experiment 1: Token Efficiency

### Primary Endpoint
**Tokens per semantic unit**: Ratio of token count to number of required semantic elements correctly expressed, measured across cl100k_base and o200k_base.

### Analysis Plan
- Pairwise comparisons: AXON vs each other condition
- Mixed-effects model: tokens ~ condition + (1|task) + (1|model)
- Report both raw token counts and density-adjusted measures

---

## Experiment 2: Parse Accuracy Under Noise

### Primary Endpoint
**Structural preservation rate**: Proportion of messages that retain correct structure after perturbation (character deletion, token swapping, truncation).

### Perturbation Protocol
- 5% character deletion rate
- Single token swap within message
- Truncation at 75% of original length
- Each perturbation applied independently

---

## Experiment 3: Compositionality

### Primary Endpoint
**Composition success rate**: Proportion of correctly composed multi-step messages (sequences, parallel, causal chains) as judged by the 3-way LLM panel.

### Secondary Endpoints
- Decomposability: Can a receiver correctly extract individual steps from a composed message?
- Nesting depth achievable before first error

---

## Experiment 4: Multi-Turn Coherence

### Primary Endpoint
**Conversation coherence score**: Average across the rubric dimensions (reply threading, context maintenance, performative appropriateness) over 5-turn conversations.

### Secondary Endpoints
- Reply-link accuracy (does re: correctly reference prior message id?)
- Performative transition validity (CFM/DNY only to truth-apt claims, ACC/REJ only to proposals)
- Context drift rate (does ctx stay consistent?)

---

## Experiment 5: Cross-Model Generalization

### Primary Endpoint
**Cross-model variance**: Standard deviation of compliance rates across model families, per condition.

### Analysis Plan
- Compare variance: Var(AXON) vs Var(other conditions) across models
- Report per-model breakdowns
- Flag conditions with high model sensitivity

---

## Statistical Analysis Plan

### Multiple Comparisons
- **Primary analysis**: Holm-Bonferroni correction across the 5 pairwise comparisons (AXON vs each other condition) per experiment
- **Family-wise error rate**: α = 0.05
- Report both corrected and uncorrected p-values

### Effect Sizes
- Cohen's d for pairwise comparisons
- 95% bootstrap confidence intervals (10,000 resamples, BCa method)

### Mixed-Effects Models
For multi-factor analyses:
```
outcome ~ condition + complexity_level + (1|task) + (1|model)
```
- condition: fixed effect (6 levels)
- complexity_level: fixed effect (3 levels)
- task: random intercept
- model: random intercept

### Power Analysis
- Target: 80% power to detect medium effect (d = 0.5)
- With 6 conditions, 9 tasks, and 3 runs per cell: N = 162 observations per condition
- Minimum: 2 model families × 9 tasks × 3 runs = 54 observations per condition
- Holm-Bonferroni adjusted power maintained by increasing runs if needed

---

## Operationalized Definitions

### Naturalness
Operationalized as the inverse of error burden:
- **Error rate**: Proportion of outputs failing validation
- **Error classes**: Structural, missing-element, type-mismatch, semantic
- **Recovery latency**: Number of attempts needed to produce valid output after error feedback
- **Schema-violation rate**: Proportion of outputs that parse but violate semantic constraints

### Auditability (Secondary)
- Can a human reviewer identify sender, receiver, intent, and content from the raw message?
- Measured on the 30-item human validation subset

### Composability (Secondary)
- Can the format express sequences, parallel actions, and causal chains?
- Measured by Experiment 3 composition success rate

### Formal Verifiability (Secondary)
- Can the format be mechanically validated without LLM assistance?
- Measured by parser/validator pass rate on valid outputs

---

## Reporting

### Required Reporting
- All primary and secondary endpoints with confidence intervals
- Full pairwise comparison tables
- Per-model breakdowns
- Prompt token counts per condition
- Raw data and analysis scripts made available

### Deviation Protocol
If the analysis plan must deviate from pre-registration:
1. Document deviation and rationale before analyzing affected data
2. Report both pre-registered and exploratory analyses
3. Label exploratory results clearly

### Negative Results
If AXON does not outperform baselines on primary endpoints, this is reported as a valid finding. The research question is empirical — confirming the null is informative.
