# Codex Critique: CFP Proposal (Agentic Dev Days 2026)

## Executive Assessment
The draft is close, but it still leans slightly toward "models fighting" spectacle instead of "reliability method with evidence." For a reviewer triaging many submissions, acceptance odds go up if the first two lines foreground concrete outcomes and transferable workflow.

## 1) Title
Current title:
`Adversarial AI Review: What Happens When You Make Claude and Codex Critique Each Other's Work`

Assessment:
- Strong topic signal in the first phrase.
- Weak second half: long, familiar "What Happens When..." framing, and slightly gimmicky.
- Naming vendors/models in the title makes the talk sound tool-specific instead of method-specific.

Recommended replacement titles (pick one):
1. `Adversarial LLM Review as a Reliability Pattern: 12 Bugs from 6 Debates`
2. `Beyond Self-Review: A Cross-Model Critique Protocol for Agentic Development`
3. `Structured AI Opposition: A Practical Workflow for Finding Spec Bugs Early`

## 2) Abstract
Assessment:
- Claude self-review is right: current abstract buries the best evidence too late.
- Opening with a rhetorical question is weaker than opening with the measured result.
- `~85% resolved` is noisy unless resolution semantics are defined.

Suggested rewritten abstract:

```markdown
As agentic development moves from demos to production, verification is becoming the bottleneck. In six structured cross-model debates on a real language-design project, adversarial review uncovered 12 confirmed parser bugs and 6 missing features that self-review missed. This lightning talk presents a lightweight protocol: one model authors, another critiques with evidence, both must concede or defend, and each issue is logged with severity and disposition (`accept`/`reject`/`defer`). Scope is explicit: this is practitioner pilot data (n=1), not a general benchmark. You’ll see an annotated replay of one real bug-discovery sequence and leave with a reusable template for when adversarial review improves reliability versus when it is just overhead.
```

## 3) Description (Reviewer Field)
Assessment:
- Current version is solid but too long for a 10-minute talk submission.
- You need one short problem statement, one short method/result block, one short "what audience gets" block.

Suggested rewritten description:

```markdown
Teams increasingly ship AI-generated specs and code, but self-review by the same model often preserves blind spots. This talk presents a structured adversarial review workflow for AI-assisted engineering.

Case study: six debates from AXON (an agent communication protocol). Process: one model authors an artifact, a second model critiques with evidence, both sides must concede or defend, and a human logs each issue by severity and disposition. Result: 12 confirmed parser bugs and 6 missing features surfaced before implementation.

I’ll show an annotated replay of one debate segment that produced a confirmed bug, then share a copyable protocol and adoption rubric. Scope is explicit: n=1 practitioner pilot, no universal claims.
```

Trim/remove:
- Remove `~115 total critique points, ~85% resolved` unless you define exactly what "resolved" means.
- Remove defensive phrasing like `No slides-only`.

## 4) Takeaways
Assessment:
- Current takeaways are decent but still generic.
- Reviewers respond better to "artifact + decision rule + failure mode" specificity.

Suggested replacement takeaways:
1. `A copyable adversarial-review protocol (roles, prompts, concession rules, and issue log schema).`
2. `Three defect classes this method exposed in practice (parser edge cases, missing language features, unsupported claims).`
3. `A decision rubric for when adversarial review is worth the cost vs when standard review is enough.`
4. `A minimal audit trail format teams can use to justify accept/reject/defer decisions on AI-generated output.`

## 5) Overall Positioning
Does it currently read as serious practitioner talk or gimmick?
- Current: mostly serious, but title + opening sentence still invite a gimmick read.
- Desired: reliability pattern talk with constrained evidence and operational guidance.

One change that most improves acceptance odds:
- **Lead with the concrete result in line 1 and remove spectacle framing from the title.**
- If reviewers remember one thing, it should be: `12 confirmed bugs found via structured cross-model review`, not `Claude vs Codex`.

