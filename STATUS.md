# AXON Project Status

**Last session:** 2026-03-01
**Branch:** main
**Latest commit:** 2d39926

## Completed This Session
- Ran Exp 1 full statistical analysis (analyze.py --all)
- Added version provenance to RESULTS.md — data collected on v0.1a (7-level grammar), grammar extended to v0.1b (9-level) 13 days later
- Results support the reliability pivot: AXON wins on zero failures + structured-format efficiency, not raw token savings over English

## Key Statistical Results (v0.1a grammar)
- **Mixed-effects model**: AXON significantly better than JSON FC (+0.407, p<0.001), FIPA-ACL (+0.269, p<0.001), Inst-matched (+0.216, p<0.001). Free English significantly better than AXON (-0.208, p<0.001) but has 11.1% failure rate.
- **Pairwise (Holm-Bonferroni)**: No comparisons survive correction (AXON vs JSON FC marginal at p=0.063)
- **Bootstrap CIs**: AXON vs JSON FC d=-0.43 [-0.67, -0.21], AXON vs FIPA-ACL d=-0.33 [-0.52, -0.12] — both exclude zero
- **Convergence warnings**: Group variance ~0 (only 3 model groups), Hessian not positive definite
- **Prompt overhead**: AXON 529 tok (v0.1a) / 580 tok (v0.1b) vs JSON FC 205 tok → breakeven ~6-7 messages

## In Progress
- Human validation: Items 1-7 complete (100% agreement), items 8-30 remaining

## Next Steps (prioritized)
1. Finish human validation (items 8-30)
2. Run `--human-score` after sheet complete
3. Design Exp 3 (compositionality/repair dynamics) — biggest evidence gap per debate
4. Build AXON↔A2A field mapping table — resolve Tier 1 routing overlap
5. Generate AISP Benchmark A cells (81 cells across 3 models)
6. Reframe paper: reliability/correctness primary, token efficiency secondary

## Blockers
- None
