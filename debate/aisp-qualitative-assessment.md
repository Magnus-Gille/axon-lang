# AISP Qualitative Assessment: Non-Measurable Factors

> **Date**: 2026-02-27
> **Purpose**: Evaluate dimensions that cannot be captured in benchmarks — usability, ecosystem readiness, community health, and strategic positioning.

---

## 1. Usability

### 1.1 Character Set: ASCII vs Unicode

**AXON**: Pure ASCII. Every character is on a standard keyboard. Messages look like:
```
[id:"m1", %%:1] QRY(@agent-a>@agent-b): status(@web-server)
```

**AISP**: Heavy Unicode (mathematical symbols). Documents look like:
```
𝔸1.0.spec@2026-01-15
⟦Σ:Types⟧{ Player≜{X,O}; Board≜Cell[9] }
⟦Γ:Rules⟧{ ∀move:ValidMove(board,pos)⇔board[pos]=Empty }
```

**Assessment**: For agent-to-agent communication (the stated use case for both), character set is irrelevant — agents don't type. However:

- **Debugging**: ASCII is universally renderable in terminals, log files, and monitoring tools. Unicode symbols require UTF-8 support and may render as boxes in some environments.
- **Prompt engineering**: Writing AISP by hand requires copy-pasting Unicode symbols or memorizing Alt codes. AXON can be typed directly.
- **Tokenization**: Unicode mathematical symbols often tokenize as multi-byte sequences, potentially counteracting AISP's claimed compression advantage. A single `≜` may cost 2-3 tokens where AXON's `:` costs 1.
- **Copy-paste robustness**: Some chat interfaces, terminals, and clipboard managers mangle Unicode combining characters or double-width symbols.

**Edge for**: AXON (for practical tooling), AISP (for visual impressiveness in documentation).

### 1.2 Readability

AISP's use of standard mathematical notation (`∀`, `∃`, `λ`, `∈`) is immediately readable to anyone with mathematical training. For the target audience of AI researchers and engineers, this is a genuine advantage for human reading.

AXON's syntax is compact but learnable: `QRY(@a>@b): ...` reads as "query from a to b". The 19-performative vocabulary maps to natural language verbs.

**Assessment**: For human readers, AISP may have a slight readability advantage through mathematical convention. For machine consumption (the actual use case), readability is irrelevant — only parseability matters.

---

## 2. Learning Curve

### 2.1 System Prompt Size

- **AXON**: ~350 tokens (one-shot learnable, as demonstrated in Exp 0)
- **AISP AI_GUIDE.md**: ~19KB / ~4,800 tokens (full specification)
- **AISP CHEATSHEET.md**: ~5KB / ~1,250 tokens (quick reference)

For an LLM to use AISP, the entire AI_GUIDE.md (or at minimum the CHEATSHEET.md) must be included in the system prompt. This is 3.5-14x the prompt overhead of AXON.

**Empirical data** (AXON only): Exp 0 showed AXON is learnable from a 350-token prompt across 3 models with 88-100% compliance. No equivalent test exists for AISP.

### 2.2 Documentation Structure

AISP's documentation is scattered across multiple files with overlapping content:
- `AI_GUIDE.md` (19KB) — the specification, written in AISP notation
- `HUMAN_GUIDE.md` (13KB) — tutorial for humans
- `CHEATSHEET.md` (5KB) — symbol reference
- `reference.md` (29KB) — full 512-symbol glossary
- `guides/advanced/` — 4 "pillar" documents

Total: ~66KB of documentation for a format with no working parser.

AXON has:
- `spec/SPECIFICATION.md` — formal grammar and type system
- System prompt (~350 tokens) — sufficient for LLM usage
- `RESEARCH.md` — evidence rationale
- 3 example files

Total: ~30KB of documentation with a working parser and 54 tests.

**Assessment**: AISP's documentation volume is disproportionate to its implementation. The documentation describes a theoretical system that doesn't exist in code.

