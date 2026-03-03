# Experiment 3: Compositionality — Results

**Generated**: 2026-03-03T11:45:27.043569
**Grammar version**: v0.1b
**Total records**: 567

## Summary

| Condition | N | Comp Rate | Elem Rate | Nesting Depth |
|-----------|---|-----------|-----------|---------------|
| free_english | 81 | 95.0% | 98.4% | 0.0 |
| structured_english | 81 | 96.2% | 95.0% | 0.0 |
| instruction_matched_english | 81 | 94.6% | 98.0% | 0.0 |
| json_fc | 81 | 75.4% | 32.2% | 0.0 |
| fipa_acl | 81 | 83.5% | 41.5% | 0.0 |
| axon | 81 | 66.2% | 44.5% | 1.8 |
| aisp (exploratory) | 81 | 73.7% | 89.6% | 0.0 |

## Version Provenance

Data collected using AXON grammar v0.1b (with arithmetic operators).
Exp 1 used v0.1a. The main difference is additional precedence levels
for `+`, `-`, `*`, `/` and the `==` alias for `=`.

See `experiments/exp1_token_efficiency/RESULTS.md` for v0.1a results.
