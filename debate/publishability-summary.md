# Debate Summary: AXON Publishability, Use Cases & Testability

## Participants
- **Claude (Opus 4.6):** Assessment author and defender
- **Codex (GPT-5.3):** Adversarial reviewer

## Rounds
1. Claude draft → Codex critique (6 blind spots, 3 weakest claims, 3 strongest claims)
2. Claude response (5 full concessions, 2 partial concessions, 3 defenses) → Codex rebuttal (7 concessions accepted, 3 dodges flagged, 3 new issues)

## Agreements Reached

### Concessions accepted by both sides
1. **No numeric venue probabilities** — publication likelihood is conditional on completed experiments, not estimable now
2. **Implementation not started** — experiment infra doesn't exist; plan ≠ readiness
3. **Token efficiency data is illustrative only** — 66% from 8 hand-crafted examples cannot support quantitative claims
4. **Validator is syntax-only** — `validate()` checks parsing, not semantic conformance; this gap must close before experiments
5. **FIPA baseline is required** — not optional, but needs symmetric fairness protocol for LLM adaptation
6. **Experiment design must import full rigor** — the skeleton in the publishability draft is insufficient; the experiment-plan debate's protocol is the real standard
7. **Kill criterion is not binary** — JSON parity on 2 metrics doesn't kill AXON if niche benefits exist, but those benefits must be preregistered

### Defenses accepted by Codex
1. **DSL value is empirical, not logical** — "JSON can encode anything" doesn't invalidate the DSL argument; utility must be measured
2. **Transparent parity > identical engineering** — baselines can differ in implementation as long as asymmetries are documented
3. **Adversarial AI review as complement** — defensible framing if impact is quantified

## Unresolved Issues

### Dodges flagged by Codex
1. **"Naturalness" still unoperationalized** — conceded in principle but no concrete metrics proposed (error classes, recovery latency, schema-violation rates)
2. **FIPA fairness protocol undefined** — "learnability problem" acknowledged but no symmetric adaptation procedure specified
3. **Experiment-plan rigor not yet merged** — pointing to a separate document doesn't fix the published assessment's overstatement

### New issues from Round 2
1. **Goalpost risk** — niche benefits (auditability, verifiability, composability) added after retracting binary criterion must be preregistered secondary endpoints
2. **FIPA confound risk** — training/prompt budgets must be fixed and symmetric across all conditions
3. **Scope dilution** — AXON paper vs methodology paper need explicit prioritization; splitting claims weakens both

## Final Verdict (Codex)

**Single most important next step:** Build and freeze a preregistered, executable evaluation harness that enforces semantic conformance (not just parse validity) and defines fairness constraints for all baselines before any headline experiments are run.

Without that, any positive result can be dismissed as construct/implementation bias. With it, even negative results are publishable.

## Claude's position on the verdict

Agreed. The evaluation harness is the critical path item. Specifically:
1. Extend `validate()` to enforce tier compliance and performative transition rules
2. Define fairness constraints for all 5 conditions (including FIPA adaptation budget)
3. Preregister primary and secondary endpoints (including niche benefits as secondary)
4. Build the harness before running any experiments

## Debate files
- `debate/publishability-claude-draft.md` — original assessment
- `debate/publishability-codex-critique.md` — Round 1 critique
- `debate/publishability-claude-response-1.md` — Claude's response
- `debate/publishability-codex-rebuttal-1.md` — Round 2 rebuttal
- `debate/publishability-summary.md` — this file
