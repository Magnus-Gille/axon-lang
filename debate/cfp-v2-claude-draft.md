# CFP v2 — Claude's Improved Proposals

## Assessment of Current State

Since the previous CFP debate, the evidence base has changed dramatically:
- **Exp 0** (learnability): PASS on all 3 models — LLMs can learn AXON from a spec
- **Exp 1** (token efficiency): 486 scored outputs, statistically significant results — AXON beats JSON FC by ~32% (p < 0.001 in mixed model), ties English on efficiency but with zero failures vs 11.1% failure rate for free English

This changes the calculus for Talk 1. The previous debate concluded "30 minutes requires at least one executed benchmark." We now have two. The 30-minute talk is no longer premature — it has empirical backing.

## Talk 1 — Revised (30 minutes)

### Problems with the current version

1. **Missing the data.** The abstract talks about information theory and side-by-side comparisons but never mentions that we actually RAN the experiments. This is the single biggest missed opportunity. A practitioner talk with benchmarks is 10x more credible than one with theory alone.

2. **Shannon claim is oversimplified.** "Shannon proved it's 50–75% redundant" — he estimated English redundancy, not specifically agent communication redundancy. The claim isn't wrong but it's imprecise enough for a skeptic to dismiss.

3. **"20 speech-act performatives" is spec jargon.** Conference attendees don't care about performative counts. They care about what it does for them.

4. **"come poke holes" is good but undercut by "draft v0.1".** The honest framing is right, but signaling "very early" immediately after asking people to invest 30 minutes creates tension. Better to frame it as "tested, early-stage."

5. **No takeaways structure.** The abstract says what attendees will learn but doesn't promise concrete deliverables.

6. **Internal notes are strong but could be stronger.** The prompting champion credential is excellent and unique. The enterprise clients list is impressive.

### Revised Talk 1

**Title:** What Happens When You Stop Making Agents Talk Like Humans

**Abstract:** Every multi-agent framework routes tasks through English or JSON — and pays the cost in tokens, parsing failures, and ambiguity. We benchmarked six communication formats (free English, structured English, JSON function calling, FIPA-ACL, and AXON — a purpose-built agent protocol) across three LLMs and 486 scored outputs. AXON used 32% fewer tokens than JSON function calling (p < 0.001), matched English on compactness, and had zero complete failures where free English failed 11% of the time.

This talk walks through why natural language and JSON break as agent protocols, how speech-act theory and information theory inform a better design, and what the benchmarks actually show — including where AXON doesn't win. I'll do live side-by-side comparisons, demonstrate the reference parser, and share the open-source toolkit (MIT). AXON is early-stage (v0.1) but empirically tested. Come stress-test the claims.

**Internal Notes:** Sweden's first national AI prompting champion (2025, 300+ participants). Regular speaker on AI strategy and agentic systems for enterprise audiences including IKEA, Saab, Epidemic Sound, and Koenigsegg. 15+ years enterprise experience in data architecture and AI, including Product Owner of AI Enablement at Scania/Traton.

### Key changes:
- Lead with the benchmark data, not theory
- Specific numbers (32%, p < 0.001, 486 outputs, zero failures, 11% failure rate)
- "Including where AXON doesn't win" — builds credibility by signaling honesty
- Dropped "Shannon proved" — replaced with implicit framing ("pays the cost")
- Dropped the 20-performative spec jargon
- "Empirically tested" replaces "draft v0.1" — same honesty, better framing
- Dropped "AXON" from title — makes it about the problem, not the product

---

## Talk 2 — Revised (Lightning Talk, 10 minutes)

### Problems with the current version

1. **"approximately 85% of around 100 critique points"** — this was flagged in the previous debate as a soft claim. It should either be made precise ("87 of 103 critique points resolved") or reframed to focus on the 12 confirmed bugs, which is the hard number.

2. **"4-round adversarial debate"** — the actual protocol varies (2–4 rounds). This implies a single debate, but it was ~12 debates across the project. The number undersells the evidence base.

3. **"What if your code reviewer..."** opening — good for a blog post, risky for a 10-minute slot where every second counts. The question format delays the value proposition.

4. **Missing the experiment angle.** The methodology was used not just for bug-hunting but as part of a formal research project. That's unusual and interesting — most dev tools don't come with empirical data.

5. **"I'll share the template"** — good promise, could be more specific about what the template contains.

### Revised Talk 2

**Title:** Bug Hunting with Rival AIs: How Cross-Model Debate Found 12 Bugs Self-Review Missed

**Abstract:** I ran 12 structured adversarial debates between Claude and Codex to stress-test a language specification — parser, grammar, experiment design, and research claims. The process caught 12 confirmed bugs and surfaced 115+ critique points that neither model found through self-review alone. Each debate follows a fixed protocol: draft → self-critique → cross-model attack → concede-or-defend → human verdict.

In 10 minutes, I'll show the protocol, walk through one real bug-discovery sequence, and give you a reusable template (roles, prompts, concession rules, and issue-log schema). You'll know when adversarial debate is worth the token cost and when standard review is enough. The technique works for specs, architecture decisions, design docs — anything where blind spots cost more than extra API calls.

**Internal Notes:** The methodology was developed during a formal benchmarking study of agent communication formats (also submitted as a 30-min talk), where it was applied across 12 debates covering spec design, experiment methodology, and research claims. Sweden's first AI prompting champion (2025, 300+ participants). Regular speaker on AI strategy and agentic systems for enterprise audiences.

### Key changes:
- "12 structured debates" replaces "4-round debate" — shows breadth
- "12 confirmed bugs" and "115+ critique points" — hard numbers replace soft claims
- "that neither model found through self-review alone" — makes the value proposition explicit
- Fixed protocol steps listed upfront — shows it's systematic, not ad hoc
- Subtitle change ("How Cross-Model Debate Found 12 Bugs Self-Review Missed") — results-first
- Dropped the "What if..." rhetorical question — straight to evidence
- Internal notes strengthened with formal research context

---

## Strategic considerations

1. **The two talks complement each other.** Talk 1 is the research result. Talk 2 is the methodology that produced it. Together they tell a complete story: "here's what we found" and "here's how we verified it."

2. **If only one gets accepted**, Talk 2 (lightning) is safer. The methodology is immediately actionable for any developer. Talk 1 requires the audience to care about agent communication specifically.

3. **The internal notes should highlight the prompting championship more prominently.** It's a genuinely unique credential for an AI developer conference — nobody else at the event will have it.

4. **Both proposals are honest about limitations.** Talk 1 says "including where AXON doesn't win." Talk 2 scopes to a specific methodology without universal claims. This is the right tone for a dev conference.
