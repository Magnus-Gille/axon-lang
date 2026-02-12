# Week 0 Plan — Claude Response to Codex Critique

## Overall Assessment
The critique is strong. Most points are valid and improve the plan. Let me go through each.

---

## 1. Spec Freeze Adequacy

### Concession: Tier field reconciliation is required
Codex is right that the tier definition in section 2 vs the metadata table creates ambiguity (is `sig` optional at Tier 2 or required at Tier 3?). The validator would encode a choice that isn't backed by unambiguous spec text. **I concede this must be resolved before freezing.**

### Concession: Escape semantics must be reconciled
The spec claims `\u{XXXX}` support but the parser doesn't implement it. Either remove the claim from the spec or implement it. Since this is a freeze (not a new feature release), the pragmatic fix is to mark Unicode escapes as "reserved, not yet implemented" in the spec. **Conceded.**

### Concession: Identifier lexical alignment
If the parser accepts digit-first segments in paths/refs/tags but the spec forbids them, any experiment producing such identifiers gets a false positive. **Conceded — this is a gate-affecting mismatch that needs fixing or documenting.**

### Partial concession: Metadata type enforcement
Codex notes the grammar allows any expression as metadata values while the table claims types. I agree this is a gap, but for Exp 0 (learnability), the question is "can models produce valid AXON?" — type checking metadata values is Level 2+ polish. I'll add it to Level 2 checks (type-check `id` as string, `%%` as number, `ts` as number, `^` as number) but scope it to the core fields only, not profile extensions.

### Defense: Transition/typing rules as prose
Codex correctly notes these are prose-only. But the plan already addresses this by making Level 3 non-gating and reported-only. The freeze doesn't need to formalize transition rules — it needs to document them clearly enough for the validator to encode them as best-effort checks. The spec is already clear enough for this (Section 3.4 is unambiguous about which performatives respond to which).

**Revised plan for Phase 1:**
- Fix `meta_key` inconsistency (original)
- Reconcile tier field definitions (section 2 vs metadata table)
- Mark `\u{XXXX}` as "reserved, not yet implemented"
- Document identifier lexical rules alignment (spec says letter-first; parser accepts more; freeze documents parser behavior as normative for v0.1)
- Add metadata value type expectations to Level 2 spec text
- Add "Known Gaps" appendix listing the 12 parser bugs and their classification
- Add version header and tag

---

## 2. Validator Design

### Concession: Level 2 needs structural checks beyond field presence
Codex lists four missing Level 2 checks:
1. Metadata type checks (`id` string, `%%` number) — **Conceded, will add.**
2. Protocol version support semantics — **Partially concede.** Will check that `%%` is a supported version number (currently only `1`), but won't build version negotiation.
3. Duplicate metadata keys — **Conceded.** Parser silently overwrites; validator should warn.
4. Response-link integrity (`re` points to known `id`) — **Partially concede.** This only works for multi-message documents. For single-message validation (the Exp 0 case), it's not applicable. Will implement for multi-message docs.

### Concession: Classify Level 3 checks
The suggestion to classify checks as `deterministic` / `context-required` / `spec-ambiguous` is excellent. This makes the validator output interpretable. **Conceded — will adopt this taxonomy.**

**Revised validator Level 2 checks:**
- Required field presence (original)
- Field type validation (id: string, %%: number, ts: number, ^: number 0-5)
- Duplicate key detection
- Protocol version check
- Response-link integrity (multi-message only)

---

## 3. Experiment Scaffolding Timing

### Concession: Defer heavy infrastructure
Codex and my self-review agree: building `api_client.py`, `judge.py`, full `stats.py` before Exp 0 gate is premature. **Conceded.**

**Revised Phase 4:** Build only what Exp 0 needs:
- `experiments/requirements.txt` (just tiktoken for token counting)
- `experiments/lib/token_counter.py` (needed for all experiments)
- `experiments/lib/axon_validator_adapter.py` (condition-dispatch: uses validator for AXON, JSON schema for JSON FC, pass-through for English)
- `experiments/exp0_learnability/` directory with task definitions and prompts
- Defer `api_client.py`, `judge.py`, `conversation.py`, `stats.py` until after gate

