# The real bottleneck: reliable *semantic* encoding for agent communication

## What the pilots established (so we attack the right thing)

Three layers of the agent-comms problem are already solved by existing tech — and AXON was
orthogonal to all three:
- **bytes** → gzip / binary codecs (the wire is not the problem)
- **shape / syntax** → structured outputs / grammar-constrained decoding (~100% schema-valid)

What is left — and what *every* format failed at under a deterministic consumer — is **semantics**:
1. **Semantic fidelity gap.** Even schema-constrained emission lands ~**0.89**, not 1.0 (in-context
   pilot, qwen3-30b). The model fills the *right fields* with *wrong / dropped / hallucinated values*.
2. **Valid-but-wrong is silent.** Structured outputs guarantees SHAPE, never MEANING. A schema-valid
   message with wrong content passes undetected and propagates downstream. (We saw this kill
   retry-until-valid in M5 §4.6 too.)

> **The real bottleneck:** get an LLM to put the *right meaning* into a machine-consumable message,
> and let the receiver *know when it didn't* — cheaply.

## First-principles frame: agent comms as a noisy *semantic* channel

Model sender→receiver as a channel whose noise is **LLM semantic error** (a field dropped,
distorted, or hallucinated). Shannon/coding theory then gives the toolkit — applied to MEANING,
not bits:

1. **Redundancy → detect + correct** (repetition / parity codes): self-consistency ensembles;
   dual-encoding *semantic checksums* (carry the content twice in independent encodings, cross-check).
2. **Feedback / ARQ** (automatic repeat request): a semantic *error-detecting code* + a handshake —
   the receiver flags a suspect message and asks for re-send instead of acting on garbage.
3. **Constraint → make errors impossible**: value-set + cross-field-invariant constrained decoding
   *grounded in the source intent* (not just type constraints).
4. **Verify-repair** (source coding + check): extract → verify each field against the source → fix —
   the semantic analog of the deterministic syntax repair we already built.

## Why a cross-lingual synthesis is the actual edge

Three research traditions each own a piece and rarely cite each other:
- 🇷🇺 **Russian** — *semantic* information theory (Kharkevich's *value of information*; Yu. Shreider's
  semantic information; Kolmogorov complexity) + *помехоустойчивое кодирование* (noise-resilient
  channel coding, ARQ). The theory of **reliable meaning-transfer over a noisy channel.**
- 🇨🇳 **Chinese** — *语义通信* (semantic communication for 6G: transmit *meaning* not bits, with DL
  encoders) + LLM-*智能体* (agent) reliability + *结构化生成 / 工具学习* (structured generation /
  tool learning). The **engineering of meaning-channels at scale.**
- 🇬🇧 **English** — constrained/grammar-guided decoding, self-consistency, LLM-as-verifier, tool-call
  reliability. The **LLM-emission toolkit.**

Russian semantic-channel *theory* + Chinese semantic-communication *engineering* + English
LLM-decoding *mechanisms* is a combination nobody seems to have assembled. That's the bet.

Plus deliberately-tangential inspiration: Gricean pragmatics (cooperative principle / maxims),
biological signaling codes (kin-recognition, error-tolerant molecular codes), TCP/ARQ checksums.

## Success criterion (measured on the existing 14-task harness + M5 box)

- Push schema-constrained agent-message fidelity from **0.89 → ≥0.95**, AND/OR
- add a **cheap semantic-error detector** that catches valid-but-wrong with high recall,
- at low token / call overhead.

Wild experiments encouraged. Negative results logged. Mechanisms credited to the tradition they
draw from (the cross-lingual provenance is part of the contribution).
