# Draft — AXON earns no defensible place; pivot the contribution to a negative result

**Reviewer backend:** codex / gpt-5.5
**Snapshot:** commit `cdd2592`, files: `experiments/exp_m5_falsification/{REPORT.md (§4.9/§6), OVERNIGHT_FINDINGS.md, wire_economics.py}`
**Debate type:** priority/product (primary), protocol/architecture (secondary)

## Position

AXON-the-language does not survive its own evidence. The project's publishable contribution
should pivot from *"here is a dense agent-communication notation"* to a **negative result +
falsification methodology**: *"When does a general dense agent-communication notation beat JSON
or a custom API? Essentially never — read-tolerance + gzip + caching erase the density premium,
and there is no comprehension upside."*

### Evidence

1. **Use-case falsification (adversarial panel).** 7 generators × diverse lenses proposed
   candidate deployments; a skeptic killed each with the arsenal {custom API, JSON+FC,
   protobuf/CBOR, TOON, grammar-constrained schema, the emission floor}. **0 of 14 survived.**
2. **Wire economics, measured on the corpus (`wire_economics.py`).**
   - gzip: raw AXON 75 B/msg vs gzip(JSON) stream **12 B/msg** (−84%); gzip(AXON) 10 ≈ gzip(JSON) 12.
   - binary: AXON's *only* raw-byte win is over schemaless binary-with-keys (CBOR/msgpack ~98 B);
     schema-stripped positional binary (protobuf-like) **56 B / 8 B gzipped** beats AXON (75/10).
   - tokens: AXON's saving over JSON is **~100% structural overhead** (irreducible content ≈10
     tok identical); prompt-caching that structure @0.1× collapses the edge **31% → ~9%**.
3. **Read-fidelity ledger (our data).** An LLM reader recovers AXON at 0.942 — *below* json_schema
   (0.959) and ≈ plain json (0.938). No comprehension upside to trade density for.
4. **Counting-unit dilemma.** Strict validity only matters for a *deterministic parser* → then
   the wire bills **bytes**, where binary+gzip win. Token billing only happens with an *LLM
   reader* → then validity is moot and JSON ties on fidelity. The regime where AXON wins is empty.
5. **Codec reframe self-destructs.** Decode-before-LLM ⇒ byte wire ⇒ binary/gzip win;
   raw-AXON-to-LLM ⇒ reader returns, validity moot, JSON ties.

## Assumptions (load-bearing)

- A1. **gzip/Content-Encoding is "free and ubiquitous"** on the relevant transports (HTTP). If a
  transport can't gzip (raw TCP, some edge/embedded, or text pasted into a prompt with no
  compression layer), the byte-wire kill weakens.
- A2. **Prompt-caching applies to the structural slice at ~0.1×.** This assumes the repeated
  structure sits in a cacheable *prefix* and that caching is available/used. An *incoming* message
  appended to context is full-price on first read; the model is "long conversation where prior
  messages are cached."
- A3. **The corpus's message shapes are representative** of real agent payloads (14 composition-
  heavy tasks; short messages ~25-50 tok). On much larger or different-shaped payloads the ratios
  could move.
- A4. **The adversarial panel's "arsenal" is the right bar** — i.e., a use case must beat ALL of
  {custom API, JSON, binary, TOON, constrained schema} to count, and "specialized beats general"
  is decisive.
- A5. **Cost (tokens/bytes) is the axis that matters.** Non-cost value (auditability, determinism,
  human+machine readability) was judged not to create a standalone niche.

## Failure Modes (if the conclusion is wrong)

- We prematurely kill a format that *does* have a niche we mis-modeled (e.g., a no-gzip,
  no-caching, token-metered text channel between strong agents) — reputational cost is low
  (negative results are cheap to revise) but we'd miss a real contribution.
- The "negative result" paper is itself weak/un-novel if reviewers consider "dense text format
  loses to JSON+gzip" obvious or already known (TOON, prior compression work) — blast radius:
  desk-reject.
- Over-generalizing from 5 local open models + one fixed decoder + 14 tasks to "essentially
  never" — an external-validity overreach a reviewer will flag.

## Alternatives Rejected

- **Keep pitching AXON as a niche format** (terse payloads between strong code-tuned agents):
  rejected — the wire economics + 0/14 panel close that niche.
- **AXON as a deterministic wire codec** (LLM never writes it): rejected — splits into byte-wire
  (binary wins) or LLM-read (JSON ties); self-destructs.
- **Pursue grammar-constrained decoding to fix validity, then re-pitch:** rejected as the *headline*
  — it fixes emission but not the economics (gzip/caching/binary still win); worth a sentence,
  not a thesis.
- **Drop the project:** rejected — the negative result + the working falsification harness is a
  genuine, publishable contribution.

## Unknowns

- U1. Is the "negative result" *novel enough* to clear a workshop bar, or is "JSON+gzip beats a
  custom dense text format" folklore? (Venue framing risk.)
- U2. Does the caching @0.1× model survive a realistic agent-loop accounting (where incoming
  messages are *not* in the cached prefix)?
- U3. Is there a genuinely non-cost niche (regulatory/audit determinism, or AXON as a *human-
  authored* DSL for specifying agent behavior, not LLM-emitted) that the cost-framed panel
  dismissed too quickly?
- U4. Would a binary/byte transport ever *not* be available where this matters, reviving the
  text-token regime as a real moat?
