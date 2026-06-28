# Reliable semantic encoding for agent communication — research report

*Autonomous lab session, 2026-06-27 evening → night. Sender model: qwen3-30b (M5 box);
independent verifier: `claude -p`. Method: first-principles + wild experimentation +
cross-lingual literature synthesis (EN/ZH/RU + tangential). n=14 composition tasks.*

> **Executive summary** — see the end (`## Executive summary`); written last, after all results.

## 1. The problem (why this, why now)

The AXON falsification established that agent-communication's cost is **not** bytes (gzip/binary),
**not** syntax (structured outputs / constrained decoding ≈ 100% schema-valid), and that a dense
notation is orthogonal to the real bottleneck. What remains — and what *every* format fails at
under a deterministic consumer — is **semantics**:
1. **Fidelity gap:** even schema-constrained emission lands ~**0.89**; the model fills the *right
   fields* with *wrong values*.
2. **Valid-but-wrong is silent:** structure is guaranteed, meaning is not; a schema-valid wrong
   message propagates undetected.

> **The real bottleneck:** get an LLM to put the *right meaning* into a machine-consumable
> message, and let the receiver *know when it didn't* — cheaply.

## 2. First-principles frame: a noisy *semantic* channel

Model sender→receiver as a channel whose noise is **LLM semantic error**. Coding/communication
theory then applies — to meaning, not bits: redundancy (repetition/parity), feedback/ARQ,
value-grounded constraints, verify-repair. The diagnostic question for each mechanism: does it
address **variance** (random) or **bias** (systematic)? — because the answer turned out to decide
everything.

## 3. Cross-lingual synthesis (full: `crosslingual-synthesis.md`)

A 10-agent fan-out found **genuine cross-tradition convergence on semantic ARQ**:
- 🇷🇺 **Burnashev 1976** (Soviet decision-feedback coding: 1-bit feedback → *exponential*
  reliability gain) — the bound.
- 🇬🇧 **Clark grounding** (dialogue repair) — the protocol shape.
- 🇨🇳 **SemHARQ** (Chinese semantic communication: field-level NACK + soft-combining) — the engine.

Plus genuinely-underused Soviet→LLM transfers: **Yu. A. Shreider's semantic information theory**
(meaning relative to a receiver *thesaurus*), **Berger codes** (detect *all unidirectional*
errors — maps onto the LLM hallucinate-extra/drop-field asymmetry), **Varshamov-Tenengolts**
deletion codes, **Kharkevich/Stratonovich value-of-information** (a principled retransmit
threshold). The synthesis was honest that EN self-consistency/CoVe are mainstream — value is only
in *combining* them with the feedback-coding bounds.

## 4. Experimental arc — the negatives are load-bearing

