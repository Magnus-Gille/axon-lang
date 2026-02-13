# Round 2 Rebuttal on MassGen Integration

## Executive Judgment
Claude's revised position is substantially better than the original, but still under-specified where it matters operationally. The core correction (Exp 5 target drift) is real and material. The remaining weaknesses are mostly about replacing concrete planning with conditional language.

## 1) Concessions: Genuine vs Adequate

### C1 (Exp 5 target drift): genuine and adequate
This concession is both candid and consequential. Claude explicitly retracts the non-preregistered "Exp 5 = 128-agent scaling" premise (`debate/massgen-integration-claude-response-1.md:7`, `debate/massgen-integration-claude-response-1.md:59`) and aligns with the frozen prereg endpoint (`experiments/PREREGISTRATION.md:85`). That directly fixes the biggest methodological error identified in Round 1 (`debate/massgen-integration-codex-critique.md:69`).

### C2 (~100 LOC claim): genuine, partially adequate
The admission that the estimate was unsupported is genuine (`debate/massgen-integration-claude-response-1.md:12`). It is only partially adequate because the response does not replace the bad estimate with even a coarse decomposition (MVP harness vs reliable harness). The rhetorical overconfidence is removed; the planning gap remains.

### C3 (status-quo bias): genuine, not yet adequate
Claude concedes plan-protection bias (`debate/massgen-integration-claude-response-1.md:15`). But adequacy requires a process correction (for example: explicit decision criteria for when exploratory integration is triggered). That mechanism is still absent.

## 2) Defense Audit: Valid Arguments vs Dodges

### Valid defenses
- **D2 is fully valid**: MassGen as a seventh condition is still a category error against the six format-defined conditions (`experiments/PREREGISTRATION.md:12`, `debate/massgen-integration-claude-response-1.md:46`).
- **PC2 pushback is mostly valid**: "lab first, ecosystem second" is methodologically coherent and compatible with prereg discipline plus deviation handling (`experiments/PREREGISTRATION.md:158`, `debate/massgen-integration-claude-response-1.md:32`).
- **PC3 scoping demand is valid**: requesting concrete scope, frozen version/config, and explicit endpoints is exactly what an exploratory phase needs (`debate/massgen-integration-claude-response-1.md:39`).

### Where defenses dodge or overstate
- **PC1 noise objection is directionally right but currently speculative**: yes, orchestration can add variance (`debate/massgen-integration-claude-response-1.md:25`), but prereg already contemplates power maintenance by increasing runs (`experiments/PREREGISTRATION.md:122`). Without a variance budget or sensitivity analysis, this is caution, not a blocker.
- **D1 "later" stance partially dodges execution risk**: preserving Track B comparability is fair (`debate/massgen-integration-claude-response-1.md:44`), but the response does not define what "later" means in concrete project terms (milestone, trigger, or artifact freeze point). That leaves room for indefinite deferral.
- **Revised position still leans on promissory framing**: "accept in principle, needs scoping" (`debate/massgen-integration-claude-response-1.md:57`) is improvement over blanket rejection, but not yet an actionable plan.

## 3) New Issues Introduced in Round 2

1. **Implementation ambiguity**: The revised stance endorses an exploratory phase without defining minimal scope (which experiments, how many runs, what success/failure criteria).
2. **No explicit prereg-deviation workflow binding**: Claude references sequencing but does not commit to a concrete addendum process before exploratory analysis, despite the protocol requiring documented deviations (`experiments/PREREGISTRATION.md:158`).
3. **Decision-point ambiguity**: "after primary analyses complete" is underspecified. Does this mean after Exp 0 gate, after Exp 0-5, or after publication-ready prereg reporting? This matters for resourcing and bias control.
4. **Unresolved burden-shift**: Claude requests scoping detail but does not provide a minimal candidate scope. That is a procedural dodge: the critique's proposal is treated as insufficient without proposing a competing concrete draft.

## 4) Final Verdict

### (a) Single most actionable recommendation
Create a **frozen one-page Exploratory MassGen Addendum** now, before any exploratory runs, containing exactly:
- one fixed MassGen version/config;
- selected experiments to replicate (at minimum Exp 3 and Exp 4, where multi-agent realism is most relevant);
- unchanged six conditions (`experiments/PREREGISTRATION.md:12`);
- predefined analysis split: prereg results reported first, exploratory results clearly labeled per deviation protocol (`experiments/PREREGISTRATION.md:158`);
- a simple power/variance contingency rule (increase runs if orchestration variance inflates uncertainty).

This is the shortest path from "promissory note" to executable design.

### (b) Is Claude's revised position sound?
**Conditionally sound.**
It is now methodologically coherent on the major points (no 7th condition, corrected Exp 5 framing, preserve prereg integrity). It is not fully sound operationally until the exploratory phase is concretely scoped and bound to explicit deviation/reporting rules.
