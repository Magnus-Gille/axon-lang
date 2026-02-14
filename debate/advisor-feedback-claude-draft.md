# Senior Research Advisor Feedback — Claude's Response Draft

## Context

A senior research advisor provided comprehensive feedback on the AXON project across 5 dimensions: novelty, theory, publishability, real-world feasibility, and actionable advice. This draft assesses each of 10 key claims and proposes actions.

---

## Point 1: Positioning & Framing

**Advisor**: "Stop selling 'a new language'; sell 'an empirical comparison of agent communication formats.'"

**Position: AGREE with modification.**

The advisor is right that the most publishable story is the empirical comparison, not the language itself. But I'd reframe slightly: we're selling *both*. The language is the artifact; the comparison is the contribution. Many good systems papers work this way — you build a thing, then rigorously evaluate it against alternatives.

**Concrete action**: Reframe README and any paper as "we built AXON as a candidate format and tested it against 5 baselines in a preregistered 6-condition evaluation." The language spec becomes supporting material, not the headline.

**Priority**: HIGH. Affects how we write everything going forward.
**Timing**: Now — before we write any results paper.

---

## Point 2: Novelty Assessment

**Advisor**: AXON's differentiator is the combination (speech-act + compositional operators + tiered compliance + prereg evaluation). TOON, LACP, and IETF draft are active adjacent work.

**Position: AGREE. This is accurate and actionable.**

We already cite TOON and LACP in RESEARCH.md (§6). The IETF draft (Dec 2025) is new — we need to add it. The advisor correctly identifies that AXON's novelty isn't any single feature but the specific combination plus the evaluation posture.

**Concrete actions**:
1. Add IETF draft citation to RESEARCH.md §6
2. Sharpen the positioning: "AXON is a speech-act message language (not a data format like TOON, not a protocol architecture like LACP, not a data layer like the IETF draft) — it's a compact expression language with built-in compositional semantics"
3. Add explicit comparison table: AXON vs TOON vs LACP vs IETF draft on key dimensions

**Priority**: MEDIUM. Important for any publication, but doesn't block current experiments.
**Timing**: Before writing the paper. Can be done in parallel with Exp 1 scoring.

---

## Point 3: Validator Symmetry (CRITICAL)

**Advisor**: Condition validators are asymmetric (English = "non-empty", JSON = "valid JSON", FIPA = substring, AXON = full parse). "Will get attacked hard in peer review."

**Position: STRONGLY AGREE. This is the most important methodological fix.**

Looking at `experiments/lib/condition_adapter.py`:
- `_validate_english()` (line 71): Any non-empty string passes. All 3 English conditions use this.
- `_validate_json_fc()` (line 79): Valid JSON + top-level object/array. No schema validation.
- `_validate_fipa_acl()` (line 92): Substring check for performative presence. Very loose.
- `_validate_axon()` (line 112): Full parse via reference parser. Strictest by far.

This asymmetry means the compliance rates are **not comparable across conditions**. AXON at 88.9% under strict validation is being compared to English at 100% under trivial validation. That's not a fair comparison.

**Should we fix retroactively for Exp 0?**
No. Exp 0 is a learnability gate — "can the model produce something that roughly looks like this format?" The loose validators are appropriate for that question. But we MUST:
1. Document the asymmetry explicitly in Exp 0 results
2. Build strict validators for Exp 1+ where correctness matters
3. Report Exp 0 with the caveat that compliance rates are not directly comparable across conditions

**Concrete actions for strict validators**:
- **Structured English**: Parse for required sections/headers matching the prompt template. Check key-value pairs present.
- **Instruction-matched English**: Check for all instructed speech-act labels, metadata fields, routing indicators.
- **JSON FC**: Validate against a JSON Schema with required keys (`performative`, `sender`, `receiver`, `content`), allowed performative values, type checks.
- **FIPA-ACL**: Implement a minimal S-expression parser for the FIPA subset we use. Parse performative, sender, receiver, content fields.

