# Debate Summary: Making the Adversarial AI Debate Methodology Publishable

## Participants
- **Claude (Opus 4.6):** Proposal author and defender
- **Codex (GPT-5.3):** Adversarial reviewer

## Rounds
1. Claude draft → Codex critique (6 questions answered, multiple missing controls identified)
2. Claude response (7 concessions, 3 partial concessions, 3 defenses) → Codex rebuttal (concessions accepted, 4 remaining gaps, 2 new issues, 6-item publishability checklist)

## Agreed publication framing

**Not publishable as a confirmatory methodology paper.** Publishable as a **registered pilot + prospective protocol paper** if the checklist below is executed.

## Concessions accepted by both sides

1. **Frozen artifact snapshots** — all conditions must review the same frozen version; no sequential evolution
2. **Mixed-effects analysis** — critique points cluster within artifacts; artifact is a random effect; effective N is artifact count, not point count
3. **Retrospective data is exploratory only** — existing ~115 points are pilot data, not confirmatory
4. **Preregistered analysis plan** — primary endpoints, stopping rules, analysis hierarchy defined before data collection
5. **Independent adjudication** — project author cannot be sole rater; multi-rater with inter-rater reliability (Cohen's kappa)
6. **Blinded pre/post quality scoring** — replaces "led to change" as impact metric
7. **Recall proxy labeled as lower-bound** — union-of-conditions denominator is acceptable but must be explicitly labeled as proxy coverage, not true recall

## Defenses accepted by Codex

1. **Author-swap not required** — workflow-specific study is valid as long as claims are scoped to "Claude-authored artifacts reviewed by Codex"
2. **Novelty is conditionally valid** — "rigorously evaluated cross-model adversarial protocol" is a real contribution, but only if execution matches the rigor claims

## Remaining gaps (Codex's view)

1. **Adjudication still too thin** — "1-2 raters on 30 points" may not be enough for stable reliability across conditions/severities; needs broader sample or explicit power justification
2. **Human baseline unresolved** — either include a bounded human calibration arm or fully drop all human-comparison claims (including from title/abstract)
3. **Subset-only ablations** — same-model adversarial condition and rerun variance on subsets are fine for pilot decisions but not confirmatory claims unless sampling/decision rules are precommitted
4. **Blinding protocol missing** — raters must be blinded to condition/model identity for unbiased labels

## New issues from Round 2

1. **Scope creep risk** — adding conditions (1b), reruns, human calibration, and blinded scoring increases complexity; without predeclared minimum artifact count per arm and primary endpoint hierarchy, this risks being underpowered and many-endpoint
2. **Adjudication workflow unspecified** — no explicit blinding protocol for raters

## Codex's 6-item publishability checklist

If these are executed faithfully, the contribution is defensible:

1. Lock a preregistered protocol with primary endpoint(s), stopping rule, and analysis hierarchy
2. Freeze artifacts and randomize/counterbalance review order across conditions
3. Use blinded multi-rater adjudication on a sufficiently broad sample; report inter-rater reliability and disagreement resolution
4. Explicitly narrow claims to the studied workflow/domain unless external validation is added
5. Either include a bounded human calibration arm or remove all human-comparison claims end-to-end
6. Label union-recall as proxy coverage and separate exploratory from confirmatory analyses

## Claude's position on the checklist

Agreed on all 6 items. Specific implementation notes:
- Items 1-3 are non-negotiable prerequisites
- Item 4 is already the plan (scope to AXON project, Claude→Codex workflow)
- Item 5: I lean toward dropping human-comparison claims and framing cost-effectiveness as "cost per valid issue found" without a human comparator, unless we can recruit a domain expert for calibration
- Item 6: natural paper structure — Methods clearly separates pilot/exploratory (retrospective) from prospective (confirmatory)

## Practical changes to start now

1. **Update the debate skill** to capture structured per-point metadata (ID, classification, impact, severity)
2. **Add self-review step** before Codex invocation (for ablation data)
3. **Log costs** per invocation (tokens, dollars, time)
4. **Snapshot artifacts** before any review condition
5. **Define primary endpoint** before next debate: precision of adversarial cross-model vs self-review

## Debate files
- `debate/methodology-claude-draft.md` — original proposal
- `debate/methodology-codex-critique.md` — Round 1 critique
- `debate/methodology-claude-response-1.md` — Claude's response
- `debate/methodology-codex-rebuttal-1.md` — Round 2 rebuttal
- `debate/methodology-summary.md` — this file
