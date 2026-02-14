# Debate Summary: Senior Research Advisor Feedback

## Participants
- **Claude** (Opus 4.6): Initial response + self-review + Round 1 response
- **Codex** (GPT-5.3): Round 1 critique + Round 2 rebuttal

## Rounds
2 full rounds (draft → critique → response → rebuttal)

---

## Concessions Accepted by Both Sides

### Claude conceded (Codex accepted as genuine):
1. **Canonical semantic scoring is #1 priority** — not validator symmetry. The primary endpoint (tokens/semantic unit) depends on denominator validity.
2. **Paper A framing should be locked NOW** — "benchmarking comparison" is the active target, constraining all scope decisions.
3. **Formal semantics overclaim must be fixed immediately** — 5-minute spec edit, no reason to defer.
4. **Prereg governance discipline needed** — all scoring/validator changes must be appended as DEVIATION.md amendments.
5. **Exp 0 secondary claims need qualification** — cross-condition token comparisons are contaminated by validator asymmetry; sensitivity analysis required.
6. **AXON↔JSON canonical mapping should be defined now** — as a document, even if converter tool comes later.

### Codex conceded:
1. **LLM judges for free-form English are practically unavoidable** — automated extraction is realistic for AXON/JSON/FIPA but not for unrestricted English.
2. **Strict English validators need careful scoping** — format-policing ≠ semantic comparability.
3. **Exp 0 gate result is robust** — gate criterion (AXON ≥ 80% and ≥ JSON FC) is not sensitive to English validator changes.

---

## Defenses Accepted by Codex

1. English conditions genuinely need LLM/human judges for semantic extraction
2. Validators for English should check information content, not formatting — but boundary must be clear
3. 30-item human subset is acceptable with pre-locked expansion triggers

---

## Unresolved Issues

1. **English scoring contract underspecified**: What is machine-scored vs judge-scored for English conditions? Calibration triggers? Escalation rules? This must be locked before scoring begins.
2. **Potential circularity between strict validation and semantic scoring**: If English validators check "required information content," they blur the line between structural compliance and semantic endpoint scoring.
3. **Selective human subset expansion**: Expanding only failing conditions introduces bias without a pre-locked trigger rule.
4. **Reliability ≠ construct validity**: >90% judge agreement doesn't prove the denominator is condition-invariant.

---

## New Issues from Round 2

1. English scoring/judging contract must be frozen alongside canonical representations (Tier 1, not Tier 3)
2. Human subset expansion rules need pre-locked triggers
3. Machine-vs-judge boundary per condition must be explicit in DEVIATION amendment

---

## Final Verdict

### Claude's position:
Build canonical semantic representations → automated extractors for structured formats → LLM judges for English (validated against gold + human) → strict validators → run experiments.

### Codex's position:
Same overall direction, but **freeze the complete scoring-governance addendum first** — including the English-condition scoring contract — before any Exp 1 scoring begins.

### Agreed next step:
**Before any Exp 1 scoring, publish and freeze one unified scoring-governance addendum** that hard-locks:
- Canonical semantic representations for all 9 tasks
- Per-condition scoring contract (what is machine-scored vs judge-scored)
- English-condition extraction/judging rules
- Calibration thresholds and expansion triggers
- Reporting rules for reliability metrics

This converts the debate outcomes into defensible methodology.

---

## Revised Action Plan (Post-Debate)

### Tier 1: Do NOW (blocks Exp 1 scoring)
1. Lock Paper A framing: "Benchmarking agent communication formats"
2. Build canonical semantic representations for all 9 tasks
3. Build automated extractors for AXON, JSON FC, FIPA-ACL
4. Define per-condition scoring contract (machine vs judge boundary)
5. Define English-condition LLM-judge extraction rules with calibration triggers
6. Freeze unified scoring-governance addendum to DEVIATION.md
7. Fix "formal semantics" overclaim in spec

### Tier 2: Do NOW (parallel with Tier 1)
8. Build strict structural validators for all conditions
9. Define AXON↔JSON canonical mapping (document)
10. Run strict validators on Exp 0 data as sensitivity analysis
11. Qualify Exp 0 secondary token-efficiency claims

### Tier 3: Before Exp 1 scoring begins
12. Validate LLM judges against gold + human scores on 30-item subset
13. Add IETF draft + comparison table to RESEARCH.md
14. Restructure RESEARCH.md: lead with practical cost data, Shannon as background

### Tier 4: Paper writing
15. Reframe all positioning per Paper A
16. Build AXON↔JSON converter tool (if useful)

---

## Debate Files
- `debate/advisor-feedback-claude-draft.md` — Claude's initial 10-point response
- `debate/advisor-feedback-claude-self-review.md` — Claude's self-critique (7 weaknesses)
- `debate/advisor-feedback-codex-critique.md` — Codex Round 1 (7 critique areas)
- `debate/advisor-feedback-claude-response-1.md` — Claude's response (5 concessions, 3 partial, 3 defenses)
- `debate/advisor-feedback-codex-rebuttal-1.md` — Codex Round 2 (final verdict)
- `debate/advisor-feedback-summary.md` — This file
- `debate/advisor-feedback-critique-log.json` — Structured critique log

## Costs
| Invocation | Wall-clock time | Model version |
|------------|-----------------|---------------|
| Codex R1   | ~2 min          | gpt-5.3-codex |
| Codex R2   | ~2 min          | gpt-5.3-codex |

(CLI-based invocation via `codex exec` — subscription cost only, no per-token API charges)
