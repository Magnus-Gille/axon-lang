> **Authoritative final report: `REPORT.md`** (executive summary + all results + future research).

# Semantic-reliability research — findings (live)

Attacking the real bottleneck (`PROBLEM.md`): reliable *semantic* encoding for agent messages.
After shape is fixed by structured outputs (~0.89 fidelity), the residual is **systematic value
errors**. Method: first-principles + wild experimentation + cross-lingual literature
(`crosslingual-synthesis.md`, running).

## The experimental arc (negatives are load-bearing)

| # | mechanism | tradition | result | lesson |
|---|---|---|---|---|
| 0 | structured outputs (baseline) | EN constrained decoding | 0.888 ± 0.007 | shape solved, ~0.11 semantic gap remains |
| 1 | **self-consistency** ensemble (k=5 majority vote) | EN / RU repetition code | **+0.000** | errors are **systematic (bias), not random (variance)** — repetition codes can't fix bias |
| 2a | thesaurus in the **schema** (json_schema descriptions) | RU Shreider thesaurus | **−0.012** | the box's `response_format` enforces *structure* and **drops descriptions** — they never reach the model |
| 2b | **thesaurus in the PROMPT** (per-field semantic defs) | RU Shreider thesaurus | **+0.062 → 0.950 ± 0.000** | ✅ confirmed: the error is a sender↔receiver **thesaurus mismatch**; aligning it fixes the role confusion |
| 3 | **same-model detection** of valid-but-wrong (self / receiver / +thesaurus framings) | EN self-verify / listener-speaker | recall **0.14** (all 3 identical) | ✗ the model can't catch its *own* systematic error — verification shares the generative **blind spot** (same reason self-consistency failed) |
| 4 | **INDEPENDENT-verifier detection** (claude -p, different family + thesaurus) | RU Burnashev feedback × listener>speaker asymmetry × ZH SemHARQ | recall **0.50** (catches the genuine role-confusions; T01 both, T08 both) | ✅ a genuinely independent view breaks the blind spot (0.14 → 0.50; the "misses" are mostly scorer-strict synonyms) |

## The diagnosis (why exp.1 had to fail before exp.2 could work)

Failure analysis of the persistent errors:
- **T01** (0.33): model put the *recipient* `@agent-b` in `target` and the queried entity in
  `subject`. **T08** (0.50): put the *recipient* `@admin` in `source`, `@web-server` in
  `root_cause`. The schema pins field *names + types* but **not the *meaning* of each slot**, so
  the model systematically **mis-assigns entities to roles** (recipient leaks into content fields;
  cause/source/root confused), the *same way every time*.
- That systematicity is exactly why **self-consistency gave +0.000** — majority vote corrects
  variance, and this is bias.
- It maps directly onto **Yu. A. Shreider's semantic information theory (RU)**: meaning is relative
  to the receiver's **thesaurus**; the failure is a sender/receiver *thesaurus mismatch*, not
  channel noise. The fix is **thesaurus alignment** — carry the per-field semantics where the model
  attends (the **prompt**, since the constraint engine ignores schema descriptions).

## The unified result — one theory explains the whole landscape

**Agent-message reliability is a THESAURUS-ALIGNMENT + INDEPENDENT-VERIFICATION problem.** The
dominant failure after structured outputs is *systematic semantic-role confusion* — a sender↔
receiver **thesaurus mismatch** (Shreider), not channel noise. That single diagnosis predicts every
result above:

- **Why self/variance methods fail** (self-consistency +0.000; same-model verification 0.14): they
  reuse the model's *own wrong thesaurus*, so they're internally consistent with the error — a
  **shared-bias blind spot**. This is a clean negative on the EN-mainstream self-verification /
  self-consistency reflex for this error class.
- **Prevention works (encoding side):** ship the shared thesaurus to the EMITTER, *in the prompt*
  (the constraint engine drops schema descriptions). **+0.062 → 0.950, σ=0.000.** ~Free, robust.
- **Detection works only with an INDEPENDENT view (receiver side):** a different-family verifier +
  thesaurus catches the genuine valid-but-wrong (**recall 0.14 → 0.50**) — the listener>speaker
  asymmetry + semantic-ARQ "independent view" (Burnashev / SemHARQ), confirmed.

So a practical, cheap recipe falls out: **(1) ship the shared field-semantics thesaurus to the
emitter prompt; (2) for high-stakes fields, verify with a *different* model that also holds the
thesaurus; (3) ARQ-patch the flagged fields.** None of it is a new notation — it's alignment +
an independent channel, exactly where AXON was orthogonal.

## Open frontier

1. **Push detection recall up:** the independent verifier's "misses" are mostly scorer-strict
   synonyms — a fidelity-aware (not exact-match) detector, or a 2-model verifier panel, should lift
   real recall well past 0.50. Then close the ARQ loop end-to-end (detect → patch → re-verify).
2. **Selective thesaurus** (only ambiguous fields) to remove exp.2b's single-run regressions.
3. **Robustness:** more senders/verifiers (coder-80b, gpt-oss, frontier), more & longer tasks;
   current results are n=14, one sender.
4. **Write-up:** this is a self-contained contribution — *"reliable agent communication is semantic-
   channel alignment, not notation; here are the mechanisms, drawn from RU semantic-information &
   feedback-coding theory, ZH semantic communication, and EN pragmatics/verification."*

## Files
`PROBLEM.md` (framing), `run_selfconsistency.py` (exp.1), `run_thesaurus.py` (exp.2),
`run_structured.py` reused from `../exp_incontext_dsl`. Cross-lingual survey → `crosslingual-synthesis.md`.
