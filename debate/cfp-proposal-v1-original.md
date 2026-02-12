# CFP Proposal v1 (Original Draft)

## Title
Adversarial AI Review: What Happens When You Make Claude and Codex Critique Each Other's Work

## Abstract
What if you used a second AI model not to generate code, but to systematically attack what the first model built? We developed a structured adversarial review protocol — multi-round debates between Claude and Codex with forced concessions and documented outcomes. Across six debates on a language design project, cross-model review surfaced 12 confirmed bugs and 6 missing features that self-review missed. This talk walks through the protocol, shows real examples of what it catches, and shares a reusable template you can adapt for your own projects.

## Description
Most teams using AI for development rely on a single model's judgment. But LLMs have systematic blind spots, and self-review (asking the same model to critique its own output) tends to confirm rather than challenge. We wanted to know: does structured adversarial review between different models actually catch more issues?

We built a multi-round debate protocol where Claude authors an artifact (spec section, experiment design, research claim) and Codex critiques it — with explicit rules: acknowledge strengths before attacking, ground critique in evidence, force concessions on both sides, and log every point with classification and severity.

Over six debates on a real project (designing AXON, an agent communication protocol), this process surfaced:

- 12 confirmed parser bugs missed by the authoring model
- 6 missing language features
- ~115 total critique points, ~85% resolved
- Multiple cases where the reviewing model caught issues the authoring model defended incorrectly

This is pilot evidence from one project, not proof of general superiority. But the protocol itself is model-agnostic and immediately reusable. I'll share the template, walk through a real debate excerpt showing how a bug was caught, and discuss where this approach breaks down.

**This talk is not about the specific project.** It's about a reliability pattern: using AI agents adversarially, with structure, to stress-test AI-generated artifacts before they ship.

## Takeaways
1. A concrete, reusable protocol for structured cross-model adversarial review
2. Real examples of defect classes that cross-model review catches (and self-review misses)
3. Practical limitations: when this adds value vs. when it's overhead
4. A template you can adapt for your team's AI-assisted development workflow

## Format
Lightning talk, 10 minutes. No slides-only — includes annotated walkthrough of a real debate excerpt showing bug discovery.

## Speaker Bio
[placeholder]