---

## 3. Ecosystem Readiness

### 3.1 Tooling Reality

| Tool | AXON | AISP |
|------|------|------|
| Parser | Working (Python, 947 lines) | None (substring matching only) |
| Validator | Working (3 tiers) | Counts symbols |
| Formatter | None | None |
| LSP / IDE plugin | None | None |
| Linter | None | None |
| Converter | None | npm `aisp-converter` (find-and-replace) |
| REPL | None | None |

AISP has a converter tool (find-and-replace with 76 English→symbol mappings) — AXON does not. This is a genuine AISP capability, though its value for agent communication is questionable.

### 3.2 Integration Path

For integration into an existing system:

**AXON**: Import Python parser → parse messages → get typed AST → route by performative. Clear integration story.

**AISP**: Install npm package → call validate() → get boolean + symbol count. No AST, no typed output, no routing capability. For actual use, you'd need to write your own parser from scratch.

---

## 4. Community Health

### 4.1 Bus Factor

Both projects currently have a bus factor of 1.

- **AXON**: Single researcher, but the adversarial review process (Claude + Codex) and documented debate transcripts create institutional knowledge. All decisions have recorded rationale. A new contributor could understand design choices from the debate archive.
- **AISP**: Single contributor. All source code removed from the repo and published to npm/crates. No design decision documentation. If the maintainer abandons the project, there is no path to understanding or extending the codebase.

### 4.2 Contribution Quality

AISP's sole external PR was 88,243 additions across 247 files — clearly AI-generated bulk content. It was closed without merge. This suggests the project may attract enthusiasm but not quality contributions.

AXON has no external contributors (research project), but the structured debate methodology produces high-quality critical review: ~100 critique points raised, ~85% resolved.

### 4.3 Issue Engagement

AISP's 4 open issues include:
- 2 author-created (recruiting, Q&A)
- 1 user report that is uncertain about what they observed
- 1 detailed formal verification proposal (not merged)

This pattern suggests interest but not productive engagement.

---

## 5. Marketing Effectiveness

### 5.1 What AISP Does Well

AISP's marketing is objectively more effective than AXON's:

1. **Memorable headline number**: "97x improvement" is dramatic and shareable, even if unsubstantiated.
2. **Visual sophistication**: Unicode mathematical symbols signal seriousness to casual observers.
3. **Polished README**: Professional presentation with comparison tables, tier badges, and clear (if inflated) claims.
4. **Easy to try**: `npx aisp-validator` gives instant feedback (even if that feedback is essentially "yes, you used Unicode symbols").
5. **Quick hook**: "Made for AI and agents" + "Reduces decision points from 40-65% to <2%" tells a compelling story in seconds.

### 5.2 What AXON Can Learn

1. **Lead with the headline metric**: "32% more efficient than JSON function calling" is memorable. Use it.
2. **Visual comparison**: Side-by-side AXON vs English examples in the README, not buried in research docs.
3. **One-command demo**: `echo 'QRY(@a>@b): status(@srv)' | python3 src/axon_parser.py -` should be front and center.
4. **Benchmark table**: The Exp 1 results table is publishable — put it in the README.
5. **Lower barrier**: The 350-token system prompt is a strength — market it as "learn AXON in one prompt."

### 5.3 What AISP's Marketing Obscures

The impressive presentation masks:
- Zero working implementations beyond substring matching
- Zero controlled experiments
- Zero test cases
- Hardcoded metrics passed off as computed
- Placeholder evidence documents
- Internal inconsistencies (tier thresholds differ between spec and evidence)

This creates a credibility debt. When users try to build something real with AISP, they discover the implementation doesn't match the marketing. Issue #3 (user reporting confusion about what they observed) may be an early signal.

---

## 6. Academic Positioning

### 6.1 Publication Readiness

