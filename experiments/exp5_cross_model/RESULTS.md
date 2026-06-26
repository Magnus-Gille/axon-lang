# Experiment 5: Cross-Model Generalization — Results

**Generated**: 2026-03-02T09:04:40.242118

## Summary

Cross-model consistency analysis using Exp 1 (token efficiency) and
Exp 3 (compositionality) scored data. No new data collection.

### Token Efficiency (Exp 1) — Cross-Model SD

| Condition | SD (tok/unit) | CV |
|-----------|---------------|-----|
| free_english | 4.604 | 0.283 |
| structured_english | 2.524 | 0.159 |
| instruction_matched_english | 1.183 | 0.064 |
| json_fc | 2.213 | 0.098 |
| fipa_acl | 2.058 | 0.096 |
| axon | 0.484 | 0.031 |

### Compositionality (Exp 3) — Cross-Model SD

| Condition | SD (comp rate) | CV |
|-----------|----------------|-----|
| free_english | 0.237 | 0.462 |
| structured_english | 0.167 | 0.274 |
| instruction_matched_english | 0.061 | 0.131 |
| json_fc | 0.092 | 0.369 |
| fipa_acl | 0.099 | 0.223 |
| axon | 0.048 | 0.073 |
| aisp (exploratory) | 0.043 | 0.122 |

Lower SD = more consistent across models.
