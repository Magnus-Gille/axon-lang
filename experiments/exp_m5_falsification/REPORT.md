# Does AXON earn its place? A falsification campaign on local open models

**Run:** overnight 2026-06-25 → 26, fully autonomous.
**Hardware:** M5 home inference box (`inference.gille.ai`), 5 open models, ~3B→120B.
**Frame:** kill-shot — try hard to show AXON adds nothing; if it survives, find the niche.

> **TL;DR.** A genuine attempt to kill AXON mostly succeeds — and locates exactly one
> defensible niche. Across **5 open models × 5 formats × 14 tasks (350 attempted cells,
> 338 decoded)**, on the **all-attempt** metric (a failed/empty/undecoded encode counted
> as fidelity 0) AXON ranks **last** (0.85 vs 0.91–0.94 for JSON / structured-English /
> FIPA) and is the **only** format with poor surface validity (**64%** parse-valid vs
> 97–100%). But that deficit is **emission reliability, not faithfulness**: AXON yields a
> usable message on only 63/70 attempts (vs 70/70 for JSON), and on the messages it *does*
> decode its fidelity is **0.94 — mid-pack**, indistinguishable from the incumbents
> (0.938–0.959). So AXON **fails as a general/default format** — not because what it
> conveys is wrong, but because weaker models too often can't write valid AXON at all. That
> failure is concentrated in **small and mid models**, where validity collapses to 43–64%:
> AXON does **not** help weak models — it *requires* a capable one. On the two **large**
> models (gpt-oss-120b, qwen3-coder-80b) AXON **earns its place** and sits on the
> fidelity-vs-tokens Pareto frontier: it matches the best incumbent's fidelity (0.95–0.96)
> at fewer tokens — on the code model it is *both* more faithful and **~40% cheaper** than
> the best incumbent (JSON+Schema); on gpt-oss-120b it is only **~4% cheaper than the best
> incumbent** (structured English) though ~34% cheaper than JSON+Schema. Its single best
> host is the **code-tuned** model (0.96 fidelity, 86% valid, best of all five formats). On
> a *tokens-per-correct-message* basis AXON is best overall (31.9), but it buys **no latency
> win** — reasoning models spend 3–5× more generation tokens "thinking" to emit valid AXON.
> **Net:** not a general-purpose payload format, but a real, narrow seam — terse machine-
> payloads between strong, structure-fluent (especially code-tuned) agents, where token cost
> matters more than the last few points of fidelity.

---

## 1. Why this experiment

The existing AXON experiments (Exp 0–5) all ran on **frontier** models and reached a
mixed, mostly negative verdict: AXON wins on raw token density (~15.4 tok/unit, ~32%
under JSON function-calling) and on cross-model consistency, but it **loses** on
judge-scored compositionality (66–67%, dead last behind every English baseline at
94–96%) and is **fragile** under noise (16% structural survival). The pre-registered
thesis — that AXON's *intrinsic* composition operators beat *extrinsic* structure —
was not supported once LLM judges scored the outputs.

Frontier models, however, are the wrong place to find AXON's value: they can parse and
compose anything, so they don't *need* a constrained notation. The interesting,
previously-untestable question is whether AXON helps (or collapses) when the model is
**weak, open, and local** — exactly what the M5 box now makes testable, across a model
size axis from a ~3B-active reasoner to a 120B model.

We deliberately framed this as a **falsification campaign**: the goal is to *disprove*
that AXON earns a place in agent-to-agent communication, and only concede a niche if
AXON survives a genuine attempt to kill it.

## 2. The honest competitive landscape (so we don't reinvent a worse wheel)

AXON lives at **Layer 3, the content/payload format** — the bytes inside a message,
not the transport. The stack around it is largely settled and AXON neither competes
with nor should duplicate it:

- **Transport / connection:** A2A (Google), MCP (Anthropic), ACP/ANP, NLIP — converged
  under the Linux Foundation's AAIF (Dec 2025). AXON would be the *content* of an A2A
  message `Part` (a `text/axon` MIME type), not a transport.
- **Discovery:** Agent Cards, `agents.json`.
- **Frameworks / orchestration:** LangGraph, CrewAI, AutoGen.
- **Content format (AXON's actual layer):** JSON (universal, every LLM trained on it),
  **TOON** (30–60% token savings on tabular data, *with real adoption*), YAML, Markdown.

The only defensible question is therefore narrow: **as a message payload format, does
AXON beat the incumbents (JSON, JSON+Schema, structured English, FIPA-ACL) on a metric
that matters — and in a regime where it isn't already served better by JSON or TOON?**

## 3. Method — round-trip fidelity, not vibes

Agent communication is encode → wire → decode. A dense format the receiver can't decode
is worthless; a verbose one that round-trips perfectly is fine. So we measure the loop:

1. **Encode** — an M5 model (Agent A) turns a natural-language intent into ONE message
   in the condition's format (format spec + 2 few-shot examples, equal scaffolding).
2. **Decode** — a single fixed model (Agent B, `qwen3-30b-instruct`) reads the message
   and recovers the canonical field tuple as JSON. The decoder is taught **every**
   format's structure and given the shared field schema, so it models a real receiving
   agent rather than a JSON-only parser. (This fixed a real confound found in smoke
   testing, where a naive decoder mistook AXON's `(@a>@b)` routing envelope for payload
   — the same class of artifact that flipped the earlier compositionality result.)
3. **Score** — recovered fields are machine-compared to ground truth
   (`scoring_lib.py`, self-tested). **No LLM judge in the main metric** — objective
   field matching, to avoid judge-generosity artifacts.

Per message we also record **validity** (does it parse? AXON via its reference parser),
**neutral_tokens** (tiktoken `cl100k_base`, a model-independent size unit),
**completion_tokens** and **latency** (the box's real cost).

**Headline composite:** `effective_tokens = mean_tokens / mean_fidelity` — the expected
wire-tokens per *fully correct* message. AXON's whole pitch is density; this checks
whether density survives contact with correctness.

**Conditions (5):** `axon`, `json` (naive), `json_schema` (envelope contract — the real
incumbent), `struct_english` (the Exp 3 surprise winner), `fipa_acl`.
**Models (5):** `qwen3-30b-instruct`, `gemma4`, `qwen3-coder-next-80b`, `gpt-oss-120b`,
`qwen35-a3b` (serial, one loaded at a time).
**Tasks (14):** composition-heavy, 3 levels — `tasks.json`.

### Pre-registered earn / kill criteria (decided before analysis)

- **AXON earns its place in a slice** iff `fidelity(axon) ≥ best_incumbent − 0.02` AND
  `tokens(axon) < tokens(that incumbent)` (Pareto-dominant or on the frontier).
- **Falsified overall** iff it earns its place in *no* slice (overall / per-level /
  per-model) and is Pareto-dominated overall.
- **Niche found** iff it earns its place in some but not all slices — report the region.

## 4. Results

**Dataset:** 350 encoded cells (5 models × 5 conditions × 14 tasks, single run; 341 ok),
338 decoded. `gemma4` and `qwen35-a3b` are heavy reasoners whose first-pass cells were
budget-truncated and re-run at 6k/8k token budgets; `qwen35-a3b` still failed 8 cells
(timeout at 8k — it is pathologically verbose). Full tables in `results/summary.md`.

### 4.1 Overall — AXON is last *end-to-end*, but faithful once it decodes

**All-attempt** denominator (350 attempts; a failed/empty/undecoded encode = fidelity 0;
`ntok` is the attempt-mean). This is the headline metric — it charges AXON for messages it
*fails to emit*, which is a real end-to-end cost:

| condition | surf. valid% | fidelity (all-attempt) | neutral tok | eff. tok (tok/correct) |
|---|---|---|---|---|
| **axon** | **64%** | **0.848** (last) | **27.0** (lowest) | **31.9** (best) |
| json | 100% | 0.938 | 37.6 | 40.1 |
| json_schema | 97% | 0.932 | 50.6 | 54.3 |
| struct_english | n/a¹ | 0.928 | 35.9 | 38.7 |
| fipa_acl | 97% | 0.915 | 42.7 | 46.6 |

¹ *Surface validity is **format-specific**, so it is not apples-to-apples across conditions:
AXON via its reference parser; `json` via `json.loads`; `json_schema` via the envelope
contract (speech_act ∈ allowed set, sender/receiver/content present); `fipa_acl` via
performative + balanced parens + `:sender`/`:receiver`/`:content` slots; `struct_english`
has no parser, so it is N/A (valid by construction) and excluded from the validity
comparison. Re-validating the corpus with these stricter envelope/slot checks gives the
**same** percentages as the original lenient ones — the 64-vs-97 gap is robust (see §4.4).*

**Decoded-only** sensitivity (restrict to the messages Agent B actually recovered — excludes
emission failures instead of imputing 0):

| condition | decoded n | fidelity (decoded-only) | emitted tok |
|---|---|---|---|
| **axon** | 63 | **0.942** (mid-pack) | 30.0 |
| json | 70 | 0.938 | 37.6 |
| json_schema | 68 | 0.959 | 52.1 |
| struct_english | 69 | 0.941 | 36.5 |
| fipa_acl | 68 | 0.942 | 43.9 |

The two tables are the whole story. **AXON's correctness problem is emission reliability, not
faithfulness:** it only produces a usable message on 63/70 attempts (vs 70/70 for JSON), and
*when it decodes* its fidelity (0.942) is statistically indistinguishable from the field
(0.938–0.959, mid of five). The all-attempt headline (0.848, last) is driven almost entirely
by those 7 emission failures being scored as zero. On **density** AXON is decisively best
(27 tok), and because the density gap (~30–47%) dwarfs the *decoded* fidelity gap (~2%), AXON
also wins **effective tokens** (31.9) — the fewest wire-tokens per *fully correct* message.
Which denominator you privilege is the argument: end-to-end success (all-attempt) penalises
AXON's brittle emission; cost-per-correct-unit rehabilitates it. AXON is on the Pareto frontier
(with `json` and `struct_english`).

### 4.2 The size axis — AXON needs a strong model (opposite of the weak-model hypothesis)

AXON's fidelity and validity climb steeply with model capability, while the incumbents
are roughly flat across the size axis:

| model (size) | AXON fid | AXON valid% | best incumbent | AXON earns? |
|---|---|---|---|---|
| qwen35-a3b (~3B, small) | 0.685 | 57% | json 0.948 | no |
| gemma4 (mid) | 0.733 | 43% | fipa 0.963 | no |
| qwen3-30b (mid) | 0.914 | 64% | json_schema 0.954 | no |
| gpt-oss-120b (large) | 0.947 | 71% | struct_eng 0.964 | **YES** |
| qwen3-coder-80b (code) | **0.960** | 86% | json_schema 0.954 | **YES** |

> ⚠ **These are single-run numbers; the validity column does not replicate.** With n=4 runs
> (§4.9) the three capable models are statistically tied (~66–70% validity) and the
> "86%" code-model peak is noise. Read the *fidelity* column (robust) and treat the per-model
> *validity* figures as indicative only — the firmed structure is a weak→capable **threshold**,
> not a smooth ladder.

This is the headline. The intuition that a constrained notation would *scaffold* weak
models is **falsified**: on the small/mid models AXON's validity collapses to 43–64% and
its fidelity trails the incumbents by 0.04–0.23. AXON has a steep **capability floor** —
it only becomes competitive once the model is fluent enough to emit it correctly. The
incumbents (JSON especially, 100% valid and ~0.90–0.95 fidelity *everywhere*) carry no
such floor.

The two models where AXON **earns its place** are both large; the **code-tuned** model is
its best host of all (0.96 fidelity — highest of *any* format on that model — 86% valid,
30.5 tok vs JSON+Schema's 51.2). Code models are trained on dense structured syntax, so
AXON sits closest to their distribution.

The token saving is **larger on the code model than on gpt-oss-120b**, and how big it is
depends on which incumbent you compare against:

- **qwen3-coder-80b:** AXON (0.960, 30.5 tok) beats the best incumbent (json_schema 0.954,
  51.2 tok) on *both* axes — more faithful **and ~40% fewer tokens**. Unambiguous win.
- **gpt-oss-120b:** the best-fidelity incumbent is structured English (0.964, 32.9 tok);
  AXON (0.947, 31.6 tok) is ~0.02 less faithful and only **~4% cheaper** than it. AXON is
  ~34% cheaper than *JSON+Schema* on this model, but JSON+Schema is not the best incumbent
  here. So "~40% fewer tokens" is a clean claim only on the code model and only vs
  JSON+Schema; on gpt-oss-120b the honest figure vs the best incumbent is single-digit.

### 4.3 Density buys no speed on reasoning models

AXON's fewer *output* tokens do **not** translate to lower latency on reasoning models —
they translate to *more* of them. Completion-token cost to produce one AXON message:
gemma4 **2,374**, qwen35-a3b **3,310**, gpt-oss-120b 342 — versus ~200–600 for English/
JSON on the same models. The models "think harder" to get AXON's grammar right. Only on
the non-reasoning models (qwen3-30b 0.9s, coder) is AXON's latency in line with the rest.
The "compact = cheap/fast" pitch holds **only** for non-reasoning, structure-fluent models.

### 4.4 Validity failure mode

AXON's invalids are genuine grammar violations, not harness artifacts (verified): unquoted
times (`02:00..04:00`), units inside identifiers (`CPU_exceeded_95%`), wrong list syntax
(`@w1, @w2` instead of `[@w1,@w2]`), keyless records (`{60s}`). They cluster on **L2/L3
composition tasks** (validity L1 90% → L3 50%) — i.e. exactly where AXON's operators were
supposed to be the advantage, the model most often emits invalid AXON. JSON/English never
hit these walls.

**On metric fairness.** "Surface validity" is **format-specific** and the conditions are not
equally strict by nature, so the "64% vs 97–100%" gap must be read with that in mind. To keep
the incumbents from getting a free pass, we validate each as strictly as its format admits
(`validators.py`, self-tested): AXON via the reference parser, `json_schema` via the *envelope
contract* (not just `json.loads`), `fipa_acl` via *performative + slot* presence (not just
paren-balance), `struct_english` marked **N/A** (prose has no parser) rather than 100%.
Re-validating the committed corpus with these stricter checks reproduces the **same**
percentages — every parse-OK `json_schema`/`fipa` message already satisfied its contract — so
the gap reflects AXON's real fragility, not a lenient yardstick for the baselines.

### 4.5 Frontier calibration — the scorer is trustworthy and fair to AXON

A frontier judge (`claude -p`) independently scored 50 stratified cells. Machine fidelity
agrees strongly with the judge's recovered-faithfulness score: **Pearson r = 0.875, MAE =
0.050**, with a small uniform bias (+0.044 — the machine is marginally *more* generous).
Crucially, agreement is **as good for AXON (MAE 0.034)** as for the incumbents (json 0.030,
struct_english 0.031; json_schema 0.068, fipa 0.089) — the scorer is **not** biased against
AXON, so the kill is fair (this is the exact check the prior Exp 3 lacked, where the result
was a judge-generosity artifact). Separating encoder from decoder: the judge rates the
message itself at 0.926 but the recovered tuple at 0.892 — a **decoder loss of only 0.035**,
confirming the fidelity differences are driven by the **format (encoding)**, not by decoder
weakness.

### 4.6 Does fixing validity rescue AXON? (constrained-decoding follow-up)

The box honors `response_format: json_schema` but **ignores grammar-constraint params**
(`guided_grammar`/`guided_choice`/`guided_json`), so AXON can't be EBNF-constrained here.
We proxy it two ways: a **valid-only re-slice** of the existing data, and a real
**retry-until-valid** run (resample ≤3×, keep first valid) on 4 models.

- **Valid-only (biased, optimistic):** among messages that already parse, AXON fidelity is
  0.96 overall — tied with the best incumbent — at ~half the tokens; even weak gemma4's
  valid AXON scores 1.00. Suggests validity is the whole problem.
- **Retry-until-valid (de-biased):** forcing the hard cells to parse tells a subtler story
  (pooled, 4 models):

  | | valid% | fidelity | wire tok | eff. wire tok |
  |---|---|---|---|---|
  | AXON baseline | 66% | 0.889 | 29.3 | 32.9 |
  | AXON retry-until-valid | 79% | 0.905 | 30.3 | 33.4 |
  | json_schema (incumbent) | 98% | 0.940 | 51.8 | 55.1 |

  The effect **splits by model**:
  - **gemma4 (weak) — rescued:** fidelity 0.73 → **0.95** (now *above* json_schema 0.947) at
    half the tokens. Its failures were pure syntax.
  - **gpt-oss-120b (large) — hurt:** fidelity 0.95 → **0.81** — forcing previously-invalid
    *complex* cells to parse produced **valid-but-wrong** messages. Validity ≠ correctness.
  - qwen3-30b / coder: roughly flat.

**Takeaway.** The capability floor is *mostly* a **syntax-production floor** (constrained
decoding fixes it — biggest win for weak models, and ~40% fewer wire tokens persists
throughout) but *partly* a genuine **semantic-expressiveness limit on composition** that no
validity-forcing repairs — and may even *mask* (valid-but-wrong). Retry never reached 100%
valid and ~doubled generation cost; true single-pass constrained decoding would avoid that
penalty but not the valid-but-wrong failure on complex payloads. Net: constrained decoding
is a **real but partial** rescue, strongest for weak models — pair it with payload
validation on compositional messages.

### 4.7 The floor is on the writer, not the reader

Re-decoding the same AXON / JSON+Schema messages with readers of different strength:

| reader | AXON fidelity | JSON+Schema fidelity |
|---|---|---|
| mid (qwen3-30b) | 0.942 | 0.959 |
| strong (qwen3-coder-80b) | 0.918 | 0.965 |

Among capable readers, AXON is recovered **as robustly as JSON** — flat across reader
strength. So AXON's capability requirement is **asymmetric**: hard to *write* (needs a
capable sender, §4.2) but easy to *read* (a mid model recovers it fine). Practical upshot:
in a mixed fleet, put AXON *generation* on your strong/code-tuned models; the *consumer* can
be modest — or, ideally, a deterministic parser (AXON's actual intended reader, not exercised
here). The truly-weak reader (qwen35-a3b) test was **inconclusive** — the box returned
HTTP 530 on 118/131 of its calls (an infra/model-load failure, equal on JSON and AXON), so
it carries no signal.

### 4.8 Statistical firming

- Per-condition **all-attempt** fidelity, 95% bootstrap CI: AXON **0.848 [0.775, 0.911]**,
  json **0.938 [0.913, 0.961]**, json_schema **0.932 [0.887, 0.970]**, struct_english **0.928
  [0.890, 0.959]**, fipa **0.915 [0.864, 0.955]**. AXON's CI is **disjoint only from JSON**;
  it **overlaps** json_schema, struct_english, and fipa. So the defensible statistical claim is
  "AXON is clearly below JSON and has the lowest point estimate," **not** "significantly lowest
  vs every incumbent." (And recall §4.1: this all-attempt CI is depressed by AXON's emission
  failures; the decoded-only fidelity gap is ~0.02.)
- Capability floor as a rank effect (n=5 models, ad-hoc capability ordering — **exploratory
  monotone evidence, not a settled effect**): **Spearman(capability, AXON fidelity) = +1.00**
  (a genuine monotone climb, no ties) and **+0.90 for AXON validity**, vs **+0.20 for JSON
  fidelity**. JSON validity is constant (100% across all 5 models), so its rank correlation is
  **undefined** — the tie-correct helper now reports that rather than the spurious +1.00 a
  plain argsort produced. AXON tracks capability steeply; the incumbents are flat-to-undefined.
- Paired over 70 model×task cells, AXON **ties** JSON+Schema on 45, **loses** 16, **wins** 9
  (mean −0.084): AXON matches the incumbent on most cells and is dragged down by a minority
  of hard failures.

### 4.9 Replication & robustness firming (multi-run + repair)

A follow-up campaign added **2–4 runs per cell** on the headline models (3 models × 4 runs;
gemma4 × 2–4; qwen35-a3b partial) plus a cross-reader sweep and a deterministic-repair probe
(`replication_stats.py`, `axon_repair.py`, `OVERNIGHT_FINDINGS.md`). It **strengthens the core
thesis but corrects two single-run claims**:

- **The capability floor is a *syntactic-emission* floor, not a semantic one.** Decoded-only
  fidelity is flat and high across *every* model (0.91–0.98, run-to-run SD ≈ 0). AXON is
  recovered faithfully *once it parses*; **all** capability dependence lives in **validity**.
- **Validity is a *threshold*, not a smooth ladder — and there is no code-model peak.** With
  n=4, the three capable models are statistically indistinguishable (qwen3-30b 66±8, gpt-oss
  70±8, qwen3-coder 68±11); the weak models sit far below (gemma4 36±7, qwen35 45±12). **The
  §4.2 single-run "code model 86% valid, best host" was noise** — the corrected picture is a
  weak-vs-capable step (~40% → ~68% plateau), not a monotonic climb.
- **The floor is purely sender-side (firmed).** Decoding the same AXON messages with readers of
  differing capability gives flat fidelity (qwen3-30b 0.945, gpt-oss 0.951, qwen3-coder 0.930):
  hard to *write*, easy to *read*.
- **~Half the floor is removable for free, safely.** A 15-line deterministic, meaning-preserving
  normalizer (quote bare times, tag bare records, bracket multi-receiver routing) makes **49%**
  of invalid AXON parse — recovery is **uniform across capability** and produces **0 valid-but-
  wrong** (the repaired messages decode at the same fidelity). Effective parse-validity rises
  +13–21 pts (capable models → 82–85%). The residual decomposes into multi-error surface slips
  and **genuine expressiveness gaps** (comparisons / member-access in conditionals,
  units-glued-to-identifiers) that AXON's grammar cannot express — an AXON *design* limit, not
  a model failure.
- **Practical upshot:** AXON's strict validity matters **only for its own deterministic-parse
  pitch** (machine-parse, no LLM). For an LLM reader, even *invalid* AXON decodes at ~0.88, so
  validity is nearly irrelevant and JSON would serve as well. Where the no-LLM-parse pitch is
  the point, the free preprocessor is the highest-leverage fix on the validity axis.

## 5. Verdict (against the pre-registered criteria)

- **Falsified overall (per the pre-registered criterion): NO — but it fails as a
  general/default format.** The pre-reg defines "falsified overall" as earning its place in
  *no* slice **and** being Pareto-dominated overall. Neither holds: AXON earns 2 model slices
  (below) and sits on the overall fidelity-vs-tokens Pareto frontier. What *is* true — and what
  the earlier drafts conflated with "falsified overall" — is that AXON **fails the OVERALL
  aggregate slice and every task-Level slice** (its all-attempt fidelity gap to the best
  incumbent, 0.07–0.12, far exceeds the 0.02 tolerance). So: AXON does **not** earn the
  general/default payload slot, but it is **not falsified** in the strict pre-registered sense.
  The driver is parseability/emission (§4.1, §4.4), not faithfulness once decoded.
- **Niche found: YES — and precisely located.** AXON earns its place on 2 of 5 models, both
  large/structure-fluent (gpt-oss-120b, qwen3-coder-80b), where it matches the best incumbent's
  fidelity at fewer tokens (~40% on the code model vs JSON+Schema; single-digit vs the best
  incumbent on gpt-oss-120b — §4.2). It fails on all small/mid models.
- **Direction vs prior work:** consistent. Frontier Exp 3 found AXON last on composition;
  here AXON is again last on the all-attempt headline and worst on composition validity
  (though mid-pack on fidelity once decoded — §4.1). The new contribution is the
  *capability-floor* result and the *code-model* niche — neither visible when every model
  is frontier-grade.

## 6. Where — if anywhere — AXON could earn its place

Given the honest landscape (§2), AXON should **not** chase the general payload slot: JSON
owns it (universal, 100%-valid, training-ubiquitous), and TOON already owns token-efficient
*tabular* payloads with real adoption. The seam this experiment actually supports is
narrow but real:

> **Terse machine-to-machine payloads between strong, structure-fluent agents — especially
> code-tuned models — in token-metered or bandwidth-constrained settings, where ~40% fewer
> tokens is worth a few points of fidelity and both ends are known to be capable.**

Conditions for that seam to pay off, all evidenced above: (1) both agents are large/
code-tuned (capability floor); (2) cost is dominated by *payload* tokens, not generation
*reasoning* tokens (else the thinking overhead erases the saving); (3) ideally paired with
**grammar-constrained decoding** (unavailable on this box) to lift validity from 64% toward
100% by construction — the single highest-leverage fix, since validity, not expressiveness,
is AXON's binding constraint. Absent constrained decoding, AXON does not earn a general
place; with it, the contest moves toward tokens-per-correct-message, where AXON leads on
cost (~40% fewer wire tokens). But the follow-up (§4.6) shows the rescue is **partial, not
clean**: forcing validity helps *weak* models a lot (gemma4 0.73→0.95) yet can *hurt* strong
ones by turning honest parse-failures into valid-but-wrong messages on complex payloads. So
the realistic niche is narrower still: **constrained-decoded AXON between strong/code-tuned
agents for mostly-flat (non-deeply-compositional) payloads, with payload validation kept on
the complex ones.** Venues for writing this up are scouted in `VENUES.md` (arXiv now;
workshop targets MOSS@COLM, REALM@EMNLP, Negative-Results@EMNLP — several deadlines in the
next 1–3 weeks).

## 7. Limitations & honesty notes

- One fixed decoder model; cross-model decode not swept (a heterogeneous-agent
  extension). Constrained decoding is unavailable via the box's chat API — noted as a
  steelman caveat (it would push every structured format toward 100% validity,
  concentrating the contest on fidelity + tokens, which we measure directly).
- `qwen35-a3b` and `gemma4` are heavy reasoners; early cells were budget-truncated and
  re-run with larger budgets (the truncations were a harness artifact, not a format
  failure — see §4).
- Replication: the *original* headline tables (§4.1–4.2) are single-run. A follow-up added
  **2–4 runs** on the headline models and 2 runs on gemma4 (§4.9): decoded **fidelity is
  stable** (run-to-run SD ≈ 0), but **per-model validity is noisier** than one run implied —
  hence the §4.2 validity column is corrected to a threshold (not a ladder) in §4.9.
  qwen35-a3b remains under-sampled (pathologically verbose; partial 2nd run).

## 8. Reproduce

See `README.md`. `bash run_all.sh`, then `python analyze.py`.
