# AISP Deep-Dive Analysis

> **Date**: 2026-02-27
> **Purpose**: Structured technical analysis of AISP (AI Symbolic Programming) for competitive comparison with AXON.
> **Repository**: github.com/bar181/aisp-open-core
> **Version analyzed**: v5.1 (latest as of analysis date)

---

## 1. Claims Audit

AISP makes the following quantitative claims. Each is traced to its source and assessed for methodology.

### 1.1 "97x improvement in multi-step pipeline success rate"

**Source**: README.md, evidence/README.md, reference.md

**Derivation** (from reference.md):
```
P_prose(10) = (0.62)^10 = 0.0084
P_aisp(10) = (0.98)^10 = 0.817
Improvement = P_aisp / P_prose = 97x
```

**Assessment**: This is a mathematical thought experiment, not an empirical measurement. The base assumptions — 62% per-step accuracy for prose, 98% for AISP — are not validated anywhere in the repository. No methodology describes how these per-step rates were measured, what models were used, or what tasks were evaluated. The 97x figure is a derived number from assumed inputs.

**Evidence tier**: **Unverifiable** — no methodology described for base rate measurements.

### 1.2 "Reduces AI decision points from 40-65% to <2%"

**Source**: README.md, AI_GUIDE.md

**Assessment**: No controlled experiment compares decision-point counts between prose and AISP. No definition of "decision point" is provided. No measurement methodology exists.

**Evidence tier**: **Unverifiable** — no operational definition, no measurement.

### 1.3 "Misinterpretation: 25-40% (traditional) vs <1% (AISP)"

**Source**: README.md comparison table

**Assessment**: No experiment measures misinterpretation rates. No definition of "misinterpretation" is given. No evaluation rubric, no sample size, no model specification.

**Evidence tier**: **Unverifiable** — no methodology described.

### 1.4 "Technical Precision: 43/100 (prose) vs 95/100 (AISP)"

**Source**: evidence/tic-tac-toe/analysis.md

**Assessment**: The analysis document states "Status: Placeholder — Full analysis data coming soon." No scoring rubric, no evaluator specification, no sample details. The numbers appear without supporting methodology.

**Evidence tier**: **Unverifiable** — explicitly marked as placeholder by the authors themselves.

### 1.5 "Based on validation of 10,000+ AISP documents"

**Source**: evidence/README.md

**Assessment**: No dataset of 10,000+ documents exists in the repository or any linked resource. The claim appears once with no backing data.

**Evidence tier**: **Unverifiable** — no data available.

### 1.6 "Simple validation (Rust): <1ms, 10,000/sec"

**Source**: evidence/README.md

**Assessment**: Given the validator's simplicity (substring matching + symbol counting), sub-millisecond performance is entirely plausible — but this reflects implementation trivially rather than validation thoroughness. A `grep` command would also achieve similar speeds.

**Evidence tier**: **Hypothesis** — plausible but the claim is vacuous given the validator's simplicity.

### Summary

| Claim | Type | Methodology | Evidence Tier |
|-------|------|-------------|---------------|
| 97x pipeline improvement | Derived calculation | None for base rates | Unverifiable |
| 40-65% to <2% decision points | Assertion | None | Unverifiable |
| 25-40% to <1% misinterpretation | Assertion | None | Unverifiable |
| 43/100 vs 95/100 precision | Placeholder data | "Coming soon" | Unverifiable |
| 10,000+ validated documents | Assertion | No dataset exists | Unverifiable |
| <1ms validation speed | Performance claim | Plausible given trivial validator | Hypothesis |

**0 of 6 claims reach even "Supported" evidence tier.**

---

## 2. Technical Architecture

### 2.1 Format Overview

AISP is a structured document format using Unicode mathematical symbols as notation shorthand. A document consists of:

1. **Header**: `𝔸` + version + name + date (e.g., `𝔸1.0.tic-tac-toe@2026-01-15`)
2. **Context line**: `γ≔domain-name`
3. **Five required blocks**:
   - `⟦Ω:Meta⟧` — metadata and constraints
   - `⟦Σ:Types⟧` — type definitions
   - `⟦Γ:Rules⟧` — rules and invariants
   - `⟦Λ:Funcs⟧` — function definitions
   - `⟦Ε:Evidence⟧` — quality metrics
4. **Optional blocks**: `⟦Χ⟧` (Errors), `⟦Θ⟧` (Proofs), `⟦ℭ⟧` (Categories)

### 2.2 Symbol System

AISP claims 512 symbols organized as 8 categories x 64 per category:

| Category | Name | Example Symbols |
|----------|------|-----------------|
| Ω | Transmuters | `⊤ ⊥ ∧ ∨ ¬ → ↔ ⇒ ⊢ ⊨ ≜ ≔ λ μ` |
| Γ | Topologics | `∈ ∉ ⊂ ⊃ ⊆ ⊇ ∩ ∪ ∅ 𝒫 ε δ` |
| ∀ | Quantifiers | `∀ ∃ ∃! Σ Π ⊕ ⊗ ◊` |
| Δ | Contractors | `State Pre Post Type Sock Logic` |
| 𝔻 | Domains | `ℝ ℕ ℤ ℚ ℂ 𝔹 𝕊 Signal Tensor Hash` |
| Ψ | Intents | `ψ ψ_* ψ_g μ_f μ_r sim_H fit_L` |
| ⟦⟧ | Delimiters | Block markers |
| ∅ | Reserved | `⊞ ✂ Φ ∂ σ ∇` |

**Observation**: The "Contractors" category includes ASCII words (`State`, `Pre`, `Post`, `Type`, `Sock`, `Logic`), not Unicode symbols. The `reference.md` glossary does not actually list 64 distinct entries per category; several categories have fewer than 20 documented symbols. The "512 symbols" claim appears inflated.

### 2.3 Quality Tier System

AISP defines a "semantic density" metric (δ) with tier thresholds:

| Tier | Symbol | Threshold |
|------|--------|-----------|
| Platinum | ◊⁺⁺ | δ ≥ 0.75 |
| Gold | ◊⁺ | δ ≥ 0.60 |
| Silver | ◊ | δ ≥ 0.40 |
| Bronze | ◊⁻ | δ ≥ 0.20 |
| Reject | ⊘ | δ < 0.20 |

**Note**: The tier thresholds in `evidence/README.md` differ from the specification. Evidence claims Platinum ≥ 0.98, Gold ≥ 0.90 — substantially higher than the 0.75/0.60 in the spec. This internal inconsistency is not addressed.

### 2.4 Grammar

AI_GUIDE.md contains a grammar written in AISP's own notation (not standard EBNF or PEG):

```
Doc≜𝔸≫CTX?≫REF?≫⟦Ω⟧≫⟦Σ⟧≫⟦Γ⟧≫⟦Λ⟧≫⟦Χ⟧?≫⟦Ε⟧
Block≜'⟦'∘Cat∘':'∘Name∘'⟧'∘'{'∘Body∘'}'
Stmt≜Def|Rule|Expr|';; '∘.*
Def≜Sym∘('≜'|'≔')∘Expr
Expr≜Lambda|Quant|Binary|Unary|Atom|Compound
Lambda≜'λ'∘Params∘'.'∘Expr
```

**Assessment**: This grammar is not implemented by any parser. It is descriptive, not normative — no tool validates against it. Writing a grammar in a project's own notation rather than a standard formalism makes external validation impossible.

---

## 3. Implementation Audit

### 3.1 Repository Contents

As of the Jan 26, 2026 commit, the repository contains **zero source code**. All code directories (`aisp-rust/`, `validator/`) were removed with the message "Use `cargo install aisp` instead" and "Use `npx aisp-validator` instead."

