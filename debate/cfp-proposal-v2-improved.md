# CFP Proposal v2 (Post-Debate)

## Title
Adversarial LLM Review as a Reliability Pattern: 12 Bugs from 6 Debates

## Abstract
As agentic development moves from demos to production, verification is becoming the bottleneck. In six structured cross-model debates on a real language-design project, adversarial review uncovered 12 confirmed parser bugs and 6 missing features that self-review missed. This lightning talk presents a lightweight protocol: one model authors, another critiques with evidence, both must concede or defend, and each issue is logged with severity and disposition (accept/reject/defer). Scope is explicit: this is practitioner pilot data (n=1), not a general benchmark. You'll see an annotated replay of one real bug-discovery sequence and leave with a reusable template for when adversarial review improves reliability versus when it is just overhead.

## Description
Teams increasingly ship AI-generated specs and code, but self-review by the same model often preserves blind spots. This talk presents a structured adversarial review workflow for AI-assisted engineering.

Case study: six debates from AXON (an agent communication protocol). In this pilot, the two models were Claude (author role) and Codex (review role). Process: one model authors an artifact, a second model critiques with evidence, both sides must concede or defend, and a human logs each issue by severity and disposition. Result: 12 confirmed parser bugs and 6 missing features surfaced before implementation. Confirmed bug means a reproducible parser failure or ambiguity validated by human review and fixed in the grammar/spec.

I'll show an annotated replay of one debate segment that produced a confirmed bug, then share a copyable protocol and adoption rubric. Scope is explicit: n=1 practitioner pilot, no universal claims.

## Takeaways
1. A copyable adversarial-review protocol (roles, prompts, concession rules, and issue-log schema).
2. Three defect classes this method exposed in practice (parser edge cases, missing language features, unsupported claims).
3. A decision rubric for when adversarial review is worth the cost versus when standard review is enough.
4. A one-page template pack: protocol checklist plus issue-log template with accept/reject/defer states.

## Audience
Engineers and tech leads already using LLMs for code/spec work who need stronger verification workflows. No formal methods background required.

## Format
Lightning talk, 10 minutes.
1. 2 min: problem framing (self-review blind spots in agentic workflows)
2. 3 min: protocol walkthrough
3. 3 min: annotated bug-discovery replay
4. 2 min: adoption rubric and template handoff

## Speaker Bio
[Name] is a Stockholm-based [role] at [company/team], focused on AI-assisted developer workflows and reliability patterns for agentic systems. They have led hands-on multi-model adversarial review experiments in language-design work, using structured cross-model critique to surface parser/spec defects before implementation. [Add one sentence with concrete credibility: shipped systems, publications, talks, or open-source contributions.]
