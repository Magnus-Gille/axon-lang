# Overnight autonomous research — M5 capability-floor firming (2026-06-26 → 27)

**Mandate:** free use of the M5 box for experiments until ~06:00, then a short report.
**Question:** *Where exactly is AXON's capability floor — is it a writing floor or a reading
floor — with enough replication to separate signal from noise?*

The box is **serial** (one model loaded at a time; cold-swaps cost minutes), so work is phased,
each phase draining a model before the next. Token auth is self-healing now (m5_client fetches
fresh from `m5-auth` and auto-refreshes on 401), so long batches survive the ~20-min token TTL.

---

## Phase A — Headline replication (3 models, run0 vs run1) — DONE

- **Decoded-only fidelity is rock-stable**: run0 vs run1 |Δ| ≤ 0.006 for *every* condition
  (AXON 0.940 → 0.945, mid-pack both runs; json_schema top both runs). → "AXON is faithful
  once decoded" **replicates**.
- **Fidelity-capability ladder replicates** (large models above the mid model).
- **Validity-capability ladder is NOISY**: run0's clean 64 → 71 → **86%** climb flattened to
  **~57–62%** on run1 (coder fell 86% → 62% even excluding one transient empty encode). The
  "code model is 86% valid, best of all five formats" peak was **partly luck** → must be reported
  with run-variance, not as a point figure.

### Phase A.1 — run-aware refinement (`replication_stats.py`)

The sharper framing, from treating runs as repeated measures (2 runs so far):

- **The capability floor is a *syntactic-emission* floor, not a semantic one.**
  Decoded-only fidelity is **flat and high across every model** (qwen35 0.96, gemma4 0.93,
  qwen3-30b 0.91, gpt-oss 0.96, coder 0.96; per-run SD ≈ 0). AXON is recovered faithfully
  *once it parses*, regardless of sender capability. **All** the capability dependence lives
  in **validity** (can the model emit parseable AXON at all).
- **Validity ladder is directional but noisy** (mean ± SD across 2 runs):
  gemma4 46±4 → qwen35 57 → qwen3-30b 61±4 → gpt-oss 64±7 → **coder 71±14**. It climbs with
  capability, but the top is wobbly (coder ±14) — run0's 86% was within noise. → more runs
  (Phase C) to tighten the SDs and confirm direction.
- Test-retest fidelity (cells decoded in *both* runs) is near-perfect (AXON r≈1.0), i.e. the
  cells that decode are stable; the variance is entirely in *which* cells decode — reinforcing
  that emission/validity, not recovery, is the unstable axis.

## Phase B — AXON grammar-failure taxonomy (box-free, existing data) — DONE

Across all emitted AXON (n=106 ok messages, 2 runs on 3 models + 1 run on 2 models):

- **33% of emitted AXON is invalid.**
- **Invalidity scales steeply with composition depth:** L1 **6%** → L2 **39%** → L3 **53%**.
  This is the cleanest, most robust failure signal — exactly the compositional payloads AXON's
  operators were supposed to win are where the model most often can't emit valid AXON.
- **Top failure constructs** (multi-label, n=35 invalid):
  | count | construct |
  |---|---|
  | 12 | unquoted time / range (`02:00..04:00`) |
  | 11 | other / uncategorized |
  |  6 | bare comma-list not in `[]` (`@a, @b`) |
  |  5 | keyless / malformed record (`{value}`, `{x>y}`) |
  |  3 | unit/% or comparison inside a token (`cpu>95%`) |
- Parser errors: 30 ParseError, 5 LexerError.
- **Actionable for the spec:** a handful of grammar relaxations (quoted-free time literals,
  comparison operators in values, lenient list separators) would plausibly absorb the majority
  of failures — i.e. much of the "capability floor" is a *small, fixable grammar-surface gap*,
  not a deep semantic limit. (To be cross-checked against the repair experiment, Phase E.)

## Phase E — Deterministic syntactic repair (box-free) — DONE (fidelity check queued)

The taxonomy implied much of the emission floor is *surface-syntax strictness*. Tested it
directly with `axon_repair.py` — a ~15-line, **meaning-preserving** normalizer (no model, no
box) applied only to messages the strict grammar rejects:
- **R1** multi-receiver routing `(@X>@a, @b, @c)` → `(@X>[@a,@b,@c])`
- **R2** bare clock-time `02:00` → `"02:00"` (so `:` isn't read as a record separator)
- **R3** bare labelled record `alert{level:3}` → `#alert{level:3}` (tag)

**Result: 24/46 invalid AXON messages (52%) become parseable** — for free, deterministically.
Fired: R2 quote-time ×16, R3 tag-record ×11, R1 routing-list ×5. → **roughly half of AXON's
"capability floor" is a spec-strictness gap a lenient preprocessor/grammar closes**, not a
model-capability wall. Repaired messages saved to `results/repaired_axon.jsonl`.

⚠ **Caveat (the key check):** parse-recovery ≠ correctness. The repairs are meaning-preserving
by construction, but I must confirm the repaired messages *decode to the right fields* (no
valid-but-wrong, the failure mode that bit retry-until-valid in §4.6). **Decode+fidelity check
queued for the next box window (Phase F).** If fidelity holds, this is the practical headline:
AXON's emission floor is cheaply, safely removable.

## Phase C — Extra replications (runs 3–4, headline models) — RUNNING (byjf2rqsw)
## Phase D — Cross-model decode sweep (multiple readers) — PENDING
## Phase F — Decode repaired AXON → confirm fidelity holds — QUEUED (box)

---

*(Running log; updated as each phase lands. Final summary at the end.)*
