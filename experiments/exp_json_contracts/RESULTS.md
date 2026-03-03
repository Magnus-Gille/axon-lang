# JSON + Contracts — Results

**Exploratory condition** (post-pre-registration). SEMAP-inspired behavioral contracts over JSON.

## Key Numbers

- **Composition rate**: 51.6%
- **Element rate**: 45.0%
- **Failure rate**: 0.0%
- **N**: 81 outputs

## Comparison

| Condition | Comp Rate | Fail Rate |
|-----------|-----------|-----------|
| axon | 67.0% | 1.2% |
| json_contracts | 51.6% | 0.0% |
| json_fc | 27.7% | 27.2% |
| fipa_acl | 47.0% | 9.9% |
| structured_english | 61.0% | 0.0% |
| free_english | 51.4% | 0.0% |
| instruction_matched_english | 46.2% | 0.0% |
| aisp | 35.6% | 0.0% |

## Interpretation

JSON+Contracts achieves 51.6% composition rate vs AXON's 67.0% and JSON FC's 27.7%.

Adding behavioral contracts (pre/postconditions, lifecycle stage, explicit step relations) to JSON improves compositionality over plain JSON FC, but does not close the gap with AXON's intrinsic composition operators.

This supports the intrinsic-vs-extrinsic compositionality distinction: format-level syntax for composition (`->`, `&`, `|`) is more effective than contract-level rules (`"relation": "sequence"`).
