# Experiment 3: Compositionality

## Status
Phase 1 implementation complete. Ready for data generation.

## Overview

Exp 3 tests AXON's core differentiator: **composition operators** (`->`, `&`, `|`, `<-`, nesting).
Exp 1 showed AXON wins on reliability and beats structured formats on efficiency but ties
English. Exp 3 targets complex multi-step messages where formal structure should provide
clear advantages.

**Co-primary with Exp 1.** Together they form the strongest evidence for AXON's value proposition.

**Grammar version**: v0.1b (with arithmetic operators). Documented as version difference from
Exp 1 (v0.1a). See `experiments/exp1_token_efficiency/RESULTS.md` for provenance details.

## Pre-Registered Endpoints

From `experiments/PREREGISTRATION.md`:

- **Primary**: Composition success rate — proportion of correctly composed multi-step messages
  (sequences, parallel, causal chains) as judged by the 3-way LLM panel.
- **Secondary**: Decomposability — can a receiver correctly extract individual steps?
- **Secondary**: Nesting depth achievable before first error.

## Design

### Phase 1: Single-Turn Composition Generation (Confirmatory)

**Matrix**: 9 tasks x 7 conditions x 3 models x 3 runs = **567 cells**

Tasks span 3 complexity levels, each testing different composition operators:

| Level | Tasks | Operators Tested | Elements per Task |
|-------|-------|------------------|-------------------|
| L1 (simple) | L1-01 sequential, L1-02 parallel, L1-03 alternative | One operator each (`->`, `&`, `\|`) | 6 |
| L2 (medium) | L2-01 seq+parallel, L2-02 alt+sequence, L2-03 parallel+negation | Two operators, 1 nesting level | 7-8 |
| L3 (complex) | L3-01 full pipeline, L3-02 causal chain, L3-03 multi-path negotiation | 3+ operators, 2+ nesting levels | 10-12 |

### Scoring

Element categories:
- **identity** — sender/receiver (machine-scored for all structured formats)
- **intent** — performative/action type (machine for structured, judge for English)
- **composition-step** — individual actions/operations (machine + text search for structured, judge for English)
- **composition-structure** — **NEW**: structural relationships (sequence order, parallel grouping, alternatives). Machine-scored for AXON via AST walking; judge-scored for all other conditions.

Primary DV: `composition_structure_correct / composition_structure_total` per output.

### Phase 2: Decomposition Testing (Exploratory)

**Protocol**:
1. Select 90 Phase 1 outputs (1 per condition x task x model, run #1)
2. Cross-model pairing: Codex->Sonnet, Haiku->Codex, Sonnet->Haiku
3. Prompt receiving model to extract individual steps and their relationships
4. Score decomposition accuracy with 3-judge panel

## Statistical Analysis

### Primary Model (Confirmatory)

```
composition_success ~ condition + complexity_level + (1|task) + (1|model)
```

Binomial GLMM (proportion DV). Pairwise: AXON vs each of 5 prereg conditions, Holm-Bonferroni corrected.

### Interaction Model (Key Hypothesis)

AXON's advantage should grow with complexity:
```
composition_success ~ condition * complexity_level + (1|task) + (1|model)
```

### Secondary Models

- Overall element rate (all categories)
- Nesting depth: Poisson GLMM for L2+L3 only
- AISP: reported separately (exploratory, uncorrected)

### Convergence Fallback

If model variance ~0 (expected with 3 models), drop `(1|model)`, add `model` as fixed effect.
Same approach as Exp 1 (documented in `experiments/exp1_token_efficiency/RESULTS.md`).

## Key Risks

1. **Ceiling on L1**: Simple composition may be trivial for all conditions. Pre-specified:
   focus analysis on L2+L3 if L1 >90% across all conditions.
2. **English ties AXON again**: Possible, but Phase 2 decomposition should differentiate
   (formal structure aids receiver parsing).
3. **Convergence issues**: Same 3-model problem as Exp 1. Fixed-effect fallback pre-specified.
4. **AXON operator confusion**: v0.1b has both `+` (arithmetic) and `&` (parallel).
   Monitor for misuse, report as error class.

## Files

```
experiments/exp3_compositionality/
├── DESIGN.md                          # This file
├── run.py                             # Orchestrator
├── tasks/
│   ├── tasks.json                     # 9 tasks across 3 complexity levels
│   └── element_annotations.json       # Element definitions with composition-structure
├── scoring/
│   ├── composition_extractor.py       # AXON AST-based composition scorer
│   ├── composition_judge_prompt.txt   # Extended judge prompt for composition
│   ├── scoring_contract.json          # Per-condition scoring contract
│   └── score.py                       # Hybrid scorer
├── analysis/
│   └── analyze.py                     # Statistical analysis pipeline
├── results/                           # Output directory
└── RESULTS.md                         # After analysis
```
