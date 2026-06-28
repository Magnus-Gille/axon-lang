# AXON Project Status

**Last session:** 2026-06-28 (autonomous — semantic-reliability research)
**Branch:** axon-m5-replication (PRs #2 merged, #3 open)

## ⚡ CURRENT DIRECTION (read first) — semantic-channel alignment, NOT notation

The project pivoted twice and must not steer back. (1) The original *intrinsic-compositionality*
thesis was **unsupported**. (2) AXON-as-a-dense-notation was **falsified** (M5 study + use-case
panel + wire economics). (3) The live thread is now **reliable *semantic* agent communication**:
`experiments/exp_semantic_reliability/REPORT.md` is authoritative.

**Finding:** the real bottleneck is a sender↔receiver **thesaurus mismatch** (semantic-role
confusion from ambiguous field *names*) — afflicts every model (bare 0.34 mid / 0.51 capable / 0.81
frontier on ambiguous schemas). **Fix = thesaurus alignment, 3 equivalent forms → ~1.000:**
unambiguous field names (free) · thesaurus in the emitter prompt · independent+capable verifier+ARQ.
Externally validated on 28 fresh tasks / 5 domains. **Retired (don't reopen):** "make AXON better",
"density wins", "intrinsic>extrinsic", "self-consistency/self-verify catches errors". **Next (decided
this session):** external validity on a REAL benchmark = **BFCL** (Berkeley Function Calling
Leaderboard — Apache-2.0, local, deterministic per-arg scoring; derive "misrouted-value rate" =
role-confusion), bare vs thesaurus; cross-validate on ComplexFuncBench travel traps. Plan in
`experiments/exp_semantic_reliability/benchmark-plan.md`. (VoI-gated ARQ + multi-hop already done.)

Two writeups: AXON negative-result (`exp_m5_falsification/REPORT.md`) + semantic-reliability
(`exp_semantic_reliability/REPORT.md`) — a two-part story.

---

## Session 2026-06-26 — M5 Falsification Campaign (local open models)

New experiment: `experiments/exp_m5_falsification/` — full report in `REPORT.md`.
First AXON evaluation on **local open models** (M5 box, `inference.gille.ai`), framed as a
kill-shot. Metric: **round-trip fidelity** (Agent A encodes intent → fixed Agent B decodes
→ machine-scored vs ground truth), plus validity, neutral tokens, latency. 5 models
(~3B→120B) × 5 conditions (axon, json, json_schema, struct_english, fipa_acl) × 14
composition-heavy tasks = 350 cells, 338 decoded. Scorer validated against a frontier judge
(Pearson r=0.875, MAE=0.050; fair to AXON, MAE 0.034).

**Verdict: AXON fails as a general/default format, but earns a narrow niche** (NOT
"falsified overall" per the pre-reg — it earns slices + is on the Pareto frontier).
- On the **all-attempt** metric AXON is LAST on fidelity (0.85 vs 0.91–0.94) and ALONE on poor
  surface validity (64% vs 97–100%). But the deficit is **emission reliability, not
  faithfulness**: AXON decodes only 63/70 attempts; on decoded messages its fidelity is **0.94
  (mid-pack)**. Densest (27 tok) and wins **effective tokens** (31.9 tok/correct msg).
- **Size axis (headline, opposite of weak-model hypothesis):** AXON needs a STRONG model.
  Fidelity/validity climb with capability: qwen35-a3b 0.69/57% → gemma4 0.73/43% →
  qwen3-30b 0.91/64% → gpt-oss-120b 0.95/71% → **qwen3-coder-80b 0.96/86%** (Spearman ρ=+1.00,
  n=5, exploratory).
- **Earns its place on the 2 large models** (gpt-oss-120b, qwen3-coder-80b), on the Pareto
  frontier: ~40% fewer tokens **on the code model vs JSON+Schema** (also more faithful); on
  gpt-oss-120b only ~4% fewer than the best incumbent (struct_english), ~34% vs JSON+Schema.
  Code-tuned model is its best host of all.
- No latency win: reasoning models burn 3–5× completion tokens "thinking" to emit AXON.
- Niche: terse payloads between strong/code-tuned agents in token-metered settings; highest-
  leverage fix is grammar-constrained decoding (validity is the binding constraint, not
  expressiveness).

### Follow-ups completed same session (PR #2: b3efed0, ee17af1)
- **Constrained decoding** (retry-until-valid proxy; box can't grammar-constrain AXON): rescue
  is **partial and splits by model** — gemma4 (weak) rescued 0.73→0.95, gpt-oss (strong) hurt
  0.95→0.81 (forcing invalid complex cells to parse → valid-but-wrong). Validity ≠ correctness.
- **Receiver-capability test**: AXON is **hard to write, easy to read** — among capable readers
  fidelity is flat (mid 0.942 ≈ strong 0.918; JSON ~0.96). Floor is sender-side. Weak-reader
  arm inconclusive (box HTTP 530 on 118/131).
- **Stats**: AXON 0.848 [0.775,0.911] 95% CI (below JSON 0.938); Spearman(capability, AXON
  fidelity)=+1.00 vs +0.20 JSON; paired AXON ties json_schema 45/70, loses 16, wins 9.
- **Venues** (`VENUES.md`): no venue pays author travel → best = **EMNLP 2026 Budapest, present
  remotely** (workshop REALM, deadline ~Jul 17); EU in-person backup NeurIPS Paris satellite.

**Next:** write the **REALM workshop short paper** (report has the spine) + put on arXiv. Run
`/debate-codex` on the results before finalizing. A clean param-size sweep needs a model family
the M5 lacks (current axis is capability-proxy, not parameter ladder). Human review of REPORT.md.

---

## Previous session 2026-03-03 — Multi-Phase Experiment Plan (frontier models)

### Multi-Phase Experiment Plan — All Phases Complete

### Multi-Phase Experiment Plan — All Phases Complete
Executed all 5 phases of the experiment plan in a single session.

### Phase 0: Cheap Wins from Existing Data
- **0A**: Cross-model generalization (Exp 5) — `experiments/exp5_cross_model/analyze.py`
  - AXON: lowest variance (SD=0.484 tok/unit, SD=0.048 composition rate)
- **0B**: Error taxonomy — added to `experiments/exp3_compositionality/analysis/analyze.py`
  - AXON: 94% bimodal (64% perfect, 30% compositional collapse)
- **0C**: Prompt amortization — extended `experiments/exp1_token_efficiency/analysis/analyze.py`
  - AXON breakeven: 7 msgs vs JSON FC, 14 vs FIPA-ACL

### Phase 1: Exp 3 Judge Scoring — COMPLETE
- Implemented 3-judge panel (Claude A, Codex B, random C) with majority vote
- Scored all 567 outputs across 3 files (Haiku, Sonnet, Codex)
- Checkpoint-resume pattern for long-running scoring

### Phase 2: Parse Accuracy Under Noise — COMPLETE
- Built perturbation engine: char deletion, token swap, truncation
- 1,656 perturbed outputs scored
- Results: AXON 16.2%, JSON FC 17.8%, English 100%, FIPA-ACL 90%

### Phase 3: JSON+Contracts — COMPLETE
- 81/81 cells valid (3 models × 9 tasks × 3 runs)
- JSON+Contracts: 51.6% composition rate (vs AXON 67.0%, JSON FC 24.9%)

### Phase 4: Round-Trip Decomposition — COMPLETE
- 177 cross-model decompositions, 99% parseable
- All formats decomposable — no significant differentiation

### Phase 5: Related Work & Paper Framing — COMPLETE
- Updated ecosystem landscape with SEMAP, StructEval, ReliabilityBench, etc.
- Paper outline: `paper/OUTLINE.md`
- Related work draft: `paper/RELATED_WORK.md`

## Critical Finding: AXON Composition Rate Reversal

With full judge scoring, **AXON ranks last on composition rate**:

| Condition | CompRate | FailRate |
|-----------|----------|----------|
| Structured English | **96.2%** | 0.0% |
| Free English | **95.0%** | 0.0% |
| Inst-Matched English | **94.6%** | 0.0% |
| FIPA-ACL | 83.5% | 9.9% |
| JSON FC | 76.2% | 27.2% |
| AISP | 73.7% | 0.0% |
| **AXON** | **67.0%** | 1.2% |

- English conditions jumped +30-45% with judge scoring (implicit composition recovered by LLM judges)
- AXON only gained +1% (machine scoring already captured almost everything)
- At Level 3 (complex tasks), AXON drops to 39.3% vs English 88-93%
- Mixed-effects: AXON **significantly worse** than all 3 English conditions (p<0.001)

### AXON's Remaining Advantages
1. **Machine-parseability**: Composition extractable programmatically (AST walk, no LLM needed)
2. **Nesting depth**: Only format with non-zero nesting (mean 1.87, max 5)
3. **Cross-model consistency**: Lowest variance across models (SD=0.048)
4. **Low failure rate**: 1.2% vs JSON FC 27.2%

### Paper Reframing Required
- Central thesis (intrinsic > extrinsic compositionality) is not supported
- Story must shift to: "machine-readable composition vs interpretable composition"
- Or: "the cost of extracting implicit vs explicit compositional structure"
- Or: methodology paper with AXON as design artifact, not as winner

## Next Steps
1. **Decide on paper framing** — the data doesn't support the original thesis
2. Run `/debate-codex` on the results to stress-test new framing options
3. Update paper outline and related work to match new framing
4. Human validation: Items 8-30 still pending (may be less critical now)

## Blockers
- Strategic decision needed: what story does this paper tell?
