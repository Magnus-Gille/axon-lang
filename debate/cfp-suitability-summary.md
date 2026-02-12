# Debate Summary: CFP Suitability — Agentic Dev Days 2026 Stockholm

## Participants
- **Claude** (Opus 4.6): Proposer/defender
- **Codex** (GPT-5.3): Adversarial reviewer

## Rounds
- Round 0: Claude draft + self-review
- Round 1: Codex critique → Claude response
- Round 2: Codex rebuttal (final)

## Consensus Reached

**Both sides agree:**

1. **Submit a lightning talk** — the project is mature enough for a 10-minute slot at a dev conference
2. **Don't submit a 30-minute talk without at least one executed benchmark** — and token compression alone is insufficient; need to demonstrate practical value (e.g., semantic correctness, failure handling)
3. **Track B (methodology) is supporting material, not the main angle** at an agentic dev conference
4. **Perception risk is real and strategic** — premature presentation could poison future reception
5. **The MCP/function-calling objection doesn't kill AXON conceptually** but sets a very high burden of proof
6. **Epistemic honesty must be front-loaded** — "protocol hypothesis with a working prototype," not "a better agent standard"

## Concessions Accepted by Both Sides

| Point | Claude conceded | Codex accepted |
|-------|----------------|----------------|
| 30-min structure is brittle | Yes (C1) | Genuine, adequate |
| Track B over-projected for this audience | Yes (C2) | Genuine, adequate |
| Lightning overloaded at 5 min | Yes (C3) | Genuine, adequate |
| Perception risk is strategic | Yes (C4) | Genuine, adequate |

## Defenses Accepted by Codex

| Defense | Codex verdict |
|---------|---------------|
| Lightning talk is suitable without validation (D1) | Valid |
| Feedback upside is materially valuable (D2) | Valid |
| MCP covers different layer than AXON (PC2) | Valid at concept level |

## Unresolved Issues

1. **Venue fit uncertainty** — CFP scope not confirmed (JS-rendered page)
2. **30-minute go/no-go threshold** — Claude says "may be achievable" without hard criteria
3. **Token-count experiment as evidence** — Codex warns this doesn't meet the burden for a 30-min talk; Claude partially agrees but leaves it open

## Final Verdict

**Submit: Yes — lightning talk only**

The lightning talk should:
- Frame AXON as a **protocol hypothesis**, not a solution
- Show the working prototype with 1-2 concrete comparisons
- Be explicit about what's unproven
- End with an open question / call for practitioner feedback
- Target 10 minutes, not 5

The 30-minute talk should be held until at least one benchmark demonstrates value beyond token compression.

## Debate Files

1. `debate/cfp-suitability-claude-draft.md` — Claude's initial position
2. `debate/cfp-suitability-claude-self-review.md` — Claude's self-critique
3. `debate/cfp-suitability-codex-critique.md` — Codex Round 1 critique
4. `debate/cfp-suitability-claude-response-1.md` — Claude's response
5. `debate/cfp-suitability-codex-rebuttal-1.md` — Codex Round 2 rebuttal
6. `debate/cfp-suitability-summary.md` — This file
7. `debate/cfp-suitability-critique-log.json` — Structured critique data

## Costs
| Invocation | Tokens (in/out) | API cost | Wall-clock time | Model version |
|------------|-----------------|----------|-----------------|---------------|
| Codex R1   | ~30k / ~3k      | ~$0.50   | ~90s            | gpt-5.3-codex |
| Codex R2   | ~20k / ~2k      | ~$0.35   | ~60s            | gpt-5.3-codex |
