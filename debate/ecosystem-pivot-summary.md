# Ecosystem Pivot Debate — Summary

**Date**: 2026-02-27
**Participants**: Claude (Opus 4.6), Codex (gpt-5.3-codex)
**Rounds**: 2
**Topic**: AXON's position in the 2026 agent communication ecosystem and whether to pivot

---

## Context

A comprehensive ecosystem landscape analysis mapped 15+ protocols, standards, and formats across 5 layers: transport (A2A, MCP), discovery (Agent Cards), content format (JSON, TOON), frameworks (AutoGen, CrewAI), and academic research. The debate addressed 5 key questions about AXON's positioning and pivot strategy.

## Consensus Reached

### 1. AXON is NOT competing with A2A/MCP (with caveats)
AXON operates at the content/payload layer, not the transport/protocol layer. However, Tier 2-3 metadata overlaps A2A/NLIP envelope semantics, and even Tier 1 routing (`@sender>@receiver`) may collide with protocol-level addressing. A field mapping table is needed to prove clean coexistence.

### 2. Objective hierarchy resolved
**Primary goal: publishable research contribution.** Adoption is a stretch goal, not a requirement for success. This resolves the "reframing vs decision-making" confusion that plagued earlier analysis.

### 3. Option C+B hybrid is the recommended path
- **C (methodology contribution)** as the paper's primary claim — the 7-condition benchmark is novel and fills a real gap identified by ProtocolBench, "Beyond Self-Talk" survey, and LACP
- **B (A2A integration proof)** as a small but executable artifact — NOT a Future Work paragraph, but a minimal runnable adapter showing AXON inside an A2A message path

### 4. Reframed positioning language
- ~~"Content format layer is wide open"~~ → **"Research-open, adoption-constrained"**
- The research question is genuinely unaddressed; the adoption surface is constrained by JSON inertia and training distribution

### 5. Token efficiency alone is insufficient
The cost thesis weakens as inference prices drop. The paper must re-center on **reliability and coordination correctness**, with token efficiency as secondary. But the reliability leg currently lacks strong empirical support — Exp 3 (compositionality/repair dynamics) is needed.

## Concessions Accepted

| # | Concession | Severity |
|---|-----------|----------|
| C01 | Tier 2-3 metadata overlaps A2A/NLIP envelope | Major |
| C02 | "Wide open" claim self-contradicts | Major |
| C04 | Option C alone risks academic cul-de-sac | Critical |
| C05 | Non-cost thesis legs under-supported | Major |
| C06 | AISP omission is credibility gap | Major |
| C08 | Objective confusion was the deepest issue | Critical |

## Defenses Accepted by Codex

| # | Defense | Status |
|---|---------|--------|
| D1 | TOON is "intentional competitor" — useful distinction from JSON/NL defaults | Valid |
| D2 | Keeping AXON in C (vs pure E) increases contribution novelty | Valid |
| D3 | NLIP is mostly envelope/protocol layer — coexistence is plausible | Valid at high level |

## Unresolved Disagreements

1. **Scope of B proof**: Claude wants "paragraph in Future Work"; Codex wants "runnable adapter + experiment." Codex's position is stronger — a prose-only B does not de-risk the irrelevance criticism.
2. **Tier 1 routing overlap**: Even `@sender>@receiver` at Tier 1 may duplicate A2A addressing. Needs concrete field mapping to resolve.
3. **Option E assessment**: Codex says ranking E last is too absolute; Claude defends design contribution value. Remaining disagreement is preference, not substance.

## New Issues from Round 2

1. **Evidence category slippage**: Parseability ≠ reliability. Format conformance is prerequisite evidence, not outcome evidence for coordination correctness.
2. **Action items need decision gates**: No acceptance criteria or deadlines were defined for the 6 action items.

## Action Items

| # | Action | Owner | Decision Gate |
|---|--------|-------|---------------|
| 1 | **Build AXON↔A2A field mapping table** (drop/map/retain for every AXON field) | Claude | Table exists and accounts for Tier 1 routing |
| 2 | **Map AISP into ecosystem competitor matrix** | Claude | AISP appears alongside TOON/JSON/NL in analysis |
| 3 | **Add NLIP coexistence section** to landscape analysis | Claude | Explicit MIME/binding/validation story |
| 4 | **Design + run Exp 3** (compositionality/repair dynamics) | Magnus decision | Protocol + at least 1 pilot result |
| 5 | **Build minimal A2A adapter** (B proof) | Post-paper-draft | Two agents exchanging AXON via A2A-shaped path |
| 6 | **Reframe paper emphasis**: reliability/correctness primary, token efficiency secondary | Paper draft | Intro + abstract reflect reliability framing |

## Debate Files

- `debate/ecosystem-landscape-2026.md` — Full landscape analysis
- `debate/ecosystem-pivot-claude-draft.md` — Claude's initial position
- `debate/ecosystem-pivot-claude-self-review.md` — Claude's self-critique
- `debate/ecosystem-pivot-codex-critique.md` — Codex Round 1 critique
- `debate/ecosystem-pivot-claude-response-1.md` — Claude's response
- `debate/ecosystem-pivot-codex-rebuttal-1.md` — Codex Round 2 rebuttal
- `debate/ecosystem-pivot-critique-log.json` — Structured critique log (14 points)
- `debate/ecosystem-pivot-summary.md` — This file

## Costs

| Invocation | Wall-clock time | Model version |
|------------|-----------------|---------------|
| Codex R1 | ~3m | gpt-5.3-codex |
| Codex R2 | ~2m | gpt-5.3-codex |
