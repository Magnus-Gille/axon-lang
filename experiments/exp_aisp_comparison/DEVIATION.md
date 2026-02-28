# Pre-Registration Deviation Notice

> **Date**: 2026-02-27
> **Original pre-registration**: `experiments/PREREGISTRATION.md`
> **Type**: Exploratory addition (does not modify confirmatory analysis)

---

## Deviation

### What changed

A 7th experimental condition — **AISP** (AI Symbolic Programming, v5.1) — is added to the Exp 1 token efficiency experiment.

### Why

AISP (github.com/bar181/aisp-open-core) is a contemporaneous project making claims in the same problem space as AXON. Adding it as a benchmark condition:

1. Provides empirical comparison with a real-world alternative
2. Tests whether Unicode-symbol-based notation offers efficiency advantages
3. Strengthens the paper by including a broader comparison set
4. Demonstrates the experiment infrastructure's extensibility

### What is NOT changed

- **Conditions 1-6**: All original conditions remain unchanged
- **Confirmatory analysis**: AXON vs conditions 1-5 pairwise comparisons remain as pre-registered
- **Statistical corrections**: The original 5 Holm-Bonferroni comparisons are reported separately
- **Primary metric**: tok/unit (tokens per semantic element) remains the primary metric
- **Scoring methods**: Existing conditions retain their original scoring methods

### What is added

- AISP as condition 7 with judge-based scoring (same method as English conditions)
- 81 new cells (3 models × 9 tasks × 3 runs)
- Exploratory pairwise comparison: AXON vs AISP
- Updated Holm-Bonferroni for 6 comparisons (reported separately from confirmatory 5)

### Reporting protocol

All AISP results will be:
1. **Clearly labeled as exploratory** in all tables and figures
2. **Reported in a separate section** from confirmatory results
3. **Not included in the primary Holm-Bonferroni correction** (which remains at 5 comparisons)
4. **Accompanied by a secondary analysis** that includes all 7 conditions with 6-comparison correction

### Rationale for exploratory (not confirmatory) status

The pre-registration was frozen before AISP was identified as a comparison target. Adding it post-hoc as a confirmatory condition would undermine the pre-registration's integrity. Exploratory status is the methodologically correct classification.

---

## Timeline

- **Pre-registration frozen**: Before Exp 0 data collection (2026-02-12)
- **AISP identified**: 2026-02-27
- **AISP condition added**: 2026-02-27
- **Deviation documented**: This file, same date
