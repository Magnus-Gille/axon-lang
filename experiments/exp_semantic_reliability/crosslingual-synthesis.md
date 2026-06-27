# Cross-lingual synthesis — reliable semantic encoding for agent messages

Source: 10-agent fan-out (🇬🇧 EN constrained-decoding/verification, 🇨🇳 ZH 语义通信/agents/structured-gen,
🇷🇺 RU semantic-info-theory/coding-theory/cybernetics, + tangential pragmatics/biology/protocols) →
opus synthesis. The interesting result: **three traditions independently converge on feedback /
semantic ARQ**, each contributing a different layer.

## 5 strongest transferable mechanisms (prizing cross-tradition combinations)

1. **Two-phase semantic ARQ with a compact echo** — *Burnashev 1976 (Soviet decision-feedback
   coding: 1-bit feedback → **exponential** reliability gain at negligible bandwidth) × Clark
   grounding (dialogue repair turns) × Chinese SemHARQ (field-level distortion NACK + soft
   combining)*. Receiver returns a tiny semantic digest; sender patches only divergent fields.
   Genuine convergence — Burnashev gives the bound, Clark the protocol shape, SemHARQ the
   combining. Converts silent valid-but-wrong into *detected* error. Cost = O(digest) + a
   round-trip only on NACK paths.
2. **Receiver-side round-trip / pragmatic-surprisal checksum** — *IdentityChain × RSA ×
   Sieker-Zarrieß*. Decode the message back to NL, test entailment vs intent. Justified by the
   empirical **listener > speaker asymmetry**: receivers are better pragmatic evaluators than
   senders are generators → offload detection to the receiver (contradicts naive self-check). Cost
   = 1–2 forward passes, no ground truth.
3. **Field-level abstain slot + epistemic-source tagging** — *Gricean Quality maxim × SJTU Relign
   (reliability-DPO) × cancelability*. Route low-evidence values to an explicit `hedged`/`abstain`
   slot instead of confabulating; tag each field `retrieved|inferred|generated`; the receiver
   spends verification budget only on hedged/inferred fields. Attacks the error at the source,
   makes silence audible.
4. **Importance-stratified unequal protection + cheap positional checksum** — *Chinese UEP-RL
   (entity-preservation) × Varshamov-Tenengolts deletion codes × **Berger sum-codes** (Soviet
   self-checking circuits — provably detect **all unidirectional errors**)*. Rank fields
   (ACTION > RECIPIENT > VALUES > RATIONALE); heavy protection on top tiers; attach an O(log N)
   position-weighted checksum. The genuinely novel transfer: **Berger's unidirectional-error
   optimality maps onto the LLM hallucinate-extra / drop-field asymmetry.** Near-zero runtime cost.
5. **Draft-first encoding, draft shipped as a verifiable header** — *CRANE / "Format Tax"
   (degradation enters via the prompt, before any decoder constraint) × CoVe-isolation ×
   **Kharkevich/Stratonovich Value-of-Information** (principled retransmit threshold)*. Reason in
   NL, encode conditioned on that draft, transmit a compressed draft as header; receiver verifies
   fields against header — a free round-trip needing no oracle.

**Honest novelty flags (from the synthesis):** the Soviet→LLM links (Burnashev, VT, Berger,
Kharkevich) are *genuinely* underused — ~zero citation penetration, structurally apt. The Chinese
SemHARQ link is real and unknown in NLP. The "semantic capacity C_s ≥ C" claim is framing, not a
mechanism. Self-consistency / CoVe / CRANE are already mainstream in EN NLP — their novelty is
*superficial*; value is only in **combining** them with the feedback-coding bounds.

## Top-3 proposed experiments (14-task harness, local model)

- **E1 — Two-phase echo ARQ** (mech 1) [novelty High × test High × impact High]: receiver echoes a
  field-value digest, sender patches mismatches (≤2 rounds). Metric: fidelity + detection rate of
  injected wrong-values. Predicted 0.89 → 0.95+, ~70% valid-but-wrong detected at <30% token o/h.
- **E2 — Berger/VT unidirectional checksum** (mech 4) [High × very-High × Medium]: append a
  position-weighted Berger sum over entity fields; measure silent substitutions/drops flagged with
  **zero LLM calls**. Predicted: ~all single drops/transpositions, 40–60% substitutions, ~free.
- **E3 — Draft-as-header round-trip vs self-check** (mech 5 × 2) [Med × High × High]: compare
  self-critique vs round-trip-decode vs draft-header verification. Predicted: round-trip ≈
  draft-header ≫ self-check — confirming the listener-speaker asymmetry.

## How this lands against our experiments so far

- Our **self-consistency null (+0.000)** is *predicted* by mech 2/E3: self-/variance methods don't
  fix systematic bias; the gain is on the **receiver/round-trip** side. ✓
- Our **thesaurus-in-prompt (+0.062)** is the *encoder*-side fix (Shreider, RU); the synthesis
  says the *detector*-side (catch valid-but-wrong) needs **feedback/ARQ + round-trip**, not
  self-check. → next experiments target detection.
- Key subtlety we must respect: the "noise" here is the **sender** (the encoder is the error
  source), so a sender-side checksum is self-consistent with its own error and detects nothing.
  Detection requires an **independent** view (round-trip decode compared against the sender-held
  intent) — exactly mech 1/2/5.