**Repository is 100% Markdown documentation** + example `.aisp` files + 1 PDF slide deck.

### 3.2 npm: `aisp-validator` v0.3.0

Published 2026-01-15 (5 versions in ~12 hours). 71 downloads/month.

**What it actually does**:

1. Checks if the document starts with `𝔸` (the header character)
2. Checks if 5 required block markers exist as substrings: `⟦Ω`, `⟦Σ`, `⟦Γ`, `⟦Λ`, `⟦Ε`
3. Counts occurrences of specific Unicode symbols (`≜`, `≔`, `∀`, `∃`, `λ`, `⇒`, `∈`, etc.)
4. Computes "semantic density" as:
   ```
   δ = (blocksFound/5 × 0.4) + (min(symbolCount/20, 1) × 0.6)
   ```
5. Maps δ to tier thresholds

**Critical finding**: The "ambiguity" score is **hardcoded**:
```javascript
const ambiguity = valid ? 0.01 : 0.5;
```

This means every document that passes the substring check gets a reported ambiguity of 0.01 — the number is not computed, not measured, and not meaningful.

**What it does NOT do**: Parse an AST, check type correctness, validate scope, check for undefined references, enforce grammar rules, detect semantic errors, or do anything that would conventionally qualify as "validation."

### 3.3 npm: `aisp-converter` v0.1.0

Published 2026-01-26. 34 downloads/month.

A string find-and-replace tool using a 76-entry mapping table:
- "for all" → `∀`, "defined as" → `≜`, "implies" → `⇒`, etc.
- Sorted by longest-match-first for greedy substitution
- Has a "minimal" mode (direct substitution), "standard" (adds headers), "full" (wraps in all blocks)
- Includes LLM fallback capability (calls Anthropic/OpenAI APIs) but requires API keys

The converter's confidence metric is: `mappedChars / totalChars`. This measures surface-level pattern matching, not semantic accuracy.

### 3.4 Rust Crate: `aisp` v0.1.0

Published 2026-01-16. 64 total downloads. Source code is not in the repository (was removed). Description: "AISP 5.1 document validation library."

### 3.5 WASM Binary

A 10,074-byte WASM binary is embedded in the npm package. It exports: `aisp_init`, `aisp_parse`, `aisp_validate`, `aisp_tier`, `aisp_ambig`, `aisp_density`, `aisp_error_code`, `aisp_error_offset`. **Limited to documents under 1KB.** Source code is not available for audit.

### Summary: Implementation Reality

| Component | Claimed | Actual |
|-----------|---------|--------|
| Parser | "AISP document parsing" | Substring matching for block markers |
| Validator | "Document validation" | Symbol counting + block presence check |
| Ambiguity metric | "Computed ambiguity rate" | Hardcoded to 0.01 for all valid documents |
| Semantic density | "Formal quality metric" | `(blocks/5 × 0.4) + (min(symbols/20, 1) × 0.6)` |
| Grammar | "Formal specification" | Written in own notation, not implemented |
| Test suite | Not mentioned | Zero tests in repository, zero in npm package |

---

## 4. Evidence Quality Assessment

### 4.1 Tic-Tac-Toe Case Study

The `evidence/tic-tac-toe/` directory contains an analysis claiming "6 ambiguities → 0" and "43/100 → 95/100 precision." However, `analysis.md` explicitly states: **"Status: Placeholder — Full analysis data coming soon."**

No scoring rubric, no evaluator specification, no model details, no sample size, no methodology of any kind.

### 4.2 Rosetta Stone Validation

The `evidence/rosetta-stone/` directory shows 7 `.aisp` files at different quality tiers being validated. This demonstrates that the AISP validator produces scores for AISP's own example files — a circular validation that proves nothing about effectiveness.

### 4.3 Pipeline Test

The "97x improvement" pipeline test presents compounded success rates but provides no information on: what pipeline, what models, what tasks, what sample size, how individual step success was measured, or who performed the evaluation.