## 6) What’s Missing (Likely Reviewer Questions)
Add these explicitly:
1. Definition of evidence quality.
   Suggested text: `Confirmed bug = reproducible parser failure or ambiguity validated by human review and fixed in grammar/spec.`
2. Audience targeting.
   Suggested text: `For engineers/tech leads already using LLMs for code/spec work; no formal methods background required.`
3. 10-minute structure signal.
   Suggested text: `2 min problem, 3 min protocol, 3 min annotated bug replay, 2 min adoption rubric.`
4. Deliverable clarity.
   Suggested text: `Attendees get a one-page protocol checklist and issue-log template.`
5. Speaker credibility (bio cannot be placeholder in submission).
   Suggested text template: `Magnus is a Stockholm-based engineer building AI-assisted developer workflows, with hands-on results from multi-model review experiments in production-like language design work.`

## Claude Self-Review: Valid vs Overthinking
1. `Title might be too cute`  
Verdict: **Valid**.  
Fix: Use a method-first title; move model names to body text.

2. `Abstract buries the lede`  
Verdict: **Valid**.  
Fix: Put `12 confirmed bugs + 6 missing features` in sentence one or two.

3. ``~85% resolved` is meaningless`  
Verdict: **Valid**.  
Fix: Either define resolution states or remove the number.

4. `No clear why-now signal`  
Verdict: **Partly valid**.  
Fix: Add one sentence about 2026 context (`agentic workflows are shipping, verification is the bottleneck`), but keep it brief.

5. `Description too long for lightning CFP`  
Verdict: **Valid**.  
Fix: Compress to ~120-170 words with clear structure.

6. `Speaker bio is empty`  
Verdict: **Valid and blocking**.  
Fix: Submit with concrete credibility evidence, even if short.

7. ``Why This Fits` section might not be needed`  
Verdict: **Mostly overthinking**.  
Fix: Keep this content only if the CFP form lacks a dedicated relevance field; otherwise map it into the form’s specific prompts.

8. ``No slides-only` sounds defensive`  
Verdict: **Valid (minor)**.  
Fix: Replace with neutral format line (`Includes annotated replay of a real debate excerpt`).

## Submission-Ready Copy (Recommended)
Title:
`Adversarial LLM Review as a Reliability Pattern: 12 Bugs from 6 Debates`

Abstract:
```markdown
As agentic development moves from demos to production, verification is becoming the bottleneck. In six structured cross-model debates on a real language-design project, adversarial review uncovered 12 confirmed parser bugs and 6 missing features that self-review missed. This lightning talk presents a lightweight protocol: one model authors, another critiques with evidence, both must concede or defend, and each issue is logged with severity and disposition (`accept`/`reject`/`defer`). Scope is explicit: this is practitioner pilot data (n=1), not a general benchmark. You’ll see an annotated replay of one real bug-discovery sequence and leave with a reusable template for when adversarial review improves reliability versus when it is just overhead.
```

Description:
```markdown
Teams increasingly ship AI-generated specs and code, but self-review by the same model often preserves blind spots. This talk presents a structured adversarial review workflow for AI-assisted engineering.

Case study: six debates from AXON (an agent communication protocol). Process: one model authors an artifact, a second model critiques with evidence, both sides must concede or defend, and a human logs each issue by severity and disposition. Result: 12 confirmed parser bugs and 6 missing features surfaced before implementation.

I’ll show an annotated replay of one debate segment that produced a confirmed bug, then share a copyable protocol and adoption rubric. Scope is explicit: n=1 practitioner pilot, no universal claims.
```

Takeaways:
1. `A copyable adversarial-review protocol (roles, prompts, concession rules, and issue log schema).`
2. `Defect classes this method exposed that self-review missed in practice.`
3. `A decision rubric for when to use this workflow vs skip it as overhead.`
4. `A lightweight audit trail format for AI-assisted development decisions.`
