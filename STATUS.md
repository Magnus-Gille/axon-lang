# AXON Project Status

**Last session:** 2026-03-02
**Branch:** main
**Latest commit:** 73cf8fd

## Completed This Session
- Scored all 567 Exp 3 outputs — machine scoring (c06fb58)
- Ran full Exp 3 statistical analysis — 4/5 prereg comparisons significant (c06fb58)
- Generated AISP Benchmark A — 81 cells, all valid (73cf8fd)
  - AISP: 394.6 tok mean — 5.1x more than AXON (76.8), 3.0x more than JSON FC (132.9)

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

## AISP Benchmark A — COMPLETE
- 81/81 cells valid across 3 models × 9 tasks × 3 runs
- AISP 5.1x more tokens than AXON — confirms hand-written Benchmark 1 ratio
- Data: `experiments/exp0_learnability/results/exp0_*_20260302_*.json`

## Pending — English Judge Scoring
- ~3,500 elements need LLM judge scoring (English + AISP conditions)
- `--judge` flag in score.py is a stub — implementation needed
- Machine-scored conditions (AXON, JSON FC, FIPA-ACL) are complete

## In Progress
- Human validation: Items 1-7 complete (100% agreement), items 8-30 remaining

## Next Steps (prioritized)
1. **Implement Exp 3 judge scoring** for English/AISP conditions (~3500 elements)
2. **Re-run Exp 3 analysis** with complete dataset
3. Finish human validation (items 8-30)
4. Build AXON↔A2A field mapping table
5. Reframe paper: reliability/correctness primary, token efficiency secondary

## Blockers
- None