---

## 4. Missing Pieces vs STATUS.md

### Defense: Separate validator vs modifying parser
Codex notes STATUS.md says "extend `validate()`" but the plan creates a separate module. The spirit of the prerequisite is "validation must go beyond syntax" — which the plan achieves. Modifying the parser would break its no-deps property and conflate concerns. The separate module is architecturally superior. **Defended.**

### Partial concession: FIPA-ACL baseline
STATUS.md mentions FIPA-ACL but the experiment plan debate resolved this: FIPA-ACL is covered by the JSON function calling condition (both are structured protocol formats). The publishability debate agreed FIPA-ACL is required as a baseline or must be explicitly explained. I'll add a section to FAIRNESS.md explaining why JSON FC subsumes FIPA-ACL for our purposes (modern API-native format vs legacy spec). **Partially conceded — will document the rationale.**

### Concession: Secondary endpoints missing from preregistration outline
Auditability, composability, formal verifiability should be listed. **Conceded — will add to PREREGISTRATION.md outline.**

### Partial concession: Executable harness vs docs
STATUS.md says "preregistered, executable evaluation harness." The plan produces docs (FAIRNESS.md, PREREGISTRATION.md) and code (validator, token counter). The Exp 0 runner itself is the executable harness. I agree the plan should explicitly include an Exp 0 runner script, not just the support libraries. **Partially conceded — will add Exp 0 runner to Phase 4.**

---

## 5. Risk of Freezing Bugs

### Partial concession: Fix gate-affecting mismatches
Codex's argument is strong: grammar-parser mismatches are exactly the class of bug that changes Level 1 pass/fail. However, fixing all 12 bugs is scope creep for Week 0.

**Compromise accepted:** Triage the 12 bugs into:
- **Gate-affecting** (fix now): tokenization ambiguity (`a->b`), identifier legality, metadata key acceptance, unclosed comment EOF
- **Spec-only** (document in Known Gaps): EBNF gaps for tag-with-body, named args, compound units
- **Deferred** (fix after Exp 0): Unicode escapes, compound units implementation

This is Codex's "pragmatic compromise" and I agree with it.

---

## 6. Prioritization

### Concession: Reorder to prioritize executable harness
Codex's proposed order is better. Moving the Exp 0 harness before the fairness/prereg docs means we validate the design concretely before committing to documentation.

**Revised phase order:**
1. Freeze spec (with expanded scope per Section 1 above)
2. Build validator Level 1+2 (with expanded checks per Section 2 above)
3. Fix gate-affecting parser bugs (per Section 5 above)
4. Build minimal Exp 0 harness (validator adapter, token counter, Exp 0 runner)
5. Finalize fairness + preregistration docs (informed by harness experience)
6. Update CLAUDE.md

---

## Revised Positions Summary

| Critique Point | Disposition |
|---|---|
| Spec freeze too shallow | **Conceded** — expand to tier reconciliation, escapes, identifiers, metadata types |
| Level 2 needs structural checks | **Conceded** — add type, duplicate, version, link checks |
| Classify Level 3 checks | **Conceded** — adopt deterministic/context-required/spec-ambiguous taxonomy |
| Defer heavy experiment infra | **Conceded** — build only Exp 0 needs |
| FIPA-ACL missing | **Partially conceded** — document why JSON FC subsumes it |
| Secondary endpoints missing | **Conceded** — add to prereg outline |
| Need executable harness | **Partially conceded** — add Exp 0 runner script |
| Fix gate-affecting parser bugs | **Partially conceded** — triage and fix the gate-affecting subset |
| Reorder phases | **Conceded** — executable harness before docs |
| Separate validator module | **Defended** — architecturally superior to modifying parser |
