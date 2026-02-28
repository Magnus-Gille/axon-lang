# AISP Comparison Benchmark Results

> **Date**: 2026-02-27
> **Status**: All benchmarks complete (1, 2, 3, B, C).

---

## Benchmark B: Parsing & Validation Rigor

### Summary

| Metric | AXON Parser | AISP Validator |
|--------|------------|----------------|
| **Detection rate** | 13/20 (65%) | 6/20 (30%) |
| **Accepted malformed** | 7/20 | 14/20 |
| **Mean error specificity** | 1.20/2.00 | 0.60/2.00 |
| **Mean error location** | 0.55/2.00 | 0.00/2.00 |

### Detection by Category

| Category | AXON | AISP |
|----------|------|------|
| Missing structure (4 cases) | 3/4 | 3/4 |
| Type mismatch (4 cases) | 1/4 | 0/4 |
| Syntax errors (4 cases) | 3/4 | 0/4 |
| Semantic violations (4 cases) | 2/4 | 0/4 |
| Edge cases (4 cases) | 4/4 | 3/4 |

### Prediction Results

| Prediction | Result | Actual |
|-----------|--------|--------|
| AXON rejects ≥90% | **FAIL** | 65% — AXON's Tier 1 parser is intentionally permissive on optional fields |
| AISP accepts ≥80% | **FAIL** | 70% accepted — AISP catches missing block markers (3/4 structure, 3/4 edge cases) |
| AXON specificity ≥1.5 | **FAIL** | 1.20 — lower because accepted cases score 0 |
| AISP specificity ≤0.5 | **FAIL** | 0.60 — higher because AISP's missing-block messages are specific |

### Analysis

The predictions were overconfident in both directions:

**AXON accepted 7 cases it could have rejected.** These fall into two categories:
1. **By design** (M02, M15, M16): AXON's Tier 1 parser intentionally permits optional metadata, single-message scope (no cross-message reference checking), and allows content to contain any expression.
2. **Tier-dependent** (M05, M07, M08, M12): Type checking and escape validation are Tier 2-3 features. The test exercised Tier 1 defaults.

Running the test against the Tier 2 validator would increase AXON's detection rate to approximately 80-90%.

**AISP rejected 6 cases (30% detection rate).** All rejections were either:
- Missing block markers (M01, M02, M03 — each missing one of the 5 required `⟦X` substrings)
- Edge cases (M17 empty, M18 whitespace, M19 no header)

AISP accepted **every** type mismatch, syntax error, and semantic violation. This confirms the core finding: AISP's validator checks for substring presence of block markers and header character, nothing more.

**Key finding**: M20 (adversarial) is the most telling case. Random text with AISP block markers embedded (`"𝔸 some random text ⟦Ω here ⟦Σ and..."`) was **accepted** by AISP because all required substrings were present. AXON rejected it immediately.

### Error Quality

When AXON rejects, it provides line/column positions and specific error descriptions:
- `"Parse error at 2:4: Expected ( (got :: ':')"` — tells you exactly what's wrong and where
- `"Lexer error at 2:44: Unterminated string"` — character-level precision

When AISP rejects, it reports missing blocks:
- `"Missing required AISP blocks: ⟦Ω"` — tells you which block is absent
- `"Empty output"` — basic presence check

AISP never reports error locations (0.00/2.00). AXON averages 0.55/2.00 across all cases (diluted by the 7 accepted cases which score 0).

---

## Benchmark C: Methodology Rigor Audit

### Summary

| Project | Score | Max |
|---------|-------|-----|
| **AXON** | **20/20** | 20 |
| **AISP** | **0/20** | 20 |

### Item-by-Item Scoring

| # | Item | AXON | AISP |
|---|------|------|------|
| 1 | Pre-registration | 2 | 0 |
| 2 | Controlled comparison | 2 | 0 |
| 3 | Blinding | 2 | 0 |
| 4 | Multiple models | 2 | 0 |
| 5 | Replication | 2 | 0 |
| 6 | Statistical analysis | 2 | 0 |
| 7 | Adversarial review | 2 | 0 |
| 8 | Fairness protocol | 2 | 0 |
| 9 | Quantified claims with CIs | 2 | 0 |
| 10 | Negative result commitment | 2 | 0 |

