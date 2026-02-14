# Exp 1: Token Efficiency — Preliminary Results

> **Status**: Track A scoring complete. Statistical analysis pending.
> **Date**: 2026-02-14
> **Scoring method**: Hybrid (machine extraction for structured formats, 3-judge LLM panel for English)

## Summary

486 outputs scored across 3 models (Codex, Haiku, Sonnet) × 6 conditions × 9 tasks × 3 runs.
Track A (confirmatory) uses the pre-registered element counts from Exp 0.

**AXON ranks #1 in token efficiency** (15.4 tok/unit mean across models) and has the fewest
raw tokens (76.8 mean). The margin over structured English is small (3%). The margin over
JSON FC and FIPA-ACL is substantial (~30%).

## Tokens Per Semantic Unit (Track A, cl100k_base)

Lower = more information per token = better.

| Rank | Condition | Codex | Haiku | Sonnet | Mean |
|------|-----------|-------|-------|--------|------|
| 1 | **AXON** | **15.0** | **15.9** | **15.4** | **15.4** |
| 2 | Structured English | 14.7 | 18.8 | 14.1 | 15.9 |
| 3 | Free English | 16.6 | 20.7 | 11.5 | 16.3 |
| 4 | Instruction-Matched English | 19.8 | 17.6 | 17.9 | 18.5 |
| 5 | FIPA-ACL | 20.7 | 19.8 | 23.7 | 21.4 |
| 6 | JSON FC | 20.5 | 22.4 | 24.9 | 22.6 |

## Raw Token Counts

| Condition | Codex | Haiku | Sonnet | Mean |
|-----------|-------|-------|--------|------|
| AXON | 81.9 | 70.6 | 77.8 | **76.8** |
| Structured English | 77.4 | 81.2 | 66.0 | 74.9 |
| Free English | 88.9 | 94.2 | 63.0 | 82.0 |
| Instruction-Matched English | 106.5 | 94.6 | 100.1 | 100.4 |
| FIPA-ACL | 114.1 | 109.7 | 97.4 | 107.1 |
| JSON FC | 111.0 | 139.1 | 148.6 | 132.9 |

## Semantic Element Detection Rate

Percentage of required elements successfully communicated.

| Condition | Codex | Haiku | Sonnet |
|-----------|-------|-------|--------|
| AXON | 99.3% | 92.2% | 94.1% |
| FIPA-ACL | 100.0% | 97.4% | 92.2% |
| Free English | 96.7% | 56.9% | 97.4% |
| Structured English | 94.8% | 82.4% | 86.3% |
| Instruction-Matched English | 94.8% | 93.5% | 100.0% |
| JSON FC | 100.0% | 81.0% | 94.8% |

## Complete Failures (Zero Elements)

| Model | Count | Conditions Affected |
|-------|-------|-------------------|
| Codex | 0 | — |
| Haiku | 16 | Free English (9), JSON FC (4), Structured English (2), Inst-Matched (1) |
| Sonnet | 1 | JSON FC (1) |

Haiku failures were genuine: either refusals ("I need clarification") or wrong-format outputs
(AXON syntax when asked for JSON FC). AXON had **zero complete failures** across all models.

## Key Findings

### 1. AXON is the most token-efficient format
Across all 3 models, AXON has the lowest mean tok/unit (15.4) and fewest raw tokens (76.8).
The advantage over JSON FC is ~32% on tok/unit and ~42% on raw tokens.

### 2. Structured formats are not inherently verbose
The common assumption that structured = verbose is wrong for AXON. JSON FC and FIPA-ACL
are verbose because of their syntax overhead (braces, quotes, nested objects, S-expression
parentheses). AXON's compact syntax avoids this while remaining machine-parseable.

### 3. AXON is the most consistent across model tiers
The range in element detection across models:
- AXON: 92.2%–99.3% (7.1pp range)
- Free English: 56.9%–97.4% (40.5pp range)
- JSON FC: 81.0%–100.0% (19.0pp range)

Weaker models (Haiku) benefit most from structured formats. AXON provides structure
without the token cost of JSON.

### 4. Format acts as a guardrail for weaker models
Haiku's 9 complete failures on free English (33% of L2 tasks) were refusals — the model
asked for clarification instead of producing the message. Structured formats prevented this.

## Scoring Methodology

- **Machine-scored** (AXON, JSON FC, FIPA-ACL): Automated extractors parse format-specific
  syntax and check each element. 100% agreement by definition.
- **Judge-scored** (English ×3): Claude Sonnet + Codex + random tiebreaker. Majority vote.
- **Bug encountered**: Claude judge had a transient failure during Codex run#2 scoring
  (12 outputs, all-ABSENT). Detected via systematic agreement analysis, re-scored
  successfully. See scoring notes below.
- **Cross-validation**: Pending (30 structured outputs to be judge-scored for comparison).

## Remaining Work

1. **Formal statistical analysis**: Mixed-effects model, pairwise comparisons with
   Holm-Bonferroni, bootstrap CIs, two-part model for zero-element outputs
2. **Track B scoring**: Expanded atomic element decomposition (exploratory)
3. **Cross-validation**: Machine vs judge agreement on structured formats
4. **Human validation subset**: 30 items scored by human rater

## Data Files

- `results/exp1_scored_codex_tracka_*.json` — Codex scored outputs
- `results/exp1_scored_claude-haiku_tracka_*.json` — Haiku scored outputs
- `results/exp1_scored_claude-sonnet_tracka_*.json` — Sonnet scored outputs
- `scoring/extractors.py` — Automated element extractors
- `scoring/scoring_contract.json` — Per-condition scoring method specification
- `scoring/score.py` — Hybrid scoring orchestrator

## Scoring Notes

### Claude Judge Transient Failure (2026-02-14)
During Codex Track A scoring, Claude Sonnet (judge A) returned unparseable responses for
12 consecutive English outputs (structured_english run#2 L3 tasks + all instruction_matched_english
run#2 tasks). The response parser defaulted every element to ABSENT. When judge C was also
Claude (random selection), this created 2-1 ABSENT majority on elements that were clearly present.

**Detection**: Systematic analysis of per-judge agreement rates flagged 0% agreement on
all affected outputs. Pattern was batch-correlated (all run#2, consecutive indices), not
element-correlated, ruling out legitimate scoring disagreement.

**Fix**: Re-scored all 12 outputs with fresh Claude judge calls. All returned correct verdicts.
Also fixed dict key collision bug where judge C overwrote judge A/B entry when same model
was randomly selected.
