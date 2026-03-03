# AXON Project Status

**Last session:** 2026-03-03
**Branch:** main
**Latest commit:** ccc3561 (pre-session)

## Completed This Session

### Multi-Phase Experiment Plan — All Phases Complete
Executed all 5 phases of the experiment plan in a single session.

### Phase 0: Cheap Wins from Existing Data
- **0A**: Cross-model generalization (Exp 5) — `experiments/exp5_cross_model/analyze.py`
  - AXON: lowest variance (SD=0.484 tok/unit, SD=0.048 composition rate)
- **0B**: Error taxonomy — added to `experiments/exp3_compositionality/analysis/analyze.py`
  - AXON: 94% bimodal (64% perfect, 30% compositional collapse)
- **0C**: Prompt amortization — extended `experiments/exp1_token_efficiency/analysis/analyze.py`
  - AXON breakeven: 7 msgs vs JSON FC, 14 vs FIPA-ACL

### Phase 1: Exp 3 Judge Scoring — COMPLETE
- Implemented 3-judge panel (Claude A, Codex B, random C) with majority vote
- Scored all 567 outputs across 3 files (Haiku, Sonnet, Codex)
- Checkpoint-resume pattern for long-running scoring

### Phase 2: Parse Accuracy Under Noise — COMPLETE
- Built perturbation engine: char deletion, token swap, truncation
- 1,656 perturbed outputs scored
- Results: AXON 16.2%, JSON FC 17.8%, English 100%, FIPA-ACL 90%

### Phase 3: JSON+Contracts — COMPLETE
- 81/81 cells valid (3 models × 9 tasks × 3 runs)
- JSON+Contracts: 51.6% composition rate (vs AXON 67.0%, JSON FC 24.9%)

### Phase 4: Round-Trip Decomposition — COMPLETE
- 177 cross-model decompositions, 99% parseable
- All formats decomposable — no significant differentiation

### Phase 5: Related Work & Paper Framing — COMPLETE
- Updated ecosystem landscape with SEMAP, StructEval, ReliabilityBench, etc.
- Paper outline: `paper/OUTLINE.md`
- Related work draft: `paper/RELATED_WORK.md`

## Critical Finding: AXON Composition Rate Reversal

With full judge scoring, **AXON ranks last on composition rate**:

| Condition | CompRate | FailRate |
|-----------|----------|----------|
| Structured English | **96.2%** | 0.0% |
| Free English | **95.0%** | 0.0% |
| Inst-Matched English | **94.6%** | 0.0% |
| FIPA-ACL | 83.5% | 9.9% |
| JSON FC | 76.2% | 27.2% |
| AISP | 73.7% | 0.0% |
| **AXON** | **67.0%** | 1.2% |

- English conditions jumped +30-45% with judge scoring (implicit composition recovered by LLM judges)
- AXON only gained +1% (machine scoring already captured almost everything)
- At Level 3 (complex tasks), AXON drops to 39.3% vs English 88-93%
- Mixed-effects: AXON **significantly worse** than all 3 English conditions (p<0.001)

### AXON's Remaining Advantages
1. **Machine-parseability**: Composition extractable programmatically (AST walk, no LLM needed)
2. **Nesting depth**: Only format with non-zero nesting (mean 1.87, max 5)
3. **Cross-model consistency**: Lowest variance across models (SD=0.048)
4. **Low failure rate**: 1.2% vs JSON FC 27.2%

### Paper Reframing Required
- Central thesis (intrinsic > extrinsic compositionality) is not supported
- Story must shift to: "machine-readable composition vs interpretable composition"
- Or: "the cost of extracting implicit vs explicit compositional structure"
- Or: methodology paper with AXON as design artifact, not as winner

## Next Steps
1. **Decide on paper framing** — the data doesn't support the original thesis
2. Run `/debate-codex` on the results to stress-test new framing options
3. Update paper outline and related work to match new framing
4. Human validation: Items 8-30 still pending (may be less critical now)

## Blockers
- Strategic decision needed: what story does this paper tell?
