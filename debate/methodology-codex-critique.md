# Critique of `debate/methodology-claude-draft.md`

## High-level assessment
The proposal is promising as an **internal evaluation plan**, but not yet rigorous enough to support strong publishability claims about the methodology itself. The current draft has the right instincts, but key controls and adjudication design are missing.

## What is strong
- The core claim is falsifiable and decomposed into three testable sub-claims (`debate/methodology-claude-draft.md:7`, `debate/methodology-claude-draft.md:9`).
- You already include a meaningful ablation structure instead of one-condition anecdotes (`debate/methodology-claude-draft.md:26`).
- You explicitly track cost, which most methodology papers ignore (`debate/methodology-claude-draft.md:38`).
- You acknowledge important limitations (single project, shared blind spots) rather than hiding them (`debate/methodology-claude-draft.md:89`).

## 1. Study design rigor: enough for the claims?
Short answer: not yet.

Missing controls that block causal interpretation:
- No randomization/counterbalancing of review order across conditions. If conditions are run in a fixed sequence, later reviewers benefit from earlier edits/exposure.
- No frozen artifact snapshots per condition. Without this, "condition effect" is confounded with artifact evolution.
- No model stochasticity control (temperature/seed/retry policy/version pinning). You log model version (`debate/methodology-claude-draft.md:40`) but do not define reproducibility constraints.
- No independent adjudication design. "Project author rates ~30 points" (`debate/methodology-claude-draft.md:44`) cannot serve as robust ground truth for validity/novelty/severity.
- No human-review baseline despite claiming cost-effectiveness "compared to human review" (`debate/methodology-claude-draft.md:12`). Right now there is no explicit human comparator arm.
- No preregistered analysis/stopping plan. Prior debate already flagged rigor and goalpost risks (`debate/publishability-summary.md:19`, `debate/publishability-summary.md:35`).

## 2. Sample size: is 115 existing + ~100 new critique points enough?
For exploratory analysis: maybe. For strong statistical claims: likely no.

Key issue: your unit of analysis is wrong if you count critique points as independent. Points are clustered within artifacts/debates/reviewers, so effective N is much smaller than 200-250.

Concrete problems:
- "~600-750 data points across conditions" (`debate/methodology-claude-draft.md:51`) overstates power unless each point is independent (it is not).
- The retrospective 115 points (`debate/methodology-claude-draft.md:51`, `debate/methodology-claude-draft.md:71`) are post-hoc coded and likely affected by hindsight/selection bias.
- Human validation on ~30 points (`debate/methodology-claude-draft.md:44`) is underpowered for stable precision/severity estimates and cannot support tight confidence intervals.

What would make this defensible: treat this as a pilot, analyze with mixed-effects models (artifact as random effect), and scale artifact count (not just point count).

## 3. Ablations: are these the right ones? What confounds remain?
Current 3-condition ablation is a good start but does not isolate all effects.

Current confounds:
- Model identity is confounded with authorship role: Claude authors + self-reviews, Codex cross-reviews (`debate/methodology-claude-draft.md:29`, `debate/methodology-claude-draft.md:30`).
- Prompt style and adversariality are partially isolated for Codex (2 vs 3), but not for Claude. You cannot tell whether adversarial framing is generally helpful or Codex-specific.
- No reviewer-order control.
- No token/context budget parity control.

Missing ablations I would add:
- Same-model adversarial self-review for Claude (neutral vs adversarial) to isolate prompt effect independent of model family.
- Author-swap or cross-over artifacts (some artifacts authored by Codex, reviewed by Claude) to reduce role asymmetry.
- Human reviewer arm (even small) if making "vs human" cost/value claims.

## 4. Metrics: complete enough?
Not yet. Current metrics are useful but incomplete (`debate/methodology-claude-draft.md:55`).

What is missing:
- Recall proxy / issue coverage. Precision alone rewards low-volume critics.
- Downstream artifact quality delta (blinded pre/post scoring), not just "led to change" (`debate/methodology-claude-draft.md:22`), since many changes are low value.
- Inter-rater reliability (e.g., Cohen/Fleiss agreement) for validity/severity labels.
- Reviewer burden metrics: time spent triaging false positives, not just API dollars (`debate/methodology-claude-draft.md:58`).
- Robustness/reproducibility: rerun variance across repeated runs on same artifact.

## 5. Biggest threats to validity
- **Adjudication bias**: project author as ground-truth rater (`debate/methodology-claude-draft.md:44`) creates confirmation and self-justification bias.
- **Construct validity**: "novelty" measured by self-report ("would you have caught this") is weak and vulnerable to hindsight bias (`debate/methodology-claude-draft.md:46`).
- **Selection/reporting bias**: retroactive classification of existing points (`debate/methodology-claude-draft.md:71`) invites outcome-aware labeling.
- **Internal validity confounds**: model/version drift and uncontrolled prompt/context differences.
- **External validity**: single project/domain limits generalization (`debate/methodology-claude-draft.md:91`).
- **Protocol maturity risk**: prior summary already notes experiment rigor/harness concerns not fully merged (`debate/publishability-summary.md:32`, `debate/publishability-summary.md:41`).

## 6. Novelty: real contribution or just "two chatbots talk"?
As currently framed, novelty is **not yet established**.

What is potentially novel:
- A disciplined, preregistered, cost-aware **cross-model adversarial review protocol** with ablations and adjudication.

What currently makes it look incremental:
- Multi-agent critique/debate workflows are already common; without stronger controls and external adjudication, this reads as operational practice, not methodological research.
- The draft does not benchmark against standard alternatives (single-model strong prompt review, human review, or mixed human+AI review) strongly enough to justify "independent contribution" status.

## Bottom line
You have a credible pilot design, not yet a publishable methodology paper design. If you tighten controls, add independent adjudication, preregister analysis, and frame current data as exploratory, this can become publishable. Without those changes, the strongest criticism remains: this is an anecdotal process report, not a validated methodology.
