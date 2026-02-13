# Exp 1 Plan — Claude Self-Review

> Self-critique of the Exp 1 Token Efficiency plan, conducted before Codex adversarial review.
> This serves as the baseline condition for Track B methodology evaluation.

## Strengths

1. **Data reuse is efficient** — leveraging 486 existing outputs avoids costly new LLM runs
2. **Semantic element taxonomy is concrete** — element-by-element tables for all 9 tasks make the scoring reproducible
3. **Statistical plan follows preregistration exactly** — mixed-effects model, Holm-Bonferroni, bootstrap CIs
4. **Calibration step** — ground-truth scoring of 18 outputs before full run catches judge prompt issues early

## Critique Points

### S01: Circular measurement risk (Major)
The primary metric is `tokens / semantic_elements_correctly_expressed`. But "correctly expressed" is judged by an LLM looking at the raw output — which means the judge needs to understand the format to extract elements. For AXON (`QRY(@a>@b): status(@srv)`), the judge must parse AXON-like syntax. For English ("Agent A asks Agent B..."), it reads naturally. **This may systematically bias element extraction in favor of English conditions**, because LLM judges understand English better than AXON notation. If the judge misses an element in AXON that is actually there, AXON's denominator shrinks, making its tokens/unit look worse.

**Mitigation**: The calibration step should catch this. But the bias could be subtle — judges might agree with each other while both being wrong about AXON.

### S02: Element count granularity mismatch (Minor)
L1 tasks have 4-5 elements, L3-03 has 22. The tokens/unit metric will be dominated by high-element tasks in the mixed-effects model. This is fine mathematically (random intercept for task absorbs it), but the interpretability suffers — "AXON saves 0.5 tokens per element" means very different things for a 4-element vs 22-element message.

### S03: Prompt overhead not captured (Major)
The preregistration lists "prompt token overhead per condition" as a secondary metric. The AXON system prompt is 48 lines; the free English prompt is 1 line. If we're measuring communication efficiency, we should arguably amortize the prompt overhead across messages. A format that saves 40% per message but costs 10x in prompt tokens only breaks even after ~25 messages. The plan mentions this as a secondary metric but doesn't specify how to integrate it into the primary analysis.

### S04: No new data generation means no repair cycle (Minor)
The preregistration mentions recovery latency (attempts needed to produce valid output after error feedback) under "Operationalized Definitions." By reusing Exp 0 data, we skip the repair cycle entirely. This is fine for Exp 1 specifically (token efficiency doesn't require repair), but worth noting that we're leaving that preregistered secondary endpoint unaddressed.

### S05: The density metric is undefined for zero-element outputs (Minor)
Question 8 in the plan identifies this but doesn't resolve it. If an output scores 0 elements, tokens/elements = infinity. The plan should specify: exclude from density metric, include in a separate "complete failure" count.

### S06: 2-judge vs 3-judge departs from FAIRNESS.md (Minor)
The plan argues that element presence is near-binary and 2 judges suffice. This is reasonable but FAIRNESS.md specifies 3-way judging explicitly. Even if we believe 2 is enough, we should either: (a) pre-register this deviation, or (b) use 3 judges and show that the third rarely breaks ties (empirical justification).

### S07: No visualization plan (Minor)
The plan describes statistical analyses but no visualizations. Token efficiency results are most compelling as box plots or density curves. Should specify: (a) tokens by condition (box plot), (b) tokens/element by condition (box plot), (c) element count vs tokens (scatter with condition coloring).

## Summary

| ID | Issue | Severity | Self-caught? |
|----|-------|----------|-------------|
| S01 | LLM judge bias toward English in element extraction | Major | Yes |
| S02 | Element count granularity varies 5.5x across tasks | Minor | Yes |
| S03 | Prompt overhead not integrated into primary analysis | Major | Yes |
| S04 | No repair cycle data collected | Minor | Yes |
| S05 | Density metric undefined for zero-element outputs | Minor | Yes |
| S06 | 2-judge deviates from FAIRNESS.md 3-way protocol | Minor | Yes |
| S07 | No visualization plan | Minor | Yes |
