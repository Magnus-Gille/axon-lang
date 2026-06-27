# In-context deterministic-DSL pilot — results

**Closes the one regime the cross-model debate (`debate/axon-falsification-pivot-*`) left open
for AXON:** model-visible / token-billed (in a prompt), **deterministic consumer** (no LLM
tolerance — invalid/unmapped input is *rejected*, unlike the LLM decoder in the M5 study), **no
compression layer** (you can't gzip a prompt). The counting-unit dilemma's "untested hole."

**Answer: the regime does NOT rescue AXON — and, more sharply, it doesn't reward a dense notation
at all. It rewards *schema-constrained emission* (structured outputs), a JSON-ecosystem technique
orthogonal to AXON.**

## View A — token × validity trade (best case for AXON; `incontext_cost.py`)

Granting *every* format the best case ("parsed ⇒ correct", optimistic geometric reject-retry),
capable senders (qwen3-30b / gpt-oss-120b / qwen3-coder-80b):

| format | det-parse % | eff. marginal tok/correct |
|---|---|---|
| **axon** | 69% | **44.9 — loses** |
| axon + deterministic repair | 84% | 36.9 — ~ties |
| **compact JSON** | 100% | **37.1** |
| json_schema | 100% | 52.7 |

**Even granted best case, raw AXON loses to compact JSON** — the ~31% deterministic-parse-failure-
retry cost outweighs the ~28% density saving. Repair only lets AXON *tie* JSON. The emission floor,
not density, dominates once the consumer is deterministic.

## View B — strict deterministic extraction (the real consumer; `det_fidelity.py`)

A *real* deterministic consumer extracts fields by **literal key/structure** — no LLM, no alias
tolerance (the alias-matching the M5 LLM decoder used is exactly what's unavailable here). Measured
fidelity collapses for **every free-form LLM-emitted format**:

| format | strict-deterministic fidelity | tokens | parse % |
|---|---|---|---|
| plain JSON | **0.267** | 37 | 100% |
| custom task-DSL | 0.514 | **22** | 100% |
| json_schema (envelope pins speech_act/sender/receiver/content) | **0.574** | 53 | 97% |

(M5's reported JSON fidelity was 0.94 — *all* of that gap is the LLM decoder's alias-matching.)

**The deterministic-consumer regime is hostile to all free-form LLM emission** — the model never
reliably hits the exact field vocabulary/structure a literal parser expects (vocabulary drift is
the same class of failure as AXON's syntax floor, just relocated). What *helps* is **pinning the
schema**: json_schema's envelope (0.57) already beats free JSON (0.27) precisely because it
constrains structure. The logical endpoint is **structured outputs / grammar-constrained decoding**
— forcing the emitter to the exact keys+types — which is a JSON technique, not a property of AXON.

## Verdict (for the paper)

In the in-context deterministic-parse regime — AXON's last plausible niche — AXON:
1. **loses to compact JSON** on effective marginal tokens even granted best-case extraction (View A);
2. has **no advantage** under real deterministic extraction, where the binding constraint is
   *constrained emission*, solved by JSON structured outputs, not by a dense notation (View B).

So the in-context hole the debate flagged **does not rescue AXON** — it closes cleanly. The
broader, more novel point the pilot surfaces: **dense agent notations target the wrong variable.**
The cost in agent comms is not message density (gzip/caching/binary handle that) and not, in the
deterministic regime, syntax — it is *getting an LLM to hit an exact machine-consumable schema*,
which structured outputs / constrained decoding solve directly. AXON is orthogonal to the real
bottleneck.

## Honesty notes / limits
- View A grants "parsed ⇒ correct" (generous to AXON); a strict AXON extractor (not built — the
  AST→fields mapping is task-specific) would only lower AXON further, so the View-A loss is
  conservative.
- View B's DSL (n=14, one model, one run) and AXON-strict are pilot-scale / unmeasured respectively.
  The DSL's emitter, like JSON's, was *not* given the field vocabulary (fair: all free-form); a
  vocabulary-pinned DSL ≈ a structured-output, which is the recommended winner anyway.
- **The clean confirmatory next step:** a **structured-outputs arm** — emit with the box's
  `response_format: json_schema` built from each task's fields (~100% valid AND schema-conformant
  by construction) → strict deterministic extraction should approach 1.0, directly demonstrating
  "constrained JSON emission wins the in-context deterministic regime." Not yet run.

## Files
`PLAN.md`, `incontext_cost.py` (View A), `dsl.py` + `run_dsl.py` (custom DSL arm),
`det_fidelity.py` (View B), `results/dsl.jsonl`.
