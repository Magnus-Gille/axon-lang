# Exp 1: Token Efficiency — Implementation Plan

> Post-debate revision. Incorporates all changes from the Claude↔Codex adversarial review.
> See `debate/exp1-plan-summary.md` for the full debate record.

## Research Question

How many tokens does each format need to convey the same semantic content? Is AXON measurably more token-efficient than controlled alternatives?

## Primary Metric

**tokens_per_semantic_unit** = `token_count / semantic_elements_correctly_expressed`

Measured across both `cl100k_base` (primary) and `o200k_base` (secondary) encodings.

## Data Source

Reuses the 486 outputs from Exp 0 (3 models x 6 conditions x 9 tasks x 3 runs). Deviations from the original pre-registration are documented in `DEVIATION.md`, which is frozen before any scoring begins.

## Dual-Track Analysis

**Track A (Confirmatory)**: Uses original `expected_elements` from Exp 0 tasks.json. Preserves the pre-registered denominator. Supports confirmatory inference.

**Track B (Exploratory)**: Uses expanded atomic element decomposition. Each countable fact is one element. Labeled exploratory throughout.

Both tracks use identical scoring protocol, statistical methods, and reporting.

## Scoring Protocol

- **3-judge panel**: Claude Sonnet + GPT-5.3 Codex + random tiebreaker (per FAIRNESS.md)
- **Majority vote**: 2/3 agreement. 3-way disagreements flagged for human review.
- **Blinding**: No condition labels. Format-neutral preamble.
- **Human validation subset**: 30 items (5 per condition), scored by human before LLM judges.
- **Calibration**: 36-item subset with ground truth. Target >90% per-element agreement.
- **Element verdicts**: PRESENT (1), ABSENT (0), INCORRECT (0).

## Statistical Analysis

### Primary Model
```
log(tokens_per_unit) ~ condition + complexity_level + (1|task) + (1|model)
```

### Secondary Model (prereg-faithful)
```
tokens ~ condition + complexity_level + (1|task) + (1|model)
```

### Two-Part Model
- Part 1: P(complete failure) ~ condition (logistic)
- Part 2: tokens/unit conditional on elements > 0

### Pairwise Comparisons
5 comparisons (AXON vs each), Holm-Bonferroni corrected (α = 0.05).

### Effect Sizes
Cohen's d with 95% BCa bootstrap CI (10,000 resamples, block bootstrap at task × model level).

### Prompt Overhead (Secondary)
Prompt token counts per condition + breakeven analysis.

## Directory Structure

```
experiments/exp1_token_efficiency/
├── PLAN.md                            # This file
├── DEVIATION.md                       # Frozen deviation addendum
├── tasks/
│   └── element_annotations.json       # Dual-track element definitions
├── scoring/
│   ├── score.py                       # 3-judge element scorer
│   └── judge_prompt.txt               # Blinded judge prompt template
├── analysis/
│   └── analyze.py                     # Full statistical pipeline
├── results/                           # Scored outputs + analysis artifacts
└── run.py                             # Orchestrator
```

## Run Protocol

```bash
# Dry run
python3 experiments/exp1_token_efficiency/run.py --dry-run

# Score Track A (confirmatory)
python3 experiments/exp1_token_efficiency/run.py --score --track a

# Score Track B (exploratory)
python3 experiments/exp1_token_efficiency/run.py --score --track b

# Analyze all scored results
python3 experiments/exp1_token_efficiency/run.py --analyze

# Full pipeline
python3 experiments/exp1_token_efficiency/run.py --all --track a
```

## Debate Record

18 critique points from Codex, 7 from self-review. Key changes:
- Added dual-track analysis (Codex's top verdict)
- Upgraded to 3-judge panel with human validation subset
- Added condition blinding
- Added complexity_level fixed effect
- Pre-specified log-transform and two-part model
- Specified block bootstrap resampling

See `debate/exp1-plan-summary.md` and `debate/exp1-plan-critique-log.json`.
