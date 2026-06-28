# Public function-calling benchmark — selection & adaptation plan

*From a 9-agent survey of 20 benchmark entries (BFCL, ToolBench/ToolLLM, τ-bench/τ²-bench, API-Bank,
Nexus, xLAM/ToolACE/APIGen, Seal-Tools, ComplexFuncBench, NESTFUL, MTU-Bench, T-Eval, HammerBench,
Chinese/multilingual). Goal: a REAL benchmark to externally-validate the thesaurus-alignment finding
beyond our 42 self-generated tasks — needs per-argument gold (right value in right slot) + role-
confusion/ambiguity potential + local-runnable + clean format.*

## Verdict
**No public benchmark is purpose-built for our exact thesis** (curated ambiguous-name pairs labeled
for intra-call misrouting). Two fit well and are complementary:

1. **BFCL — Berkeley Function Calling Leaderboard (Gorilla / UC Berkeley) — TOP PICK.**
   Native deterministic per-argument scoring, cleanest format, fully local, no LLM judge, large N.
2. **ComplexFuncBench (zai-org) — complement.** Weaker turnkey scoring, but the richest *real,
   confusable* named-argument traps (`fromId`/`toId`, `departDate`/`returnDate`, `checkIn`/`checkOut`).

BFCL first (decision-ready, low scorer risk, runnable today); cross-validate the thesaurus effect on
ComplexFuncBench's travel traps for genuinely confusable real-world names.

## BFCL adaptation plan
- **Source:** `pip install bfcl-eval`; data HF `gorilla-llm/Berkeley-Function-Calling-Leaderboard` /
  GitHub `ShishirPatil/gorilla/berkeley-function-call-leaderboard/`. **Apache 2.0, ~12 MB, JSONL.**
  Deterministic AST evaluator (no frontier dependency).
- **Categories:** non-live **Multiple** (200) + **Parallel Multiple** (200) as the core role-confusion
  surface; add **Live Multiple** (1,037) for realistic field names (`recipient`/`content`/`from`/`to`/
  `source`/`destination`). Skip executable/live-exec (need RapidAPI keys) and V3 multi-turn (outcome-only).
- **Gold → our metric:** each `possible_answer` is `{id, ground_truth:[{fn:{arg:[accepted_values]}}]}`.
  Per-argument fidelity = predicted arg value ∈ accepted list. **Derived "misrouted-value rate"** = a
  gold value belonging to arg A appearing under a *different* arg B (intra-call) or under the *wrong
  parallel call* = "right value, wrong slot" — exactly our role-confusion signal (~30 lines on the
  parsed AST; BFCL doesn't surface it but its structure makes it trivial).
- **Enrich for ambiguity (caveat fix):** BFCL isn't curated for confusable names, so density is
  uneven. Pre-filter to cases where (a) two args in one call share a type, or (b) parallel/candidate
  functions share an argument name with differing semantics — concentrates the signal before spending inference.
- **Conditions (same gold + scorer):** **Bare** = schema with names+types only, descriptions stripped.
  **Thesaurus** = inject a per-argument semantics gloss ("this field means X; don't confuse with Y") +
  disambiguated names where allowed. Measure Δ per-argument fidelity and Δ misrouted-value rate.
- **Smallest first slice:** 50 Parallel Multiple on one warm local model (M5 `qwen3-coder-next-80b`,
  or `mellum` for a fast pilot) to validate the misrouting scorer end-to-end → then full 400 non-live + 1,037 Live Multiple.

## Honest compromise
Neither benchmark *labels* intra-call misrouting natively — we derive it. BFCL's ambiguous-name
density is uncurated (mitigated by filtering). ComplexFuncBench has the real confusable names but
needs a custom per-arg scorer (its annotation stripped some cross-call response ambiguity; the static
`fromId`/`toId`-type traps remain). **Plan: BFCL first; cross-validate on ComplexFuncBench travel traps.**

*Other entries surveyed but lower-fit: ToolBench/τ-bench (trajectory/outcome scoring, not per-arg);
API-Bank/Nexus (smaller/format); xLAM/ToolACE/APIGen (mostly training data); MTU-Bench/T-Eval
(aggregators); HammerBench (mobile, some confusable args — possible tertiary). Full table in the
workflow result / Munin.*