### 4.4 "10,000+ Documents" Claim

Appears once in `evidence/README.md`. No dataset exists in the repository, no link to external data, no description of how documents were generated or sourced.

### 4.5 Tier Threshold Inconsistency

The specification defines Platinum as δ ≥ 0.75. The evidence directory defines Platinum as δ ≥ 0.98. This 23-point discrepancy is not acknowledged or explained.

---

## 5. Community & Adoption Snapshot

| Metric | Value | Notes |
|--------|-------|-------|
| GitHub stars | 122 | Heavily front-loaded: ~60 in first 2 days |
| Forks | 18 | Most in Jan 13-30 window |
| Contributors | 1 | bar181 (Bradley Ross) |
| Commits | 7 | All by single contributor |
| Open issues | 4 | 2 are author-created (recruiting, Q&A) |
| Merged PRs | 0 | 1 PR submitted (88K lines, AI-generated), closed without merge |
| npm downloads (validator) | 71/month | |
| npm downloads (converter) | 34/month | |
| Crates.io downloads | 64 total | |
| Academic citations | 0 | |
| Third-party integrations | 0 | |
| Test suite | None | Zero tests in repo or packages |
| CI/CD | None | |

**Star pattern**: The rapid accumulation of 60+ stars in 48 hours followed by tapering suggests promotional activity rather than organic adoption. For comparison, typical research repositories accumulate stars gradually.

**Issue #1** is titled "Open Invite for AISP Elite Team Members and Research Sponsors" — a recruiting post by the sole author.

**Issue #3** from an external user (marioja) reports being "flabbergasted" by early tests but "discovered issues" and states they are "not fully certain what I observed."

**Issue #4** from sravinet presents a detailed Rust formal verification system claiming 40-50% spec coverage with 100% test success. This code was not merged.

### Author Context

The README identifies the author as a Harvard ALM (Extension School) student. Issue #1 describes the project as a "Harvard ALM capstone project" with completion May 2026. The repo description references "Savant AI" as a related project.

---

## 6. Fundamental Design Differences from AXON

| Dimension | AXON | AISP |
|-----------|------|------|
| **Target use case** | Agent-to-agent messages (M2M) | Human-to-AI specifications (H2M) |
| **Scope** | Single message format | Full document/specification format |
| **Character set** | ASCII only | Unicode mathematical symbols |
| **Grammar** | Formal EBNF, context-free | Written in own notation, not implemented |
| **Parsing** | Recursive descent (947 lines) | Substring matching |
| **Design philosophy** | Minimal, composable, machine-optimized | Comprehensive, symbol-rich, document-oriented |

AISP and AXON address different problems. AXON is a communication protocol for inter-agent messages. AISP is a documentation format for writing specifications. Despite both claiming to improve AI communication, they operate at different layers of the stack.

---

## 7. Conclusions

1. **AISP's claims are quantitatively specific but methodologically unsupported.** Every quantitative claim (97x, <2%, <1%, 43→95) traces to either assumed inputs, placeholder data, or unverifiable assertions.

2. **AISP's implementation is trivially simple.** The "validator" performs substring matching and symbol counting. The "ambiguity metric" is hardcoded. No AST is built, no types are checked, no semantics are verified.

3. **The repository contains no source code.** All implementation was moved to npm/crates packages, making audit harder. The WASM binary has no available source.

4. **Community adoption is surface-level.** 122 stars with a front-loaded pattern, zero merged external contributions, zero third-party integrations, minimal npm downloads.

5. **The project addresses a different problem than AXON.** AISP is a document specification format; AXON is an agent communication protocol. Direct comparison requires careful framing.

6. **Despite these limitations, AISP is worth benchmarking against** because: (a) it occupies mindshare in the same space, (b) empirical comparison demonstrates AXON's methodological advantage by example, and (c) it tests whether elaborate Unicode notation provides any efficiency advantage over ASCII-based formats.