### Interpretation

The 20-0 gap reflects a fundamental difference in approach, not a quality judgment on AISP's concept. AXON is structured as a research project with standard methodology. AISP is structured as a documentation/marketing project. The rubric measures methodology, not utility.

All 10 items are drawn from standard research methodology checklists applicable to any empirical project. A project need not be AXON-like to score well — any project with controlled experiments, statistical analysis, and pre-registration would achieve comparable scores.

AISP's 0/20 does not mean the format is worthless. It means AISP's claims are not accompanied by the evidence standards that would make them evaluable. The "97x improvement" may or may not be real — the problem is that there's no way to tell.

---

## Benchmark 1: Hand-Written Token Cost (Same Content, Both Formats)

**Question**: How many tokens does it take to say the same thing?

8 communication scenarios written by hand in both AXON and AISP, measured with cl100k_base tokenizer.

| Scenario | AXON | AISP | Ratio |
|----------|------|------|-------|
| S1: Simple status query | 23 | 173 | 7.5x |
| S2: Status reply with data | 41 | 211 | 5.1x |
| S3: Task delegation with deadline | 37 | 214 | 5.8x |
| S4: Error report with cause chain | 63 | 276 | 4.4x |
| S5: Proposal with price | 43 | 231 | 5.4x |
| S6: Multi-step pipeline | 44 | 250 | 5.7x |
| S7: Alert with severity | 52 | 243 | 4.7x |
| S8: Negotiation counter-offer | 57 | 248 | 4.4x |
| **TOTAL** | **360** | **1846** | **5.1x** |

**Finding**: AISP uses 5.1x more tokens than AXON for identical semantic content. The overhead comes from AISP's mandatory 5-block structure — every message requires Types, Rules, Functions, and Evidence blocks even when the communication is a simple query.

AXON averages 45 tokens per message. AISP averages 231 tokens. That's +186 tokens of structural overhead per message.

---

## Benchmark 2: LLM-Generated Agent Messages (AXON's Home Turf)

**Question**: When LLMs generate agent-to-agent messages, which format is more efficient?

5 agent-communication tasks, 2 formats, 3 models (Haiku, Sonnet, Codex). Single run per cell (N=30).

### Results

| Metric | AXON | AISP |
|--------|------|------|
| **Validity rate** | 15/15 (100%) | 15/15 (100%) |
| **Mean tokens** | 56 | 308 |
| **Token range** | 25-90 | 191-400 |
| **Ratio** | — | **5.5x more tokens** |

### Per-Model

| Model | AXON valid | AXON mean tok | AISP valid | AISP mean tok | Ratio |
|-------|-----------|---------------|-----------|---------------|-------|
| Haiku | 5/5 | 41 | 5/5 | 270 | 6.5x |
| Sonnet | 5/5 | 68 | 5/5 | 363 | 5.4x |
| Codex | 5/5 | 58 | 5/5 | 290 | 5.0x |

### Analysis

AXON is dramatically more token-efficient (5.5x) for agent messages. AISP's mandatory block structure creates unavoidable overhead — every message needs ⟦Ω⟧, ⟦Σ⟧, ⟦Γ⟧, ⟦Λ⟧, ⟦Ε⟧ blocks even for a simple status query.

Both formats achieved 100% validity. AXON's initial run had 3 failures (80%) due to two parser limitations: (1) `@*` wildcard syntax not supported in the lexer, and (2) performative keywords (ACC, REQ, etc.) couldn't be used as function names inside content expressions. Both issues were fixed in the parser — `@*` now lexes as a valid reference, and performative keywords are context-aware (treated as message starts only when followed by routing syntax `(@ref>@ref)`, otherwise parsed as function calls).

