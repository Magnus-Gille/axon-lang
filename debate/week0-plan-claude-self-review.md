# Week 0 Plan — Claude Self-Review

*Self-critique of the implementation plan before Codex review. Being genuinely critical.*

## Strengths
1. **Correct dependency ordering** — Spec freeze before validator before experiments is logically sound.
2. **Validator separation** — Keeping it out of `axon_parser.py` preserves the no-deps property.
3. **Level 2 as gate, Level 3 as metric** — Follows the debate-agreed compromise. Doesn't overreach.
4. **Acknowledges the 12 parser bugs** — Explicitly defers them rather than silently ignoring.

## Weaknesses I See

### W1: "Freeze the spec" is too shallow
The plan only fixes the `meta_key` inconsistency and adds a version header. But the spec has deeper issues that will bite during experiments:
- The EBNF grammar is missing compound units (`/s`, `/KB`) which are used in examples
- Performative transition rules are prose-only — the validator will encode rules that have no formal spec backing
- The "freeze" could lock in inconsistencies that force spec revisions mid-experiment, undermining the whole point of freezing

**Self-assessment:** Partially valid concern. The point of freezing is to have a stable target, not a perfect one. But we should at least document known gaps alongside the freeze.

### W2: Validator Level 3 transition checking is underspecified
The plan says "CFM/DNY only to truth-apt, ACC/REJ only to proposals" but doesn't address:
- How to handle multi-message documents where messages don't have `re` fields linking them
- Whether transition checking even makes sense for single-message validation (most examples are standalone)
- The spec's transition rules are informal — we're formalizing something that was never formally defined

**Self-assessment:** Valid. Level 3 may be mostly useless for Exp 0 since experiment tasks produce multi-turn conversations across API calls, not multi-message AXON documents. The validator sees one message at a time.

### W3: The experiment libraries are premature
Building `api_client.py`, `judge.py`, `conversation.py`, and `stats.py` as "working stubs" before even knowing if Exp 0 passes the gate is speculative. If learnability fails, none of this infrastructure gets used.

**Self-assessment:** Partially valid. Counter-argument: scaffolding is cheap, and having the interfaces defined helps clarify the experiment design. But there's a risk of building the wrong abstractions before running any experiments.

### W4: No acceptance criteria for the spec freeze
When is the spec "frozen enough"? The plan says fix meta_key and add a version header, but doesn't define what constitutes a successful freeze. What if we discover another inconsistency during validator implementation?

**Self-assessment:** Valid. Need a rule like "the freeze covers sections 1-7; appendix profiles are explicitly marked as draft."

### W5: Missing: how the validator interacts with experiment code
The plan says "experiments call the validator directly" but doesn't specify the interface. Does Exp 0 validate individual messages or complete conversations? Does it validate AXON-condition messages and skip validation for English-condition messages? The conversation manager presumably needs condition-specific validation — is that the validator's job or the experiment's?

**Self-assessment:** Valid. This is a design gap. The validator validates AXON; the experiment needs a condition-dispatch layer that uses the validator for AXON and JSON schema validation for JSON FC.

### W6: Power analysis numbers are just restated, not verified
The plan restates the power analysis from the debate (40 scenarios for Exp 1, etc.) but doesn't verify whether those numbers are still appropriate given the 5-condition design. Adding conditions changes the multiplicity correction burden.

**Self-assessment:** Minor. The preregistration doc will need to recompute this properly, but it doesn't block implementation.

## Summary
The plan is directionally correct but underspecified in three areas:
1. What exactly gets frozen vs documented-as-known-gap in the spec
2. How Level 3 validation works in practice (single message vs conversation context)
3. Whether the experiment scaffolding should wait until after Exp 0 gate passes
