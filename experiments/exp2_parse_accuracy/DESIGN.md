# Experiment 2: Parse Accuracy Under Noise

## Motivation

Tests robustness of agent communication formats to message corruption.
Supports the reliability/correctness pivot by measuring how well each format
preserves structure and meaning when subjected to realistic noise.

Addresses the ReliabilityBench gap: our reliability claims are currently passive
(zero failures in clean data). Exp 2 provides active stress-testing evidence.

## Design

### Matrix

- **Source outputs**: Exp 1 valid outputs (already generated and scored)
- **Perturbation types**: 3 (character deletion, token swap, truncation)
- **Conditions**: 7 (free_english, structured_english, instruction_matched_english, json_fc, fipa_acl, axon, aisp)
- **Models**: 3 (codex, claude-haiku, claude-sonnet)
- **Tasks**: 9 (L1-01 through L3-03)
- **Runs**: 3 per original output
- **Cells per perturbation type**: 7 × 3 × 9 × 3 = 567
- **Total cells**: 567 × 3 perturbation types = 1,701

### Perturbation Types

1. **Character Deletion** (`rate=0.05`): Randomly remove 5% of characters.
   Models transmission errors, encoding issues, truncated network packets.

2. **Token Swap**: Swap two adjacent tokens (GPT tokenization via tiktoken).
   Models reordering artifacts from async processing or buffer corruption.

3. **Truncation** (`ratio=0.75`): Keep first 75% of characters.
   Models incomplete message delivery, timeout-based cutoffs.

All perturbations are deterministic given a seed. Seed = hash(task_id, condition, model, run_number, perturbation_type).

### Primary DV

**Structural Preservation Rate** = valid_parses / total_perturbations per condition.

A perturbed output "preserves structure" if it passes the condition's validation
(via `lib/condition_adapter.validate_output()`).

### Secondary DV (optional)

**Semantic Equivalence**: For a subset (10 per condition), prompt an LLM with
(original, perturbed) pair, ask if the core information is preserved.
Uses 3-judge panel for consistency with Exp 1/3.

### Statistical Analysis

- Primary: GLMM `preservation ~ condition + perturbation_type + complexity_level + (1|task) + (1|model)`
- Pairwise: AXON vs each condition, Holm-Bonferroni corrected
- Bootstrap CIs on preservation rate differences
- Interaction: `condition × perturbation_type` — tests whether AXON's strict syntax is more/less vulnerable to specific corruption types

### Hypotheses

- **H1**: AXON structural preservation rate differs from English conditions (non-directional — strict syntax may be MORE vulnerable to character deletion)
- **H2**: AXON × truncation interaction: AXON's single-line format loses proportionally less information than multi-line formats
- **H3**: JSON FC is most vulnerable to character deletion (unmatched braces break parsing)

### Key Insight

AXON's strict syntax is a double-edged sword:
- **Pro**: Clear failure signal — you KNOW when a message is corrupted
- **Con**: Lower tolerance — single-character deletion can break parsing
- English formats degrade gracefully but may silently lose semantic content

This tests whether intrinsic structure provides a "checksum" effect.
