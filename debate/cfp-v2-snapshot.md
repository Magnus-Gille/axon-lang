# CFP Proposals v2 — Snapshot for Debate (2026-02-16)

These are the two proposals as submitted for adversarial review. Both are for Agentic Dev Days 2026, Stockholm.

Context for reviewers:
- Exp 0 (learnability gate): PASS on all 3 models (Codex, Haiku, Sonnet)
- Exp 1 (token efficiency): 486 outputs scored. AXON #1 at 15.4 tok/unit. ~32% better than JSON FC, ~42% fewer raw tokens. Zero complete failures. Mixed model p < 0.001 vs JSON FC/FIPA-ACL/Inst-Matched English. Not significant vs Structured English or Free English on tok/unit, but Free English has 11.1% failure rate.
- Bootstrap CIs exclude zero for AXON vs JSON FC (d = -0.43), FIPA-ACL (d = -0.33), Inst-Matched English (d = -0.24).
- Prompt overhead: AXON costs 529 tokens vs 205 for JSON FC; breakeven at ~6 messages.
- The adversarial debate methodology has produced ~115 critique points across ~12 debates.
- Speaker plans to complete more research (Exp 3 compositionality, cross-validation, human validation) before the conference.

---

## Talk 1 — Talk (30 minutes)

**Title:** AXON: What Happens When You Stop Making Agents Talk Like Humans

**Abstract:** Natural language is a terrible protocol. Shannon proved it's 50–75% redundant, and every agent framework that routes tasks through English pays the tax — in tokens, in ambiguity, in failed handoffs. AXON (Agent eXchange Optimized Notation) is a purpose-built language for agent-to-agent communication: 20 speech-act performatives, typed content, symbolic operators, and zero-ambiguity routing — designed to replace the English glue holding multi-agent systems together.

Attendees will learn why current approaches to agent communication (natural language and JSON function calling) break at scale, how information theory and speech-act semantics from linguistics inform a better alternative, and what it takes to build a language that LLMs were never trained on. I'll walk through real side-by-side comparisons of equivalent agent tasks in English, JSON, and AXON, and demonstrate the working reference parser and grammar.

This is directly relevant to anyone building multi-agent systems — whether you're wiring up CrewAI pipelines, building MCP integrations, or designing your own orchestration layer. AXON is open source (MIT) and in draft v0.1. This is a practitioner talk, not a product pitch — come poke holes.

**Internal Notes:** Sweden's first national AI prompting champion (2025, 300+ participants). Regular speaker on AI strategy and agentic systems for enterprise audiences including IKEA, Saab, Epidemic Sound, and Koenigsegg. 15+ years enterprise experience in data architecture and AI, including Product Owner of AI Enablement at Scania/Traton.

---

## Talk 2 — Lightning Talk (10 minutes)

**Title:** Bug Hunting with Rival AIs: Adversarial Multi-Model Debate as a Dev Tool

**Abstract:** What if your code reviewer and your code reviewer's worst critic were both LLMs — from different providers? I ran a structured 4-round adversarial debate between Claude Opus and Codex GPT-5.3 to stress-test a language specification, and it found 12 real bugs that neither model caught alone. The process resolved approximately 85% of around 100 critique points raised across rounds.

Attendees will learn a concrete, reusable methodology: how to structure adversarial debate between competing models, what prompt scaffolding makes it work, when it's worth the token cost vs. standard single-model review, and what types of bugs surface through model disagreement that don't surface through single-model analysis.

This is relevant for any developer using AI in their workflow. The technique is model-agnostic and works for design docs, specs, architecture decisions, or any artifact where correctness matters. I'll share the template so you can run your own debate tonight.

**Internal Notes:** The adversarial debate methodology was developed and battle-tested during the creation of the AXON language specification (also submitted as a 30-min talk). Sweden's first AI prompting champion (2025). Regular AI speaker for enterprise clients.
