# AISP vs AXON: Structured Comparison Matrix

> **Date**: 2026-02-27
> **Purpose**: Side-by-side evaluation across 15 dimensions using AXON's evidence tier classification.
> **Method**: Each dimension evaluated with specific evidence. AISP claims classified as Established, Supported, Hypothesis, or Unverifiable.

---

## Evidence Tier Legend

| Tier | Definition | Criteria |
|------|-----------|----------|
| **Established** | Replicated, peer-reviewed or independently verified | Multiple models, controlled conditions, statistical analysis |
| **Supported** | Directionally correct with limited evidence | Single experiment or preliminary data |
| **Hypothesis** | Plausible but unverified | Theoretical argument without empirical test |
| **Unverifiable** | No described methodology | Claims with no way to evaluate truth value |

---

## Category 1: Technical

### 1.1 Grammar Formalism

| Aspect | AXON | AISP |
|--------|------|------|
| **Grammar format** | EBNF in `spec/SPECIFICATION.md` | Custom notation in `AI_GUIDE.md` |
| **Standard notation** | Yes (EBNF — ISO 14977) | No (written in AISP's own symbols) |
| **Machine-readable** | Yes — drives recursive descent parser | No — descriptive only |
| **Completeness** | Full grammar for all message forms | Partial — operators and precedence described but not all productions |
| **Ambiguity** | Context-free, deterministic | Not analyzed (no parser to test) |

**Verdict**: AXON has a formal, implemented grammar. AISP has a descriptive grammar in non-standard notation that is not implemented by any tool.

### 1.2 Parser Quality

| Aspect | AXON | AISP |
|--------|------|------|
| **Implementation** | 947-line recursive descent parser in Python | Substring matching in JavaScript |
| **AST output** | Full typed AST with position tracking | None — returns boolean valid/invalid |
| **Error messages** | Line/column specific with descriptive messages | "Invalid document" (no position, no explanation) |
| **Error recovery** | Partial (reports first error) | N/A (no parsing occurs) |
| **Edge cases handled** | Nested records, multi-message, complex expressions | Documents under 1KB (WASM), any size (JS substring check) |
| **Lines of code** | ~947 (parser) + ~400 (validator) | ~200 (JS validator, no parser logic) |

**Verdict**: AXON has a real parser that builds ASTs. AISP has a string presence checker that calls itself a validator.

### 1.3 Type System

| Aspect | AXON | AISP |
|--------|------|------|
| **Types defined** | String, Number, Boolean, Null, List, Record, Reference, Tag, Variable, Unit-bearing numbers | Listed in `⟦Σ:Types⟧` blocks (per-document) |
| **Type checking** | Parser validates literal forms; validator checks tier-specific type usage | None — no type checker exists |
| **Composability** | Nested records, tagged records, lists of records | Described in grammar but not enforced |

**Verdict**: AXON enforces types at parse time. AISP describes types in documentation but never checks them.

### 1.4 Error Handling

| Aspect | AXON | AISP |
|--------|------|------|
| **Syntax errors** | Caught with line/column position | Not detected (substring matching accepts malformed content) |
| **Type errors** | Caught by validator at Tier 2+ | Not detected |
| **Semantic errors** | Checked at Tier 3 (undefined references, duplicate metadata keys) | Not detected |
| **Recovery** | Reports first error, continues where possible | N/A |

**Prediction** (testable via Benchmark B): AISP's validator will accept >80% of intentionally malformed inputs because it only checks for substring presence of block markers and Unicode symbols.

### 1.5 Composability

| Aspect | AXON | AISP |
|--------|------|------|
| **Message composition** | Multiple messages in single document; nested expressions; pipeline operators | Blocks compose within a document but no inter-document references |
| **Pipeline support** | `->` (sequence), `<-` (cause), `&` (parallel) operators | `≫` (sequence) in grammar description, not enforced |
| **Extensibility** | New performatives, custom tags, metadata keys | New blocks via `⟦X:Name⟧` (not validated) |

**Verdict**: AXON's composability is implemented and tested. AISP's is described but not enforced.

---

## Category 2: Empirical

### 2.1 Evidence Methodology

| Aspect | AXON | AISP |
|--------|------|------|
| **Pre-registration** | Yes — `experiments/PREREGISTRATION.md` frozen before data collection | No |
| **Experimental design** | 6 conditions × 3 models × 9 tasks × 3 runs = 486 cells | No controlled experiments |
| **Baselines** | 5 controlled baselines (free English, structured English, instruction-matched English, JSON FC, FIPA-ACL) | Comparison to "traditional prose" (undefined) |
| **Blinding** | Judges don't know which condition produced output (FAIRNESS.md) | N/A |
| **Fairness protocol** | Documented in FAIRNESS.md — symmetric prompt budgets, metadata equivalence, 3-judge panel | None |

**AXON evidence tier**: **Supported** → **Established** (pending full statistical publication)
**AISP evidence tier**: **Unverifiable** (no experiments exist)

### 2.2 Controlled Experiments

| Aspect | AXON | AISP |
|--------|------|------|
| **Exp 0 (Learnability)** | PASS on all 3 models, 3x replications | None |
| **Exp 1 (Token efficiency)** | 486 outputs scored, AXON #1 at 15.4 tok/unit | None |
| **Cross-validation** | 30 items, 94.1% machine-judge agreement | None |
| **Human validation** | In progress (30 items, 5 per condition) | None |

### 2.3 Statistical Rigor

| Aspect | AXON | AISP |
|--------|------|------|
| **Tests used** | Welch's t-test, Holm-Bonferroni correction, Cohen's d, bootstrap CIs, mixed-effects models | None |
| **Effect sizes** | Reported with confidence intervals | No effect sizes |
| **Multiple comparisons** | Holm-Bonferroni across 5 pairwise comparisons | N/A |
| **Pre-registered analysis plan** | Yes | No |
| **Sensitivity analyses** | All-judge scoring on cross-validation subset | None |

### 2.4 Replication

| Aspect | AXON | AISP |
|--------|------|------|
| **Internal replication** | 3 runs per cell | None |
| **Cross-model** | 3 models (Claude Haiku, Claude Sonnet, Codex) | Not applicable |
| **Reproducibility** | All prompts, scoring rubrics, and infrastructure in repository | Nothing to reproduce |

---

## Category 3: Ecosystem

### 3.1 Test Suite

| Aspect | AXON | AISP |
|--------|------|------|
| **Conformance tests** | 54 (valid + invalid cases in `tests/conformance/`) | 0 |
| **Validator tests** | `tests/test_validator.py` with pytest | 0 |
| **Experiment outputs** | 486 scored cells | 0 |
| **CI/CD** | Not configured (local development) | Not configured |

### 3.2 Packages & Tooling

| Aspect | AXON | AISP |
|--------|------|------|
| **Parser** | Python, stdlib only (`src/axon_parser.py`) | npm: `aisp-validator` (71 dl/month) |
| **Validator** | Python, stdlib only (`src/axon_validator.py`) | Same package (substring matching) |
| **Converter** | N/A | npm: `aisp-converter` (34 dl/month) |
| **Rust crate** | N/A | `aisp` (64 total downloads) |
| **IDE support** | None | None |
| **Language server** | None | None |

### 3.3 Documentation

| Aspect | AXON | AISP |
|--------|------|------|
| **Specification** | `spec/SPECIFICATION.md` — formal, versioned | `AI_GUIDE.md` — 19KB guide in AISP notation |
| **Research backing** | `RESEARCH.md` — 20+ cited sources | No citations to external research |
| **Examples** | 3 example files + English comparisons | 4 evidence examples + 3 tier guides |
| **Cheatsheet** | System prompt (~350 tokens) | `CHEATSHEET.md` (~5KB) |

---

## Category 4: Claims Assessment

### 4.1 Claim Specificity

| Aspect | AXON | AISP |
|--------|------|------|
| **Primary claim** | "~32% better tok/unit vs JSON FC" | "97x improvement in pipeline success" |
| **Measured vs derived** | Measured (486 outputs, 3 judges, 3 models) | Derived from assumed base rates |
| **Qualifying language** | "~32%", includes effect size and CI | "97x", presented as definitive |

### 4.2 Falsifiability

| Aspect | AXON | AISP |
|--------|------|------|
| **Can claims be tested?** | Yes — specific metrics, specific conditions, specific models | Partially — but no methodology exists to replicate |
| **What would disprove?** | AXON scoring worse than baselines on tok/unit | AISP failing pipeline tests (but no test exists) |
| **Negative result commitment** | Documented in PREREGISTRATION.md | No |

### 4.3 Evidence Tier Classification of All Claims

| AISP Claim | Evidence Tier | Reason |
|-----------|---------------|--------|
| 97x pipeline improvement | **Unverifiable** | Derived from unmeasured assumptions |
| <2% decision points | **Unverifiable** | No measurement methodology |
| <1% misinterpretation | **Unverifiable** | No measurement methodology |
| 43→95 precision | **Unverifiable** | "Placeholder — coming soon" |
| 10,000+ validated docs | **Unverifiable** | No dataset exists |
| <1ms validation speed | **Hypothesis** | Plausible given trivial implementation |

| AXON Claim | Evidence Tier | Reason |
|-----------|---------------|--------|
| ~32% better tok/unit vs JSON FC | **Supported** | 486 outputs, 3 models, pre-registered |
| Passes learnability gate | **Supported** | 3x replications across 3 models |
| 94.1% machine-judge agreement | **Supported** | 30-item cross-validation |
| Zero complete failures | **Supported** | Observed across all 486 outputs |

---

## Category 5: Adoption

### 5.1 Community Metrics

| Metric | AXON | AISP |
|--------|------|------|
| **GitHub stars** | N/A (research project) | 122 (front-loaded) |
| **Forks** | N/A | 18 |
| **Contributors** | Adversarial review (Claude + Codex) | 1 (sole author) |
| **External PRs merged** | N/A | 0 |
| **npm downloads** | N/A | 105/month combined |
| **Academic citations** | 0 (pre-publication) | 0 |
| **Third-party usage** | 0 | 0 |

### 5.2 Marketing vs Substance

AISP's 122 stars represent marketing effectiveness. The project launched with a polished README, mathematical symbols that signal sophistication, and claims of dramatic improvements. This attracted attention despite the absence of supporting evidence.

AXON's approach prioritizes evidence over marketing. The research-first strategy means lower visibility but higher credibility when published.

**Lesson for AXON**: Marketing matters. AXON's eventual publication should include a clear, memorable headline metric (the ~32% improvement) and visual comparisons that make the methodology difference obvious.

---

## Summary Scorecard

| Category | AXON | AISP |
|----------|------|------|
| Grammar formalism | Formal EBNF, implemented | Non-standard notation, not implemented |
| Parser quality | Recursive descent, AST output | Substring matching |
| Type system | Enforced at parse time | Described only |
| Error handling | Line/column errors | No error detection |
| Composability | Tested operators | Described only |
| Evidence methodology | Pre-registered, 6-condition design | None |
| Controlled experiments | 486 scored outputs | None |
| Statistical rigor | t-tests, CIs, effect sizes | None |
| Replication | 3 runs × 3 models | None |
| Test suite | 54 conformance tests | 0 |
| Packages | Python (stdlib) | npm + Rust crate |
| Claim specificity | Measured with CIs | Derived/asserted |
| Falsifiability | Yes | No methodology to replicate |
| Community | Research project | 122 stars, 1 contributor |
| Marketing | Minimal | Effective |

**The comparison is asymmetric by design.** AXON is a research project with empirical methodology. AISP is a marketing-forward project with aspirational claims. The value of this comparison is demonstrating what rigorous evaluation looks like versus what it doesn't.
