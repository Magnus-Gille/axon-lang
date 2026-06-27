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

## Result so far

A robust **+0.062** (0.888 → **0.950**, σ=0.000 over 3 reps, qwen3-30b) from a ~free move:
put the field-semantics (the shared thesaurus) in the prompt alongside structured outputs.
Crosses the ≥0.95 target. **The placement finding is itself useful:** schema descriptions are
dropped by `response_format`; the thesaurus must be in the prompt.

## Open frontier (next experiments)

1. **Semantic-error DETECTION** (the other half of the success criterion — catch *valid-but-wrong*):
   a cheap semantic checksum / ARQ-style cross-check so the receiver *knows* when a message is
   wrong. (Awaiting cross-lingual synthesis: RU помехоустойчивое кодирование / ARQ, ZH 语义通信
   fidelity metrics, biological proofreading.)
2. **Residual ~0.05 gap + selective thesaurus** — exp.2b had single-run regressions on a couple of
   already-correct tasks; a *selective* thesaurus (only ambiguous fields) may push higher without
   the regressions.
3. **Robustness:** more models (qwen3-coder, gpt-oss, a frontier sender), more tasks; current
   result is n=14, one model.
4. **Combine** with whatever the cross-lingual synthesis surfaces.

## Files
`PROBLEM.md` (framing), `run_selfconsistency.py` (exp.1), `run_thesaurus.py` (exp.2),
`run_structured.py` reused from `../exp_incontext_dsl`. Cross-lingual survey → `crosslingual-synthesis.md`.