**AXON**:
- Pre-registered experimental design → publishable
- 6-condition controlled comparison → publishable
- Adversarial review methodology → publishable (Track B)
- Statistical analysis with effect sizes and CIs → meets journal standards
- Dual-track confirmatory/exploratory design → methodologically sophisticated

**AISP**:
- No experiments → nothing to publish
- No methodology → no contribution to describe
- "Harvard ALM capstone" context → student project, not independent research
- Claims without evidence → would not pass peer review

### 6.2 Citation Potential

AXON's methodology (pre-registered multi-condition LLM benchmark) is novel and citable independent of results. The adversarial review process is separately publishable.

AISP has no citable contribution. The symbol system is not novel (it's mathematical notation applied to document structure). The claims are not supported.

---

## 7. Interoperability

### 7.1 Relationship to Existing Standards

**AXON**:
- Draws from FIPA-ACL (performative concept) but simplifies for LLM consumption
- Compatible with JSON through record syntax
- Experiment includes FIPA-ACL and JSON FC as direct comparison conditions
- ASCII-only means universal tooling compatibility

**AISP**:
- No explicit relationship to any existing standard
- No mapping to/from JSON, XML, or other formats (converter maps English → AISP only)
- No interoperability story for systems that don't understand AISP
- The converter tool's API fallback (calling Anthropic/OpenAI) introduces external dependencies for basic functionality

### 7.2 Degradation Path

If an agent doesn't understand the format:

**AXON**: Falls back to structured English (the instruction-matched condition is essentially AXON concepts in English). LLMs can read AXON messages without the system prompt and extract meaning from the readable syntax.

**AISP**: Falls back to... Unicode symbols in blocks. Without understanding the symbol vocabulary, the content is opaque. `∀move:ValidMove(board,pos)⇔board[pos]=Empty` requires mathematical literacy that not all LLMs demonstrate equally.

---

## 8. Risk Assessment

### 8.1 Project Continuity

| Risk | AXON | AISP |
|------|------|------|
| Maintainer abandonment | Code + tests + spec remain usable | npm packages remain but no source code to extend |
| Breaking changes | Versioned spec (v0.1-experimental), explicit stability guarantees | v5.1 but 7 commits — unclear stability model |
| Dependencies | Python stdlib only | Node.js + optional WASM + optional API keys |
| Reproducibility | All experiments re-runnable from repo | Nothing to reproduce |

### 8.2 Adoption Risk

If a team adopts AISP today:
1. The validator will accept malformed documents (no real parsing)
2. There's no way to check correctness beyond symbol presence
3. The sole maintainer is a student with a May 2026 graduation deadline
4. Source code is not available for the Rust/WASM components

If a team adopts AXON today:
1. The parser will reject malformed messages with specific error messages
2. Three tiers of validation are available
3. The format is research-backed with published experimental data
4. All source code is available and auditable

---

## Summary

| Dimension | AXON Advantage | AISP Advantage | Notes |
|-----------|---------------|----------------|-------|
| Usability (typing) | ASCII keyboard | — | AXON characters all typeable |
| Usability (reading) | — | Math notation familiar to researchers | Marginal for M2M |
| Learning curve | 350-token prompt | — | AISP needs 1,250-4,800 tokens |
| Ecosystem | Working parser/validator | npm converter tool | Different capabilities |
| Community health | Decision audit trail | Higher star count | Stars ≠ health |
| Marketing | — | Effective messaging | AXON can learn from this |
| Academic positioning | Publication-ready | — | AISP has no publishable contribution |
| Interoperability | JSON-compatible, FIPA-aware | — | AISP is isolated |
| Graceful degradation | Readable ASCII fallback | — | AISP requires symbol literacy |
| Risk (continuity) | All code + tests in repo | — | AISP source removed |
| Risk (adoption) | Real validation | — | AISP validator accepts malformed input |

AISP's sole clear advantage is marketing effectiveness. AXON should study and learn from AISP's communication strategy while maintaining its evidence-first approach.