**Priority**: CRITICAL. Must be done before Exp 1 scoring begins.
**Timing**: NOW — this is the single most impactful action.

---

## Point 4: Semantic Scoring Approach

**Advisor**: Define task-specific canonical semantic representation (gold JSON), build extractors per condition, score field-level F1. "Tokens per correctly transmitted field."

**Position: PARTIALLY AGREE. Good in theory, premature to replace our approach.**

The advisor's proposal is the gold standard for rigorous evaluation. But it has significant implementation cost:
- Building extractors per condition × per task = 6 × 9 = 54 extraction pipelines
- Defining gold canonical representations for 9 tasks
- Handling the many ways the same semantic content can be expressed in free-form English

Our current approach (LLM judges scoring element presence) is a reasonable proxy. The key question is whether it's *good enough* for the claims we're making.

**Compromise position**:
1. Keep LLM judges as the primary approach for Exp 1 (it's already built and frozen in DEVIATION.md)
2. Build canonical gold representations for the 30-item human validation subset
3. Report the correlation between LLM-judge scores and gold-extraction scores on that subset
4. If correlation is high (>0.9), the LLM judge is validated. If low, we have a problem to solve.
5. For a future paper, build full extractors if needed.

**Priority**: MEDIUM. The human validation subset is already required by FAIRNESS.md.
**Timing**: In parallel with Exp 1 scoring — the 30-item subset should be scored first.

---

## Point 5: Shannon Theory Usage

**Advisor**: "Treat Shannon/entropy as motivation only; make claims fully empirical."

**Position: FULLY AGREE.**

The advisor is correct that Shannon redundancy (character-level statistical model) ≠ LLM tokenization cost. RESEARCH.md already has caveats ("efficiency claims are hypotheses pending benchmarking") but the narrative could be tighter.

**Concrete actions**:
1. Move Shannon/entropy to "Motivation" section, not "Evidence"
2. Add explicit paragraph: "Shannon redundancy measures predictability under a character-level statistical model. LLM tokenization cost depends on subword encoding (BPE/SentencePiece), vocabulary composition, and model-specific tokenizer design. These are related but distinct phenomena. We use information-theoretic redundancy as motivation, not proof, for the efficiency hypothesis."
3. Ensure all Section 1 claims are labeled clearly as motivation, not evidence.

**Priority**: MEDIUM. Important for any publication but doesn't affect experiments.
**Timing**: Before writing the paper.

---

## Point 6: Scope Control / Paper Split

**Advisor**: Split into 3 papers: (A) benchmarking comparison, (B) spec/implementation, (C) MassGen ecological validity.

**Position: AGREE with the decomposition.**

This is sensible scope management:
- **Paper A** is the highest-priority deliverable and most publishable. It's the empirical comparison.
- **Paper B** (spec + tooling) is best as an arXiv tech report / OSS artifact. It provides the foundation for Paper A but isn't independently publishable at a top venue.
- **Paper C** (MassGen) is already correctly deferred per MASSGEN_ADDENDUM.md.

**One modification**: Paper A should include enough of the spec to be self-contained (a compact 1-page summary), not require reading Paper B as a prerequisite.

**Priority**: LOW for now (it's a writing decision, not an experimental one).
**Timing**: After Exp 1 results are in and we know the story.

---

## Point 7: Spec Gaps

**Advisor**: Variable scope semantics, canonicalization rules for Tier 3 signatures, "formal semantics" overclaim.

**Position: AGREE on scoping, DISAGREE on urgency.**

Per Appendix C:
- **Variable scope** (Gap #2, Medium): Currently informal. For the experiments, variables appear only in single-message contexts. This doesn't affect Exp 0-5.
- **Canonicalization for Tier 3**: The experiments only test Tier 1 compliance. Tier 3 features (sig, authz) are not in scope for the current evaluation.
- **"Formal semantics" claim**: The spec says precondition/effect tables, not modal logic. We should be explicit: "explicit intent labeling with operational pre/postconditions" rather than "formal semantics in the FIPA sense."

**Concrete actions**:
1. Soften language in spec: "precondition/effect specifications" not "formal semantics"
2. Add a sentence to the paper: "Tier 3 (production) features including canonicalization and cryptographic signatures are defined but not evaluated in this study"
3. Defer variable scope formalization to a post-publication spec revision

**Priority**: LOW for experiments, MEDIUM for paper.
**Timing**: Before publication.

---

## Point 8: Reduced LLM Judge Reliance

**Advisor**: "The more you can make automatic scoring primary, the stronger."

**Position: AGREE in principle, but our current design is defensible.**

Our Exp 1 design uses LLM judges for semantic element scoring (DEVIATION.md). This is because the task is inherently semantic — "does this output express the concept of X?" — which is hard to automate for free-form English conditions.

However, we can increase objectivity by:
1. Making the strict validators (Point 3) do as much automatic scoring as possible
2. Using LLM judges only for the semantic element presence that can't be automated
3. Reporting both automatic metrics (token count, parse success, structural checks) and LLM-judged metrics (element presence) separately
4. Using the human validation subset (30 items) to anchor the LLM scores

**The key insight**: For AXON and JSON FC, element extraction CAN be largely automated (parse the output, check for required fields). For English conditions, it cannot. This asymmetry in measurability is itself an interesting finding worth reporting.

**Priority**: MEDIUM. Partially addressed by Point 3 (strict validators).
**Timing**: Now (validators) + paper writing (reporting strategy).

---

## Point 9: AXON ↔ JSON Bridge

**Advisor**: "Build the bridge. Fastest path to real adoption."

**Position: AGREE on value, DISAGREE on timing.**

A bidirectional AXON ↔ JSON converter would:
- Demonstrate semantic equivalence (useful for evaluation)
- Enable gradual adoption (AXON internally, JSON externally)
- Serve as a practical tool for the research community

But building it NOW would be scope creep. It's an engineering deliverable, not a research one.

**Concrete actions**:
1. Define the mapping formally (AXON performatives ↔ JSON tool-calling structure)
2. Implement after experiments are done, as a companion artifact
3. Mention the mapping in the paper as evidence that AXON is not a walled garden

**Priority**: LOW for current research. HIGH for adoption later.
**Timing**: Post-experiments.

---

## Point 10: Real-World Feasibility Framing

**Advisor**: "Feasible for closed ecosystems" but "hard as a broadly adopted cross-org standard."

**Position: FULLY AGREE. This is realistic and we should own it.**

The paper should explicitly state: "AXON is evaluated as an internal message format for controlled multi-agent systems, not as a candidate for cross-organization standardization." This is both honest and strategically smart — it avoids the "but will anyone adopt it?" reviewer objection.

**Priority**: LOW (framing decision for the paper).
**Timing**: Paper writing.

---

## Summary: Priority-Ordered Action Plan

### Do NOW (before Exp 1 scoring)
1. **Build strict validators for all conditions** (Point 3) — CRITICAL
2. **Add validator asymmetry documentation to Exp 0 results** (Point 3)

### Do in parallel with Exp 1 scoring
3. **Add IETF draft to RESEARCH.md** (Point 2)
4. **Prepare gold canonical representations for 30-item human validation subset** (Point 4)
5. **Soften "formal semantics" language in spec** (Point 7)

### Do before writing the paper
6. **Reframe positioning: empirical comparison, not new language** (Point 1)
7. **Tighten Shannon/entropy claims to motivation only** (Point 5)
8. **Add comparison table: AXON vs TOON vs LACP vs IETF** (Point 2)
9. **Decide paper split** (Point 6)

### Do post-experiments
10. **Build AXON ↔ JSON converter** (Point 9)
11. **Formalize variable scope if needed** (Point 7)

### Single most impactful action RIGHT NOW
**Build strict validators for all 6 conditions.** This fixes the most critical methodological weakness, strengthens both Exp 0 reporting and Exp 1 design, and directly addresses what the advisor says will "get attacked hard in peer review."
