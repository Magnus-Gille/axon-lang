# Debate summary — AXON falsification pivot

**Date:** 2026-06-27
**Participants:** Claude (Opus 4.8) vs **Reviewer: codex / gpt-5.5** (xhigh effort)
**Rounds:** 2 (converged)
**Snapshot:** commit `cdd2592` — `experiments/exp_m5_falsification/{REPORT.md §4.9/§6, OVERNIGHT_FINDINGS.md, wire_economics.py}`
**Type:** priority/product (primary), protocol (secondary)
**Munin:** reviewer loaded live `projects/axon/status` + (R2) `decisions/drone-lab-c2-protocol/axon-fit-evaluation`

## The question

Is the pivot "AXON earns no defensible place as a general agent-communication notation; pivot the contribution to a negative result + falsification methodology" sound, or over-reached?

## Outcome: pivot direction upheld, universal claim narrowed

Both sides agree the *direction* is right — AXON as a free-form LLM-emitted default notation is in trouble (sender-side emission floor, no read-fidelity upside over JSON, weak economics under stream/binary/cached regimes). But the *universal* phrasing ("essentially never," "the regime is empty," "AXON-the-language earns no defensible place") over-reached and is retired.

**Defensible claim (agreed):** *The M5 evidence falsifies AXON as a **free-form / weakly-scaffolded LLM-emitted general/default payload notation** under the tested distribution, and closes the large-model token-wire pitch under stream-gzip + binary-schema + LLM-reader assumptions. Two regimes remain **untested** (separate theses, not falsified): (i) in-context deterministic-DSL use (token-billed, deterministically parsed, no compression layer); (ii) human/planner-authored AXON for constrained tactical channels (drone-C2).*

## Concessions accepted by both sides

- **Per-message vs stream gzip (critical correction).** The 12 B/msg kill is *stream* gzip; per-message gzip(JSON)=119 B > raw AXON 75 B. Report per-message / stream / no-compression regimes separately. *(Self-review missed this.)*
- **"essentially never" → scoped negative.** Drop the universal; bound to free-form/weakly-scaffolded LLM emission under the tested distribution.
- **Caching 31%→9% is a sensitivity model, not a measurement** (the marginal incoming message isn't prefix-cached).
- **"0/14" is adversarial-search evidence, not a survey.**
- **drone-C2 reconciliation (critical).** Live Munin holds a 2026-04-24 "use it, but scoped" decision: human/planner-authored AXON over kbps tactical radios — which sidesteps the emission floor, runs on a no-compression channel, and is valued for non-cost reasons. The M5 study doesn't touch it. Must be a **scope table splitting two theses**, not a footnote. *(Self-review missed this — only live memory surfaced it.)*
- **Contribution reframed** to the falsification method + write-hard/read-easy asymmetry + sender-side emission floor + validity-vs-fidelity split + deterministic repair + decision-boundary framework (not the gzip anecdote).
- **Reversibility / brand-burn** — publish the framework + scoped result with surviving hypotheses scheduled, not a universal negative.

## Defenses accepted by the reviewer

- **D1 — direction, not just scope:** valid. For the thing actually tested (free-form LLM-emitted default format), the pivot is substantive, not just caution.
- **D2 — surviving regimes have headwinds:** valid — but "I expect AXON to lose there" is a prior, not a result, and must not be smuggled into the conclusion.

## Unresolved / required edits before drafting

1. Tighten scope label to **"free-form / weakly-scaffolded LLM-emitted"** (excludes true constrained decoding / structured outputs).
2. **Pick the paper's object:** "payload notation emitted by LLMs" (protocol deferral OK) **or** "agent-communication notation" (then NAK/ERR/reject-retry state-machine accounting is mandatory). Title/abstract must commit.
3. Add the **two-thesis scope table** (LLM-emitted payload vs human-authored constrained-channel DSL).

## Final verdict (both sides)

Revised, scoped position is **defensible** with the precision edits above. **Single most important next step:** run a **minimal in-context deterministic-DSL falsification pilot** before drafting — reuse the 14 tasks; add competitive arms (AXON, AXON+repair, AXON+true-constrained-decoding, compact JSON, JSON structured-outputs, TOON, one hand-built task DSL); one capable local + one frontier sender; account for marginal/cached/per-msg-gzip/stream-gzip/binary bytes + parse→validate→NAK/repair/retry/fallback cost. If AXON loses there too, the scoped negative result is clean and publishable (workshop / negative-results / arXiv-with-caveats).

## Track B (cross-model value)

15 critique points logged. **Self-review catch rate: 6/15 (40%).** Cross-model added 9, including **2 of the 3 critical-severity classes self-review would never have caught**: the per-message-vs-stream gzip arithmetic error, and the drone-C2 memory counterexample (surfaced only via the reviewer's live Munin access). Strong evidence the cross-model gap + live-memory grounding catch classes self-review structurally misses.

## Files
- `axon-falsification-pivot-claude-draft.md`
- `axon-falsification-pivot-claude-self-review.md`
- `axon-falsification-pivot-codex-critique.md`
- `axon-falsification-pivot-claude-response-1.md`
- `axon-falsification-pivot-codex-rebuttal-1.md`
- `axon-falsification-pivot-critique-log.json`
- `axon-falsification-pivot-summary.md`

## Costs
| Invocation   | Wall-clock time | Model    |
|--------------|-----------------|----------|
| codex R1     | ~6 min          | gpt-5.5  |
| codex R2     | ~3 min          | gpt-5.5  |