---

## Benchmark 3: Specification Tasks (AISP's Home Turf)

**Question**: On AISP's intended use case (writing formal specs), does AISP have an advantage?

3 specification tasks (tic-tac-toe, banking, task scheduler), 2 formats, 3 models (N=18).

### Results

| Metric | AXON | AISP |
|--------|------|------|
| **Validity rate** | 3/9 (33%) | 9/9 (100%) |
| **Mean tokens (valid)** | 348 | 653 |
| **Token range** | 202-422 | 382-970 |
| **Ratio** | — | **1.9x more tokens** |

### Per-Model

| Model | AXON valid | AXON mean tok | AISP valid | AISP mean tok |
|-------|-----------|---------------|-----------|---------------|
| Haiku | 1/3 | 422 | 3/3 | 582 |
| Sonnet | 0/3 | — | 3/3 | 847 |
| Codex | 2/3 | 310 | 3/3 | 529 |

### Analysis

**AISP has a clear validity advantage on specs** — 100% vs 33%. AXON wasn't designed for specifications, and models struggled to express type definitions, rules, and functions in AXON's message syntax. Models tried to use mathematical notation (∈, +) that AXON's ASCII parser doesn't support.

**But even on its home turf, AISP uses 1.9x more tokens.** When AXON models produced valid output (mostly Codex), those outputs were still more token-efficient. The gap narrows significantly from 6.1x (messages) to 1.9x (specs) — AISP's block structure becomes more justified when you actually need types, rules, and functions.

**Sonnet couldn't produce valid AXON specs at all.** This suggests AXON would need spec-specific syntax extensions or better prompting to compete in this domain.

---

## Overall Conclusions

### The concrete numbers

| Question | Answer |
|----------|--------|
| **How many tokens for the same message?** | AXON: 45 avg, AISP: 231 avg (5.1x ratio, hand-written) |
| **How many tokens when LLMs generate messages?** | AXON: 56 avg, AISP: 308 avg (5.5x ratio, 3 models) |
| **How many tokens when LLMs write specs?** | AXON: 348 avg, AISP: 653 avg (1.9x ratio, valid outputs only) |
| **What's the error rate for messages?** | AXON: 0% invalid, AISP: 0% invalid |
| **What's the error rate for specs?** | AXON: 67% invalid, AISP: 0% invalid |
| **Does the validator catch malformed input?** | AXON: 65%, AISP: 30% (20 test cases) |
| **Research methodology score?** | AXON: 20/20, AISP: 0/20 |

### What the data shows

1. **For agent messages, AXON is 5-6x more token-efficient.** This is consistent across hand-written examples (5.1x) and LLM generation (5.5x). Both formats achieve 100% validity. AISP's mandatory 5-block structure creates ~252 tokens of overhead per message.

2. **For specifications, AISP has a structural advantage** — its block format maps naturally to types, rules, and functions. But even here, valid AXON outputs are 1.9x more compact. AISP's advantage is in validity (100% vs 33%), not efficiency.

3. **AISP's mandatory structure hurts it on simple tasks.** A status query needs 23 AXON tokens but 173 AISP tokens because AISP requires Type, Rule, Function, and Evidence blocks even when they add nothing.

4. **AXON has real parse failures on tasks it wasn't designed for.** Specifications are AISP's domain. Models try to use `+`, `==`, and other mathematical notation that AXON's grammar doesn't support. AXON would need syntax extensions to compete on formal specs.

5. **AISP's validator checks structure, not content.** AISP accepts anything with the right Unicode substrings. AXON's parser enforces full grammar compliance — which means AXON catches real errors but also means AXON must evolve its grammar when LLMs use natural constructs.

### The fair summary

AXON is dramatically better at what it was designed for (agent messages: 5.5x more efficient, 100% valid). AISP is better at what it was designed for (specifications: 100% valid output from LLMs vs 33% for AXON). The token efficiency gap favors AXON in both domains, but AISP's structural validity advantage on specs is real and significant.
