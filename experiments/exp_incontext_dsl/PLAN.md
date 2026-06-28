# In-context deterministic-DSL pilot

**Why:** the cross-model debate (`debate/axon-falsification-pivot-*`) upheld the falsification
pivot but flagged one untested hole in the "counting-unit dilemma": the **in-context
deterministic-parse** regime — a message that is model-visible / **token-billed** (sits in a
prompt), parsed by a **deterministic consumer** (no LLM tolerance; invalid input is *rejected*,
unlike the LLM decoder in the M5 study), with **no compression layer** (you can't gzip a prompt).
There AXON's raw density is a real saving, but its emission floor becomes a hard cost. This pilot
tests whether AXON survives there before any universal-sounding paper is drafted.

**Question:** when the message is model-visible, token-billed, uncompressed, and deterministically
parsed, does AXON beat compact JSON / structured outputs / a custom task-DSL at matched semantic
fidelity *and* live reject-retry cost?

## Metric

Effective marginal tokens per correctly-delivered message, under a deterministic consumer with
reject-and-retry:

    effective_marginal_tokens = mean_tokens / (deterministic_parse_rate × deterministic_fidelity)

- `deterministic_parse_rate` = the M5 `valid` field (AXON reference grammar / JSON `json.loads` /
  json_schema envelope / DSL parser).
- Geometric retry: expected attempts to land one parseable message = 1/parse_rate.
- Tokens are **marginal & uncompressed** (the in-context regime; not stream-gzip, not cached).

## Arms

| arm | status | source |
|---|---|---|
| AXON v0.1 | done | M5 corpus |
| AXON + deterministic repair (`axon_repair`) | done | M5 corpus |
| compact JSON | done | M5 corpus (`json` condition) |
| JSON+Schema envelope | done | M5 corpus |
| **custom task-DSL** | TODO | new emissions (this dir: `dsl.py`) |
| JSON structured-outputs (~100% valid) | optional | new emissions (box `response_format`) |
| TOON | out-of-scope | tasks are composition-heavy, not tabular (TOON owns tabular) |

## Senders
Capable local models (qwen3-30b, gpt-oss-120b, qwen3-coder-80b). Optional frontier sender via
`claude -p` (the M5 study lacked a frontier sender — a noted limitation).

## Result so far (box-free core, `incontext_cost.py`) — AXON loses, best case

Granting AXON the **best case** (parsed ⇒ correct; optimistic independent retries), capable senders:

| format | det-parse% | eff tok/correct |
|---|---|---|
| axon | 69% | **44.9 (loses)** |
| axon+repair | 84% | 36.9 (~ties) |
| compact JSON | 100% | **37.1** |
| json_schema | 100% | 52.7 |

**Raw AXON loses to compact JSON even in its best-case regime** — the ~31% deterministic-parse-
failure-retry cost outweighs the ~28% density saving. AXON+repair only *ties* JSON. This is
conservative for AXON: a real deterministic field-extractor (instead of "parsed⇒correct") can only
lower AXON further. → the in-context regime does **not** rescue AXON; closes the debate's open hole.

## Remaining (to fully satisfy the debate)
1. **Custom task-DSL arm** (`dsl.py`) — collect LLM emissions, score validity + effective cost.
   Expectation: a specialized format emits more reliably + compactly than general AXON (the
   "specialized beats general" point). This is near-tautological but completes the comparison.
2. (Optional) real deterministic AXON field-extractor to replace the parsed⇒correct grant.
3. (Optional) structured-outputs arm (box `response_format: json_schema`, ~100% valid).
