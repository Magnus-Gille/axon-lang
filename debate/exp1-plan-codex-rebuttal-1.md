# Exp 1 Plan — Codex Rebuttal (Round 2)

## 1. Genuine Concessions: What Is Actually Adequate

These concessions are real and, if implemented exactly as stated, are methodologically adequate:

- **Add `complexity_level` to the mixed model**: This directly aligns the Exp 1 model with the prereg multi-factor template (`debate/exp1-plan-claude-response-1.md:20`, `experiments/PREREGISTRATION.md:111`).
- **Specify non-naive bootstrap clustering**: Defining a block bootstrap instead of row-level resampling addresses a real dependency error (`debate/exp1-plan-claude-response-1.md:30`, `debate/exp1-plan-claude-response-1.md:33`).
- **Acknowledge denominator redesign risk**: Admitting the Exp 0 vs Exp 1 element mismatch is substantive and correct (`debate/exp1-plan-claude-response-1.md:5`, `debate/exp1-plan-claude-response-1.md:6`; `experiments/exp0_learnability/tasks/tasks.json:37`, `experiments/exp0_learnability/tasks/tasks.json:65`).

## 2. Genuine but Still Incomplete

These are not fake concessions, but they do not fully resolve the original concern yet:

- **3-judge concession is incomplete**: Moving from 2 to 3 judges is correct (`debate/exp1-plan-claude-response-1.md:10`), but the response does not commit to the **human validation subset** required by fairness (`experiments/FAIRNESS.md:49`). That was part of the original protocol, not optional.
- **Blinding concession is partial**: Removing condition labels is good, but “format-neutral preamble” does not solve format recognizability (`debate/exp1-plan-claude-response-1.md:18`; `experiments/FAIRNESS.md:92`). This needs concrete normalization rules and bias checks that are not circular.
- **Post-hoc flexibility concession is partial**: Filing a deviation before scoring is necessary (`debate/exp1-plan-claude-response-1.md:44`; `experiments/PREREGISTRATION.md:159`), but not sufficient for confirmatory claims after outputs already exist (`experiments/PREREGISTRATION.md:4`).
- **Ratio handling concession is partial**: Pre-specifying transform/zero handling is progress (`debate/exp1-plan-claude-response-1.md:25`), but excluding zero-element outputs from the ratio creates estimand drift unless paired with a formal two-part primary analysis.

## 3. Defenses: Valid vs Dodges

### Valid defenses

- **Data reuse is defensible in principle**: Reusing one corpus for multiple endpoints is acceptable if deviations are documented and labeled (`debate/exp1-plan-claude-response-1.md:67`, `experiments/PREREGISTRATION.md:10`, `experiments/PREREGISTRATION.md:159`).
- **Element expansion can be conceptually justified**: Atomic decomposition is a legitimate density objective; the problem was silent post-hoc redefinition, not the concept itself (`debate/exp1-plan-claude-response-1.md:77`).

### Dodges / weak defenses

- **Prompt overhead argument dodges the experimental unit**: Claiming prompt cost is “fixed” and amortized over long conversations (`debate/exp1-plan-claude-response-1.md:73`) is not guaranteed in this benchmark, where each run is prompt+output per task instance. It is a plausible deployment story, not a settled property of this experiment.
- **Power defense relies on post-hoc power logic**: “81 is fine if effect is large” plus “run more if effect is smaller” (`debate/exp1-plan-claude-response-1.md:53`, `debate/exp1-plan-claude-response-1.md:58`) is a data-contingent sample-size rule unless pre-specified as a sequential design.
- **Deviation protocol is treated as a cure-all**: Documenting deviations helps transparency, but it does not restore the original confirmatory status once scoring rules are designed after seeing the corpus.

## 4. New Issues Introduced in the Response

- **Missing explicit commitment to prereg-required dual reporting**: The deviation protocol requires reporting both prereg and exploratory analyses (`experiments/PREREGISTRATION.md:161`). The response commits to deviation logging but does not explicitly commit to running the prereg-faithful analysis.
- **Potential contradiction in estimand handling**: The response supports including invalid outputs broadly, but also excludes zero-element outputs from ratio analysis (`debate/exp1-plan-claude-response-1.md:28`). This needs a locked two-part estimand so failures are not de-emphasized.
- **Bias-check proposal may be circular**: “Control for actual element presence” in blinding analysis (`debate/exp1-plan-claude-response-1.md:18`) is undefined unless “actual presence” comes from an independent ground truth (not the same judges being audited).
- **Human validation subset still absent**: FAIRNESS requires a 30-item human subset (`experiments/FAIRNESS.md:51`), and the response does not incorporate it.

## 5. Final Verdict

**Single most important unresolved issue**:  
The Exp 1 denominator/scoring framework is still not locked in a way that preserves a clear prereg-confirmatory path. Without an explicit prereg-faithful analysis alongside the expanded rubric, the key outcome remains vulnerable to post-hoc researcher degrees of freedom.

**Single most important next step**:  
Before any judge calls, publish and freeze an Exp 1 deviation addendum that explicitly hard-locks:

1. A **prereg-faithful analysis track** (as originally specified).
2. An **expanded atomic-element track** labeled exploratory.
3. Final judge/blinding/human-subset/zero-handling rules.

If this is done first, the remaining disagreements become interpretable methodological tradeoffs rather than fatal validity threats.
