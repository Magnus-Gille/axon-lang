# Self-review — AXON falsification pivot

## Debate Type
Primary: priority/product
Secondary: protocol

## Priority/product checklist

- **Evidence supporting this priority over alternatives?** Strong on the cost axis (gzip/binary/
  caching measured), weaker on *novelty* of the negative result (U1). The pivot is well-evidenced;
  whether it's *publishable* is the real open question, not whether AXON loses.
- **Opportunity costs?** Pivoting to a negative-result paper forecloses the "build AXON v2 with
  constrained decoding" path. But that path is independently killed by the economics, so the
  opportunity cost is low.
- **Load-bearing assumptions about behavior?** A2 (caching @0.1× of the structural slice) is the
  shakiest. In a real agent loop the *incoming* message is not in the cached prefix on first read,
  so the "caching erases AXON's edge" claim may be weaker than stated — it holds for *repeated/
  historical* messages, not the marginal new one. I think this is my biggest self-identified hole.
- **What does "done" look like?** A submitted negative-result paper that survives the "isn't this
  obvious?" objection by (a) quantifying the decision boundary and (b) shipping the falsification
  harness as a reusable artifact. Success = acceptance OR a clean, cited preprint.
- **Reversibility?** High — a negative-result framing is cheap to revise if a real niche surfaces.

## Protocol checklist (secondary)

- **State machine / in-flight / versioning:** mostly N/A (this is a content-format claim, not a
  live protocol). But one protocol-flavored gap: the analysis treats messages as *independent*;
  a real agent protocol has session state, schema negotiation (Agent Cards), and versioning —
  which *strengthens* the "just use a custom/negotiated schema" kill, so it cuts our way.
- **Client behavior on unexpected response:** AXON's emission floor means ~30% invalid messages;
  a deterministic receiver would reject them. We covered this (repair recovers ~half), but the
  *protocol-level* cost of a 1-in-3 reject rate vs JSON's ~0% is arguably under-weighted in the
  headline.

## Strongest argument against my own position

The cost-framed panel may have **dismissed non-cost value too fast** (A5/U3). A dense, *strict*,
deterministically-parseable notation that is *also* human-readable could have value where you want
**one artifact that is simultaneously: machine-parseable without an LLM, token-cheap enough to sit
in a prompt, and auditable by a human** — and where gzip/binary don't apply because the medium is
*the LLM context window itself* (you can't gzip a prompt). That is a real "tokens, not bytes, and
no compression layer" regime. The panel's "counting-unit dilemma" asserts this regime is empty,
but the in-context-DSL case (AXON as a planning/scratchpad notation a model emits AND a
deterministic tool parses, inside one context) is the one place the dilemma's two horns might both
be satisfied: token-billed AND deterministically parsed. I flagged this (U3) but did not fully
kill it — Codex should press here.

## Missing baselines / gaps

- No measurement of the **in-context / no-compression** regime (we measured wire bytes + tokens,
  but not "AXON vs JSON as a deterministically-parsed in-prompt DSL" where gzip is unavailable).
- The caching number is a **model, not a measurement** (stated, but the headline leans on it).
- "0/14" is a function of how the panel was seeded; a hostile reviewer will call it
  **adversarial-by-construction** (we conceded this, but it's a real external-validity limit).

## Operational/maintenance burden

Low — the pivot reduces scope (no AXON v2, no grammar-constrained engine). The harness is the
maintained artifact.
