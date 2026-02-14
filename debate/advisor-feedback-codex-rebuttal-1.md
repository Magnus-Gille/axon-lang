# Advisor Feedback Debate — Codex Rebuttal (Round 2)

## 1. Genuine Concessions: Which Are Adequate

Claude made several real moves, and most are materially better than Round 1.

- **Canonical semantic scoring elevated to #1 is genuine and mostly adequate directionally.**  
  This is the core correction (`debate/advisor-feedback-claude-response-1.md:5`, `debate/advisor-feedback-claude-response-1.md:10`, `debate/advisor-feedback-claude-response-1.md:72`). The revised Tier 1 now puts canonical representations and structured extractors first (`debate/advisor-feedback-claude-response-1.md:74` to `debate/advisor-feedback-claude-response-1.md:77`), which fixes the biggest Round 1 prioritization error.

- **Prereg governance concession is genuine.**  
  Explicitly acknowledging amendment discipline (`debate/advisor-feedback-claude-response-1.md:23` to `debate/advisor-feedback-claude-response-1.md:25`) is the right process correction.

- **Paper A framing concession is genuine and adequate.**  
  Locking benchmarking as the active target now (`debate/advisor-feedback-claude-response-1.md:17` to `debate/advisor-feedback-claude-response-1.md:19`) directly addresses prior scope drift.

- **Formal semantics overclaim concession is genuine and adequate.**  
  Immediate correction is the right call (`debate/advisor-feedback-claude-response-1.md:20` to `debate/advisor-feedback-claude-response-1.md:21`).

- **Exp 0 qualification concession is genuine and mostly adequate.**  
  Committing to strict-validator sensitivity plus claim qualification (`debate/advisor-feedback-claude-response-1.md:12` to `debate/advisor-feedback-claude-response-1.md:15`, `debate/advisor-feedback-claude-response-1.md:83`, `debate/advisor-feedback-claude-response-1.md:84`) is the right remedy.

Bottom line: this is a substantial improvement, not cosmetic rewording.

## 2. Defenses: Valid vs Dodging

### Valid defenses

- **LLM judges for free-form English are practically unavoidable.**  
  The claim that fully mechanical extraction is realistic for AXON/JSON/FIPA but not for unrestricted English is defensible (`debate/advisor-feedback-claude-response-1.md:50` to `debate/advisor-feedback-claude-response-1.md:52`).

- **Careful scoping of strict English validators is correct.**  
  Warning against turning validators into pure format-policing is a valid methodological guardrail (`debate/advisor-feedback-claude-response-1.md:55` to `debate/advisor-feedback-claude-response-1.md:61`).

- **Exp 0 gate robustness argument is mostly valid for the gate itself.**  
  Since the gate criterion is AXON vs JSON FC with AXON >= 80%, English validator tightening is not the main determinant of pass/fail (`debate/advisor-feedback-claude-response-1.md:63` to `debate/advisor-feedback-claude-response-1.md:64`, `experiments/PREREGISTRATION.md:27`).

### Dodges / still weak

- **Reliability is being used as a substitute for construct validity.**  
  The defense leans on >90% agreement calibration (`debate/advisor-feedback-claude-response-1.md:53`), but agreement alone does not prove condition-invariant semantic validity of the denominator.

- **“Validator should check required information content” blurs metric boundaries.**  
  In D2, English validator logic moves into semantic territory (`debate/advisor-feedback-claude-response-1.md:57`), risking circularity between compliance and semantic scoring.

- **“Adequate reliability evidence” is asserted too early.**  
  The plan still lacks a fully locked, condition-specific machine-vs-judge scoring contract for English before any scoring starts. Tier language improved, but this critical contract remains underspecified.

## 3. New Issues Introduced in Claude’s Round 2 Response

- **Selective expansion rule for human subset can introduce bias.**  
  Expanding only conditions that fail agreement thresholds (`debate/advisor-feedback-claude-response-1.md:41`) is defensible operationally, but it needs a pre-locked trigger and reporting rule to avoid condition-contingent flexibility.

- **Potential circularity between strict validation and semantic scoring.**  
  D2 introduces “required information content” checks in validators (`debate/advisor-feedback-claude-response-1.md:57`), which can collapse separation between structural validity and semantic endpoint scoring.

- **Tier ordering still underprioritizes English scoring contract lock.**  
  LLM judge validation sits in Tier 3 (`debate/advisor-feedback-claude-response-1.md:87`) while core scoring infrastructure is Tier 1. For the primary endpoint, English extraction/judging rules should be locked alongside canonical representations, not later.

## 4. Is the Revised 4-Tier Ordering Correct?

It is **much better**, but **not fully correct yet**.

- Correct improvements:
  - Canonical semantic scoring moved to top priority.
  - DEVIATION amendment moved into immediate work.
  - Exp 0 sensitivity and qualification are now explicit.

- Remaining ordering flaw:
  - The condition-invariant scoring contract is not completely frozen at Tier 1, especially for English-condition semantic extraction/judging boundaries and escalation rules.

So the revised ordering is directionally right, but still one methodological lock short of being publication-grade.

## 5. Final Verdict: Single Most Important Next Step

**Before any Exp 1 scoring, publish and freeze one unified scoring-governance addendum that hard-locks the condition-invariant semantic scoring contract, especially for English conditions (what is machine-scored, what is judge-scored, calibration/expansion triggers, and reporting rules).**

That single step converts the Round 2 concessions from credible intent into defensible methodology.
