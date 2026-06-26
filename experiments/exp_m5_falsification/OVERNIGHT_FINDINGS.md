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

## Phase C — Replication to n=4 (3 headline models) — DONE

With 4 runs each, the validity "ladder" **collapses into a threshold, not a smooth climb**:

| model | #runs | validity % (mean±SD) | decoded fidelity |
|---|---|---|---|
| gemma4 (weak) | 2 | **36 ± 7** | 0.943 |
| qwen35-a3b (~3B) | 2 | **45 ± 12** | 0.979 |
| qwen3-30b (mid) | 4 | 66 ± 8 | 0.914 |
| gpt-oss-120b (large) | 4 | 70 ± 8 | 0.960 |
| qwen3-coder-80b (code) | 4 | 68 ± 11 | 0.953 |

- The three **capable models are statistically indistinguishable** (66–70%, overlapping SDs);
  the weak models sit far below (36–45%). So it's a **capability *threshold*** (below it AXON
  validity collapses; above it it plateaus ~68%), **not** a monotonic ladder.
- **The "code-tuned model is the best host (86% valid)" claim is REFUTED by replication** —
  coder (68±11) ≈ gpt-oss (70±8) ≈ qwen3-30b (66±8). Run0's 86% was noise. ← key correction.
- Decoded fidelity flat/high everywhere (0.91–0.98), reconfirming: floor = emission, not meaning.

## Phase F — Decode the repaired AXON (parse ≠ correct check) — DONE

Decoded the 24 repaired messages and scored vs ground truth:
- **Repairs are SAFE: 0/24 "valid-but-wrong"** (none drop below 0.5 fidelity). The §4.6
  failure mode of retry-until-valid (forcing parse → wrong meaning) does **not** occur here,
  because the repairs are meaning-preserving by construction.
- **But repair barely moves fidelity** (orig-invalid 0.877 → repaired 0.881, Δ+0.004): the LLM
  decoder *already* reads invalid AXON fine. → **validity barely matters to an LLM reader.**

**Repair recovery is ~uniform across capability** (gemma4 44%, qwen3-30b 53%, gpt-oss 50%,
coder 41%; overall 49%): weak and strong models fail in the *same repairable ways* — weak
models just make *more* slips, not deeper ones. Effective parse-validity after the free repair:

| model | orig valid% | + deterministic repair | lift |
|---|---|---|---|
| gemma4 | 53% | **74%** | +21 |
| qwen3-30b | 66% | **84%** | +18 |
| gpt-oss-120b | 71% | **85%** | +15 |
| qwen3-coder-80b | 69% | **82%** | +13 |

### Synthesis (the night's payoff)

1. **The capability floor is a syntactic-*emission* floor.** Decoded fidelity is flat & high
   (0.91–0.98) across every model; *only validity* varies. AXON is faithful once it parses.
2. **Validity is a threshold, not a ladder.** Weak models ~36–45%; capable models plateau
   ~66–70% (indistinguishable). The code-model "best host" peak was single-run noise.
3. **~Half the floor is spec-strictness, removable for free & safely.** A 15-line deterministic
   normalizer recovers 49% of failures (0 valid-but-wrong), lifting capable models to ~82–85%
   parse-valid — uniformly across capability (so it raises the whole curve, doesn't close the
   weak/capable gap; the residual gap is the "real" capability component).
4. **AXON's strict validity only matters for AXON's *own* use case.** For an LLM reader, even
   invalid AXON decodes at ~0.88 — validity is nearly irrelevant, and JSON would do as well.
   Validity is decisive **only** for the deterministic-parser pitch (machine-parse, no LLM) —
   which is exactly AXON's reason to exist. There, the free preprocessor is high-leverage.

### Residual failures (the unrepaired ~51%) — the floor has 3 layers, not 2

Categorising the 32 messages the normalizer does *not* fix:
- **multi-error surface slips** (a message with 2+ strictness errors; one repair fires but
  others remain) — fixable with more transforms;
- **genuine expressiveness gaps** — the model reaches for constructs AXON's grammar *lacks*:
  comparison/member-access in conditionals (`if(response.status == 200, store(...))`), units
  glued to identifiers (`CPU_exceeded_95%`), `key:val` as a bare call-arg, positional `$1`
  backrefs. These aren't strictness — AXON genuinely can't express them.

So the capability floor decomposes into **three** layers:
1. ~49% trivially-fixable surface strictness (the safe repairs),
2. multi-error surface slips (more transforms would catch these),
3. **genuine expressiveness gaps** — AXON's grammar is missing constructs models reach for
   (comparisons, member access, inline units on names). This last layer is an AXON *design*
   limitation, not a model failure, and is the part no preprocessor fixes.

## Phase D — Cross-reader decode sweep (firm "easy to read") — DONE

Decoded the same 114 AXON messages (run0+1) with four readers of differing capability:

| reader | n decoded | AXON fidelity |
|---|---|---|
| gemma4 (weak) | 44 / 114¹ | 0.985¹ |
| qwen3-30b (mid) | 113 | 0.945 |
| gpt-oss-120b (large) | 114 | 0.951 |
| qwen3-coder-80b (code) | 114 | 0.930 |

¹ gemma4-as-reader was time-boxed (heavy reasoner, ~21s/cell) and only finished 44/114 —
high fidelity on the subset it reached, but partial coverage, so inconclusive for the weak end.

Among the three readers that decoded the **full** set, **AXON fidelity is flat (0.93–0.95)
regardless of reader capability**. → the capability floor is **purely sender-side**: AXON is
hard to *write* (steep validity floor on the sender) but easy to *read* (any capable reader
recovers it, and even a deterministic parser would once it's valid). The sender-vs-reader
asymmetry — the §4.7 claim — is now firmed with a proper reader-capability curve (was 2 points).

## Phase G — Weak-end replication (gemma4/qwen35 → n=4) — RUNNING/NEXT (firm the threshold)

---

*(Running log; updated as each phase lands. Final summary at the end.)*
