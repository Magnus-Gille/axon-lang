# AXON Project Status

**Last session:** 2026-03-02
**Branch:** main
**Latest commit:** 57c2e5e

## Completed This Session
- Designed and implemented Exp 3 (compositionality) — full infrastructure
  - 9 tasks × 3 complexity levels, 7 conditions, 30 composition-structure elements
  - AST-based composition extractor for AXON, text-based for others, judge prompt for English
  - GLMM analysis pipeline matching pre-registration
- Generated all 567 cells (3 models × 7 conditions × 9 tasks × 3 runs)
- Updated CLAUDE.md with Exp 3 in project structure and current state

## Key Early Signal (validity only — scoring not yet run)
- **AXON: 99% valid** (80/81, 1 Sonnet parse error on `^` in content)
- **JSON FC: 73% valid** — collapsed to 22% on Haiku (composition too complex for flat JSON)
- **FIPA-ACL: 90% valid** — 70% on Haiku
- All English conditions + AISP: 100% valid
- Composition tasks expose structural limits of JSON FC that simple tasks (Exp 0/1) did not

## In Progress
- Human validation: Items 1-7 complete (100% agreement), items 8-30 remaining

## Next Steps (prioritized)
1. **Score Exp 3 outputs** — `python3 experiments/exp3_compositionality/scoring/score.py` on all 3 result files
2. **Run Exp 3 statistical analysis** — `python3 experiments/exp3_compositionality/analysis/analyze.py --all`
3. Finish human validation (items 8-30)
4. Build AXON↔A2A field mapping table
5. Generate AISP Benchmark A cells (81 cells)
6. Reframe paper: reliability/correctness primary, token efficiency secondary

## Blockers
- None
