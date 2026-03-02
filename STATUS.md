# AXON Project Status

**Last session:** 2026-03-02
**Branch:** main
**Latest commit:** c06fb58

## Completed This Session
- Scored all 567 Exp 3 outputs (machine scoring: AXON AST + text extraction)
- Ran full statistical analysis (GLMM + pairwise + interaction + nesting depth)

## Key Results — Exp 3 Composition Scoring
- **AXON: 66.2% composition rate** — highest of all conditions
- 4/5 prereg comparisons significant after Holm correction:
  - AXON vs JSON FC: +41.2%, d=1.05, p<0.0001 ***
  - AXON vs FIPA-ACL: +21.8%, d=0.54, p=0.005 **
  - AXON vs Inst-Matched: +20.0%, d=0.50, p=0.007 **
  - AXON vs Free English: +14.8%, d=0.35, p=0.011 *
  - AXON vs Structured English: +5.2%, d=0.13, p=0.086 ns
- JSON FC: 27.2% failure rate, 24.9% composition rate — collapsed on Haiku
- Only AXON produces nesting (mean 1.87, max 5)
- Convergence caveat on primary model (same 3-model RE issue as Exp 1)

## Pending — English Judge Scoring
- ~3,500 elements need LLM judge scoring (English + AISP conditions)
- `--judge` flag in score.py is a stub — implementation needed
- Machine-scored conditions (AXON, JSON FC, FIPA-ACL) are complete

## In Progress
- Human validation: Items 1-7 complete (100% agreement), items 8-30 remaining

## Next Steps (prioritized)
1. **Implement judge scoring** for English/AISP conditions (~3500 elements)
2. **Re-run analysis** with complete dataset
3. Finish human validation (items 8-30)
4. Build AXON↔A2A field mapping table
5. Generate AISP Benchmark A cells (81 cells)
6. Reframe paper: reliability/correctness primary, token efficiency secondary

## Blockers
- None
