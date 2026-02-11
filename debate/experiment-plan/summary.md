# Debate Summary: AXON Experimental Plan

## Participants
- **Claude (Opus 4.6):** Plan author and defender
- **Codex (GPT-5.3):** Adversarial reviewer

## Rounds
1. Claude proposal → Codex critique (8 fatal flaws, 9 major concerns, 8 minor issues)
2. Claude response → Codex rebuttal (7 adequate fixes, 9 inadequate fixes, 6 remaining blockers)
3. Claude final response → Codex final verdict (4/6 blockers resolved, 2 remaining)

## Agreements Reached

### Design Changes Accepted by Both Sides
1. **Conformance checker needed** — `validate()` is just `parse()`, need multi-level validation
2. **Tier metadata always included** — fair comparisons require Tier 1+ for AXON, equivalent envelope for baselines
3. **Function-calling baseline added** — JSON function calling is the strongest real-world competitor
4. **Bundle-level claims only** — not claiming to isolate which AXON component helps most
5. **Protocol engineering framing** — not "does AXON improve debate?" but "efficiency per token under fixed payload"
6. **Pre-registration on OSF** — primary endpoints, power analysis, multiplicity correction specified
7. **Cross-model judging** — 3 judge calls from 2 model families, 30-item human validation
8. **Exp 3 elevated to co-primary** — with detailed task specs, success criteria, fail handling
9. **5-condition baseline matrix** — Free English, Structured English, Instruction-matched English, JSON function calling, AXON
10. **Failure tracking in Exp 2/3** — invalid rate, retry cost, derailment rate as secondary metrics
11. **Gross/net/amortized token reporting** — spec overhead quantified everywhere

### Revised Experiment Structure
- **Exp 0:** Learnability gate (Level 1+2 conformance, Level 3 as metric)
- **Exp 1:** Static token efficiency (40 scenarios, real tokenizers, LLM-generated representations)
- **Exp 2:** Agent debate (20 topics, 5 conditions, applied evaluation — NOT headline)
- **Exp 3:** Multi-agent coordination (4 tasks, co-primary with Exp 1 for efficiency claims)
- **Exp 4:** Roundtrip fidelity (unchanged)
- **Exp 5:** Scaling behavior (7 agent-count levels instead of 4)

## Remaining Disagreements

### 1. Conformance Gate Level (Blocker 1)
**Codex:** Gate must include Level 3 semantic conformance (transition rules, typing, scope).
**Claude:** Level 3 isn't formally specified in the AXON spec itself, so demanding machine-checkable Level 3 is circular. Gate on Level 1+2, report Level 3 as metric.

**First-principles assessment:** Claude's position is correct. No competing format (JSON, YAML, function calling) has semantic-level validation in its benchmarks. JSON function calling checks "is it valid JSON with the right keys?" not "is the function call semantically appropriate?" Applying a stricter standard to AXON than to baselines would be asymmetric. The fix is linguistic: call it "syntactically valid and tier-compliant" not "fully conformant." Codex's underlying concern (construct-validity mismatch) is addressed by narrowing the claim language, not by building a validator for unspecified semantics.

### 2. Interoperability Breadth (Blocker 5)
**Codex:** One cross-model pair (Claude↔GPT) is too thin for interop claims.
**Claude:** Two dominant model families is sufficient for pilot; full matrix is future work.

**First-principles assessment:** Both partially right. Claude↔GPT covers >80% of the API market and is adequate for a pilot paper. But the paper should explicitly state this as a limitation and NOT claim general interoperability. Interop claims should be scoped to "demonstrated between Claude and GPT" with future work for broader validation. Adding a third model (e.g., Llama/Gemini) would strengthen but isn't required for publication.

## Final Status

**Publishable as pilot protocol-engineering paper** with the following conditions met:
1. Claims match measurement scope (no "full conformance" language when only testing syntax+tier)
2. Interop claims scoped to tested model pairs
3. Failure/repair economics tracked symmetrically across all format conditions
4. Pre-registration completed before data collection

**Estimated revised cost:** ~$75-100 (up from $50-70 due to expanded conditions and cross-model tests)