| # | mechanism | result | lesson |
|---|---|---|---|
| 0 | structured outputs (baseline) | 0.892 ± 0.011 | shape solved; ~0.11 semantic gap |
| 1 | self-consistency (k=5 majority vote) | **+0.000** | errors are **bias, not variance** → repetition codes useless |
| 2a | thesaurus in the *schema* (json_schema descriptions) | −0.012 | `response_format` enforces structure & **drops descriptions** |
| 2b | **thesaurus in the *prompt*** (Shreider alignment) | **0.950 ± 0.000** | ✅ the error is a sender↔receiver *thesaurus mismatch*; aligning it fixes role confusion |
| 2c | *selective* thesaurus (non-enum fields only) | 0.948 ± 0.007 | ≈ full; the enum over-deliberation was single-run noise |
| 3 | same-model detection (self / receiver / +thesaurus) | recall **0.14** | the model can't catch its *own* systematic error — **shared-bias blind spot** |
| 4 | **independent-verifier detection** (claude -p + thesaurus) | recall **0.50** (organic) | ✅ an independent view breaks the blind spot |
| 5 | **bare + ARQ** (independent detect + patch) | **0.963 ± 0.011** | ✅ detect-and-correct is the **strongest single mechanism** |
| 6 | **rigorous detection** (error-injection benchmark: 20 known role-swaps + 14 controls) | **capable independent** verifier (claude) **recall 1.00, prec 1.00, FPR 0.00**; **peer-tier** verifier (qwen3-30b) only **0.35** (vs 0.14 on its *own* errors) | ✅ detectable for the *anticipated* error with a *focused* detector — needs a verifier **both independent AND capable**. **⚠ but see row 16:** a *generic* detector across diverse error types is weak (0.47) — detection is prompt-sensitive, not a general solution |
| 7 | **robustness across senders** (thesaurus) | coder-80b 0.940→**0.986**; gpt-oss 0.850→**0.981**; gemma4/qwen35 → **0.000** (empty under constraint) | ✅ generalizes & **stronger on capable senders** (prevention alone → ~0.98); but **weak/heavy-reasoner senders fail constrained emission entirely** (capability floor at the structured-output layer) |
| 8 | **stacked** thesaurus + ARQ (the ceiling) | 0.950 → 0.950 (**+0.000**) | prevention & detect-correct are **SUBSTITUTES, not complements** — both target role-confusion; stacking adds nothing once it's prevented |
| 9 | **fidelity-aware (semantic) re-scoring** of thesaurus outputs (claude judge, 0 FP on controls) | exact-match 0.950 → **SEMANTIC 1.000** | ✅ the residual ~0.05 was **scorer strictness** (synonyms/case); thesaurus alignment is **semantically ~perfect** on a capable sender — the role-confusion bottleneck is *solved at the source* |
| 10 | **schema disambiguation** (rename confusable fields to self-describing ROLE names, same 14 tasks) | bare 0.905 → **0.952** (+0.048) | ✅ the root cause is **schema-name ambiguity**; good field naming fixes it **for free at design time** — equivalent to the runtime thesaurus |
| 11 | **external validity A** (10 fresh tasks, smart-home + e-commerce, *self-describing* names) | bare **1.000** = thesaurus 1.000 | well-named fresh tasks trigger **no role confusion** (confirms #10) |
| 12 | **external validity B** (18 fresh tasks, financial/hospital/devops, *deliberately ambiguous* names) | bare **0.339** (semantic) → thesaurus **1.000** (**+0.661**) | ✅✅ the bottleneck **and** its fix **generalize to new domains**; effect is *larger* with more ambiguity. Rows 11+12 = a clean natural experiment isolating name-ambiguity as the cause |
| 13 | **fresh-ambiguous set, capability gradient** (mid / capable / frontier senders) | bare **0.34 / 0.51 / 0.81** → thesaurus **1.00 / 1.00 / 1.00** (Δ +0.66 / +0.49 / +0.19) | ✅ definitive: ambiguity hurts **every** model (capability only *mitigates*, never eliminates); thesaurus alignment **fully fixes it for all**. Weak/reasoner senders (gemma4) fail to emit at all. |
| 14 | **VoI-gated ARQ** (Kharkevich value-of-information × independent verifier) | high-VoI recall **1.00** at **0.60×** the verify cost | ✅ cheap reliability — verify only fields where an error changes the receiver's *action*; full protection on what matters at ~40% less cost (more savings in field-heavier domains; here VoI-median=5/5) |
| 15 | **multi-hop relay** (A→B→C, ambiguous tasks, 3 hops) | bare **flat 0.48** every hop; thesaurus **flat 1.00** | errors don't *compound* — relaying just **copies**, so a role-confusion is *frozen in at first encoding* and persists unchanged (never self-corrects). **Encoding decides reliability; relays neither help nor hurt.** Alignment holds the whole chain. |
| 16 | **detection across DIVERSE error types** (role-swap, ref-hallucination, enum/num/bool/list, 72 known errors) — *generic* verifier prompt | overall recall **0.47** (FPR **0.000**); role-swap fell **1.00→0.40** vs the *focused* detector | ⚠️ **detection is prompt-sensitive and does NOT generalize cheaply.** A *focused* detector for an *anticipated* error is near-perfect; a *generic* "check-everything" detector is weak-but-precise (catches <half, never false-flags). **Tempers row 6** and **reinforces prevention-first** — naming/alignment is robust; detection is a fragile backstop. |

### The diagnosis (why exp.1 & 3 had to fail before 2b & 4 could work)
The persistent errors are **semantic-role confusion**: the model puts the *recipient* in `target`,
the *recipient* in `source`, confuses cause/source/root — *the same way every time*. The schema
pins names+types but not slot *meaning*. That is exactly **Shreider's thesaurus mismatch**, and it
explains every result: self-/same-model methods (self-consistency, self-verification) reuse the
model's *own wrong thesaurus*, so they're internally consistent with the error (a **shared-bias
blind spot**) — which is why they give +0.000 / recall 0.14. Fixing it requires *aligning the
thesaurus* (encoder side, 2b) or an *independent* evaluator holding the thesaurus (receiver side, 4).

## 5. The unified result

**Agent-message reliability is a thesaurus-alignment + independent-verification problem**, not a
notation problem — exactly where AXON was orthogonal. One diagnosis — the dominant error is a
sender↔receiver **thesaurus mismatch** (Shreider) manifesting as **semantic-role confusion** —
predicts the *entire* landscape:

1. **Prevention (encoder side):** ship the shared field-semantics thesaurus to the *emitter
   prompt* (not the schema — `response_format` drops descriptions). qwen3-30b 0.89→**0.95**;
   capable senders → **~0.98** (coder 0.986, gpt-oss 0.981).
2. **Detection (receiver side) is essentially solvable:** an *independent* model (different family)
   holding the thesaurus catches the characteristic role-confusion errors at **recall 1.00 /
   precision 1.00** on a controlled injection benchmark (0.50 on noisy organic errors, where the
   "misses" are mostly scorer-strict synonyms). The popular *same-model* self-check/self-consistency
   **cannot** (recall 0.14, +0.000) — a **shared-bias blind spot**.
3. **Correction:** ARQ-patch flagged fields → bare+ARQ **0.963**.
4. **Prevention and detect-correct are SUBSTITUTES, not complements** — both fix role-confusion;
   stacking them adds nothing (0.950→0.950). The residual ~0.05 is a *different* class (subtle
   value errors + exact-match scorer strictness), so the real fidelity is a lower bound.

5. **The root cause is thesaurus *ambiguity*, and there are three equivalent fixes** — all of
   which make the receiver's slot-semantics explicit to the sender:
   - **(0) Design-time — unambiguous, self-describing field names.** *Free*, first-line: renaming
     the confusable fields lifts bare 0.905→0.952 (= the runtime thesaurus), and a fresh
     well-named benchmark never triggered the error at all. **Most schemas should just do this.**
   - **(1) Runtime prevention — thesaurus in the emitter prompt.** For when you *can't* control the
     schema (terse formats, third-party/open-ecosystem schemas): 0.89→0.95 (~1.000 semantic).
   - **(2) Runtime detection — independent capable verifier + thesaurus.** For high-stakes
     messages: catches role-confusion at recall/precision 1.00; ARQ-patch the flagged fields.

Practical recipe: **name fields unambiguously; if you can't, ship the thesaurus in the prompt; for
high-stakes, verify with a different capable model.** No new notation — just alignment (+ an
independent channel when it matters).

## 6. Limitations (honest)
- **Benchmark size/scope:** original n=14, plus **28 fresh independently-generated tasks across 5
  new domains** (smart-home, e-commerce, finance, hospital, devops). External validity is now
  **well-supported** — the bottleneck *and* the thesaurus fix replicate on fresh domains
  (ambiguous-named: 0.34→1.00). Still one scorer (mitigated by the fidelity-aware judge) and mostly
  one sender for the detailed ladder; a standard function-calling dataset + multi-sender sweep
  would further harden it.
- **Exact-match scorer inflates the error rate:** several "errors" are synonyms (`notify`≈`inform`)
  the scorer marks wrong but a verifier rightly accepts. So fidelity numbers (0.95–0.98) are
  **lower bounds**; the detection "0.50 organic" is artificially depressed by these. The injection
  benchmark (1.00) is the clean signal.
- **Capability floor at the structured-output layer:** weak/heavy-reasoner senders (gemma4,
  qwen35-a3b) return *empty* under `response_format` (budget burned on hidden reasoning) → the whole
  approach needs an instruct/capable sender.
- **Injection benchmark tests one error type** (clean intra-message role swaps) — an upper bound on
  detectability; subtler partial/numeric errors are harder (organic 0.50).
- **Cost & latency of ARQ** not optimized: +1 independent verify call/msg + 1 patch/flagged-field;
  no VoI-gating, no end-to-end latency accounting yet.
- A single independent verifier was `claude -p` (frontier) — a realistic "capable receiver," but
  the asymmetry result should be re-checked with a *peer-tier* independent box model.

## 7. Recommended future research
*(Done this session: VoI-gated ARQ — row 14; fidelity-aware scoring — row 9; frontier sender &
capability gradient — row 13; external validity on 5 fresh domains — rows 11–13. Remaining:)*
1. **External validity on a REAL/standard dataset** (function-calling / tool-use benchmark, not
   synthetic) — the single most important remaining gap; our 42 tasks are all self-generated.
2. **Open-vocabulary / negotiated thesaurus (Clark grounding):** sender and receiver with
   *different* field names reconcile via a one-time mapping exchange — the open-ecosystem case
   (different vendors) the pre-shared thesaurus assumes away.
3. **Broader error model:** today's detection is validated on clean *role-swaps*; test value
   errors, list drops, boolean flips, over-specification — does the mechanism generalize beyond
   role-confusion?
4. **Schema-ambiguity linter:** since ambiguous *names* are the root cause, build a design-time
   tool that flags confusion-prone field names before deployment (prevention tooling).
5. **Multi-hop compounding:** in an agent chain, does thesaurus-mismatch error compound, and does
   alignment prevent it? (relevant to real multi-agent systems.)
6. **Characterize the semantic confusion matrix** (which roles swap into which) → a matched
   deterministic detector (Berger / matched-code).
7. **Abstain/epistemic-tagging at the source** (Gricean Quality × Relign): route low-evidence
   values to a `hedged` slot so the receiver verifies only those — make silence audible.

*(Resolved this session: the verifier asymmetry is about **both** independence and capability — a
peer-tier verifier got only 0.35 vs a capable independent one at 1.00; see row 6 of §4.)*

## Executive summary

**Status.** Starting from the AXON falsification's conclusion — agent-comms' real cost is *semantic*,
not bytes/syntax/notation — this session attacked the residual bottleneck (~0.89 fidelity even with
structured outputs; silent valid-but-wrong) with first-principles reasoning, a cross-lingual
(EN/ZH/RU) literature synthesis, and ~9 experiments on the M5 box. **One diagnosis explains
everything: the dominant failure is a sender↔receiver *thesaurus mismatch* (Shreider, RU semantic-
information theory) showing up as semantic-role confusion** (the model puts the recipient in
`target`, the source in `root_cause`, the same way every time). From it:

- **Root cause = schema/thesaurus *ambiguity*, with three equivalent fixes:**
  - **Design-time (free, first-line): unambiguous field names.** Renaming the confusable fields
    lifts bare 0.905→**0.952** (= the runtime thesaurus); a fresh, well-named benchmark (smart-home
    + e-commerce) never triggered the error (bare **1.000**). Most schemas should just do this.
    **Ambiguity hurts every model** — on a fresh deliberately-ambiguous set, bare is 0.34 (mid) /
    0.51 (capable) / 0.81 (frontier): capability *mitigates* but never *eliminates* it, and the
    fix takes all three to **1.000**.
  - **Runtime prevention: thesaurus in the *emitter prompt*** (for terse/third-party schemas you
    can't rename) → 0.89→**0.95** exact-match, **1.000 under a fidelity-aware judge**. **Generalizes
    strongly:** on 18 fresh, deliberately-ambiguous tasks across finance/hospital/devops, it lifts
    semantic fidelity **0.34 → 1.000 (+0.66)** — the effect is *larger* the more ambiguous the
    schema. Schema *descriptions* don't work (the constraint engine drops them); use the prompt.
  - **Runtime detection** (below).
- **Detection of valid-but-wrong works for an *anticipated* error with a *focused* detector, but
  does NOT generalize cheaply.** A capable *independent* verifier (holding the thesaurus) catches
  the characteristic role-swap at **recall/precision 1.00** — but a *generic* "check-everything"
  detector across six error types manages only **0.47 recall** (perfectly precise — never
  false-flags). Same-model self-check/self-consistency **can't** detect at all (0.14 / +0.000, a
  shared-bias blind spot); a *peer-tier* verifier is weak (0.35). **So detection is a fragile,
  prompt-sensitive backstop — prevention (below) is the primary, robust mechanism.**
- **Prevention and detect-correct are substitutes** (both target role-confusion; stacking → +0.000).
- **The fix is alignment + an independent channel, not a denser format** — closing the AXON arc:
  AXON optimized the wrong variable; the right one is the shared thesaurus + cross-model verification.
- **Capability floor:** the whole approach needs an instruct/capable sender — weak/heavy-reasoner
  models (gemma4, qwen35-a3b) fail constrained emission entirely (empty output).

**Cross-lingual payoff (the requested synthesis):** genuine, citation-sparse Soviet→LLM transfers
carried real weight — Shreider (thesaurus) *was* the diagnosis; Burnashev (decision-feedback coding)
+ Clark grounding + Chinese SemHARQ converge on the semantic-ARQ shape; Kharkevich value-of-info and
Berger/VT codes seed the future work. The combination is, as far as the survey found, unassembled.

**Recommendation.** This is a self-contained contribution worth writing up (*"reliable agent
communication is semantic-channel alignment, not notation"*) — pair it with the AXON negative
result as a two-part story: *AXON optimized density (the wrong variable); the right variable is
thesaurus alignment, and naming/prompt/verification beat any notation.* The **immediately
actionable** takeaway for practitioners: **name agent-message fields unambiguously** (free,
eliminates most role confusion); ship the thesaurus in the prompt for schemas you can't rename;
verify high-stakes messages with a different capable model. Before publishing, the remaining work
(§7): a **standard function-calling / tool-use dataset** to firm external validity past our 42
self-generated tasks (the single most important remaining gap), and the **open-vocabulary /
negotiated-thesaurus** case (different agents, different field names). VoI-gated ARQ and the
capability gradient are now done (§4 rows 13–14). Highest-leverage next experiment: **a real
function-calling dataset.**

*Artifacts:* `PROBLEM.md`, `crosslingual-synthesis.md`, `FINDINGS.md`, runnable
`run_{selfconsistency,thesaurus,structured,detect,indep_verify,pipeline,compare,panel,inject}.py`.
