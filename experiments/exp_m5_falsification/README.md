# Exp M5 — AXON Falsification Campaign on Local Open Models

**Date:** 2026-06-25 (overnight autonomous run)
**Hardware:** M5 home inference box (`inference.gille.ai`), OpenAI-compatible API.
**Frame:** *Kill-shot.* Try as hard as possible to show AXON does **not** earn its
place in agent-to-agent communication. If it survives anywhere, pin down the
exact niche.

This is a deliberately adversarial complement to the existing frontier-model
experiments (Exp 0–5), which already found AXON wins on token density but loses
on judge-scored compositionality and noise robustness. The M5 unlocks the one
regime those couldn't test: **weak, open, local models**, across a size axis from
~3B-active to 120B.

## Null hypothesis (to attack)

> For every task type, model size, and metric that matters in agent-to-agent
> messaging, an established incumbent (JSON, JSON+Schema, structured English, or
> FIPA-ACL) does at least as well as AXON. Therefore AXON adds nothing.

To *falsify AXON* is to fail to reject this null. To find AXON's *niche* is to
exhibit a (task × model × metric) slice where AXON **strictly dominates** the
best incumbent.

## The metric that matters: round-trip fidelity

Agent-to-agent communication is encode → wire → decode. A dense format that the
receiver cannot reliably decode is worthless; a verbose format that round-trips
perfectly is fine. So we measure the full loop:

1. **Encode** — Agent A (an M5 model) is given a natural-language intent and a
   format spec, and emits ONE message in the condition format.
2. **Decode** — a single fixed Agent B (an M5 model) reads the message and
   recovers the canonical field tuple as JSON. The decoder is given the same
   structural knowledge of all formats and the shared field schema, so it models
   a real receiving agent — not a naive parser that only understands JSON.
3. **Score** — recovered fields are machine-compared to ground truth
   (`scoring_lib.py`), giving fidelity ∈ [0,1] per message. **No LLM judge** —
   objective field matching, to avoid the judge-generosity artifact that flipped
   the earlier compositionality result.

We also record, per message:
- **validity** — does it parse as its format? (AXON via the reference parser,
  JSON via `json.loads`, FIPA via paren-balance, English trivially.)
- **neutral_tokens** — tiktoken `cl100k_base` count of the message (a
  model-independent unit for fair cross-condition token comparison).
- **completion_tokens / latency** — the M5's own cost (wall-clock value that
  only a real local box reveals).

**Headline composite:** `effective_tokens = mean_tokens / mean_fidelity` — the
expected wire-tokens per *fully-correct* message. This folds density and
correctness into one number. AXON's whole pitch is density; this checks whether
the density survives contact with correctness.

## Conditions (5)

| id | what | role |
|----|------|------|
| `axon` | AXON notation | the subject under test |
| `json` | minified JSON, descriptive keys, no schema | naive incumbent |
| `json_schema` | JSON with an envelope contract (speech_act/sender/receiver/content, typed units) | the **real** incumbent AXON must beat |
| `struct_english` | explicit structured English | the surprise winner of Exp 3 |
| `fipa_acl` | FIPA-ACL speech-act messages | the legacy semantic-protocol incumbent |

All conditions get **equal scaffolding**: a concise format description + exactly
2 few-shot examples that do not overlap the test tasks (see `FAIRNESS.md`).

## Models (size axis, full spread)

`qwen3-30b-instruct` (mid, also the fixed decoder), `gemma4` (mid),
`qwen3-coder-next-80b` (large, code-oriented), `gpt-oss-120b` (large, reasoning),
`qwen35-a3b` (small ~3B-active, reasoning). Runs serial, one model loaded at a
time (the box cold-swaps between models).

## Tasks (14, composition-heavy)

`tasks.json` — agent-to-agent intents with machine-checkable ground truth, spread
over 3 levels: L1 atomic (query, inform-metrics, action+args, error), L2 composed
(sequence, parallel, conditional, causal, fan-out, proposal), L3 complex (nested
delegation, subscribe+filter, mixed plan/conditional, negotiation-counter).
Composition (sequence/parallel/conditional/causal) is over-represented on purpose
— it is exactly where AXON's operators claim an edge and where it previously
failed.

## Pre-registered kill / earn criteria

Decided **before** seeing full results:

- **AXON earns its place in a slice** iff `fidelity(axon) ≥ best_incumbent_fidelity
  − 0.02` **and** `neutral_tokens(axon) < tokens of that incumbent` (i.e. AXON is
  at least as correct while strictly cheaper — Pareto-dominant or on the
  frontier).
- **AXON is falsified overall** iff in no slice (overall, per-level, per-model) does
  it earn its place by the above rule, **and** it is Pareto-dominated by an
  incumbent on the overall fidelity-vs-tokens frontier.
- **Niche found** iff it earns its place in some but not all slices — report the
  precise (level × model-size) region.

Reported regardless of direction. A clean null is a result.

## Fairness measures (steelman AXON)

- Decoder is taught **all** formats' structure (so it isn't a JSON-only parser
  that structurally fails on AXON/FIPA — the bug we caught and fixed in smoke
  testing, where the decoder mistook AXON's routing envelope for payload).
- Decoder gets the shared **field-semantic schema** (so self-describing JSON keys
  don't get a free pass that positional formats are denied).
- Validity is checked with AXON's own reference parser.
- Token efficiency measured in a neutral tokenizer, not any model's own.
- Constrained decoding is **not** available via the box's chat API; we note this
  as a steelman caveat (it would lift every structured format's validity toward
  100%, neutralizing validity as a differentiator and concentrating the contest
  on fidelity + tokens — which is what we measure directly).

## Layout

```
m5_client.py     OpenAI-compat client (auth from file, retries, cold-swap aware)
tasks.json       intent corpus + ground-truth field tuples
conditions.py    encoder prompts per condition + uniform decoder prompt
scoring_lib.py   field-level fidelity scoring (+ self-test: --selftest)
run_encode.py    encode pass (one model per call, resumable)
run_decode.py    decode pass (fixed decoder, resumable)
analyze.py       join + score + aggregate + Pareto + verdict -> results/summary.md
run_all.sh       orchestrator: encode-all -> decode -> analyze, checkpointed
results/         encode.jsonl, decode.jsonl, summary.md, summary.json
```

## How to run

```bash
# auth: a file containing "Bearer <token>" for inference.gille.ai
export M5_AUTH_FILE=/path/to/.m5auth
bash run_all.sh
python analyze.py            # re-aggregate at any time (safe on partial data)
```
