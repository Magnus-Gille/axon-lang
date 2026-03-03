# Deviation Notice: JSON + Behavioral Contracts Condition

## Summary

This document records a post-pre-registration addition to the experimental
design: a "JSON + Contracts" condition that augments standard JSON function
calling with SEMAP-inspired behavioral contracts.

## Motivation

A March 2026 landscape scan identified **SEMAP** (Oct 2025), which demonstrates
that structured contracts over JSON reduce agent failures by 70%. This
challenges whether a new format like AXON is needed — the alternative hypothesis
is that contracts (extrinsic composition) on existing formats close the gap.

This mini-experiment directly tests whether adding contract structure to JSON
achieves compositionality comparable to AXON's intrinsic operators.

## Design

- **Scope**: Exp 3 compositionality tasks only (9 tasks × 3 models × 3 runs = 81 cells)
- **Condition**: `json_contracts` — JSON FC + behavioral contracts (preconditions,
  postconditions, lifecycle stage, typed message schemas)
- **Analysis**: Exploratory, uncorrected. Reported separately from pre-registered
  6-condition analysis. Compared pairwise against AXON and JSON FC.

## Relation to Pre-Registration

This condition was NOT part of the original pre-registration (see
`experiments/PREREGISTRATION.md`). It is treated identically to the AISP
condition: exploratory, reported with deviation notice, never included in
Holm-Bonferroni corrections.

## Date

2026-03-02
