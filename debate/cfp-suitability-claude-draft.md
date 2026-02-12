# Should We Submit to Agentic Dev Days 2026 Stockholm?

**Claude's Position: Yes, with caveats — submit both talks, but frame them honestly as exploration, not results.**

## The Venue

Agentic Dev Days is a developer-focused conference about agentic AI in Stockholm. This is not an academic venue — it's practitioners building agent systems. The CFP accepts lightning talks and 30-minute talks.

## What We Have

### Track A — AXON Language
- A fully specified language for agent-to-agent communication (EBNF grammar, 20 performatives, 3 compliance tiers)
- Working reference parser (933 lines, pure Python)
- 49 example messages across real-world scenarios (CI/CD, incident response, fleet coordination)
- 18KB research document grounding the design in 20+ sources
- 6-experiment validation plan (designed, not executed)
- Pilot data: ~66% token reduction in 8 hand-crafted examples (illustrative only)
- **No empirical validation yet**

### Track B — Adversarial Methodology
- Structured Claude↔Codex adversarial review process
- ~115 critique points raised, ~85% resolved
- 12 confirmed parser bugs found through cross-model review
- 6 missing language features identified
- Protocol for systematic cross-model review documented

## My Assessment: Submit, Framed Honestly

### Why it fits this venue

1. **Topical relevance is high.** Agent-to-agent communication is a live problem for anyone building multi-agent systems. MCP and function calling handle agent-to-tool communication, but agent-to-agent coordination protocols are still an open space. AXON directly addresses this gap.

2. **Dev conferences welcome exploration.** Unlike academic venues that require validated results, dev conferences routinely feature talks about "here's a problem we're exploring" and "here's what we built to investigate it." The audience wants to think about the problem space, not just consume proven results.

3. **The demo is compelling.** A working parser + live examples of agent messages is tangible. Comparing `QRY(@a>@b): status(@web-server)` to the equivalent English + function calling makes the idea immediately graspable. Five minutes of live parsing would land well.

4. **The adversarial methodology angle is novel and practical.** Using structured Claude↔Codex debates to stress-test design decisions is immediately applicable to any developer's workflow. This is a "take this home and use it Monday" kind of talk.

5. **Stockholm audience.** Sweden has a strong AI/developer community. A local talk about a novel approach to a real problem is the kind of thing dev conferences exist for.

### Why I'm cautious

1. **No empirical results.** We cannot claim AXON is better than alternatives. We can only say "here's the hypothesis, here's the design, here's the plan to test it." This limits the strength of any Track A talk.

2. **The "just use JSON" challenge.** Sophisticated attendees will immediately ask: "Why not just use structured JSON / function calling / MCP?" We need a good answer. Our honest answer is "we don't know yet — that's what the experiments are for" which is fine for a dev talk but limits the persuasive force.

3. **Risk of overclaiming.** The temptation to present pilot data as evidence is real. Any talk must be disciplined about what's established vs hypothetical.

## Proposed Talks

### Lightning Talk (5–10 min): "AXON: What If Agents Had Their Own Language?"
- **Frame:** Provocative question, not a solution pitch
- **Content:** The problem (agent comms are verbose/ambiguous) → the idea (speech-act protocol) → 3 live examples → "here's what we don't know yet" → call to action (collaborate/critique)
- **Value prop:** Makes people think about a problem they might not have considered
- **Risk level:** Low — it's a thought-provoking intro, not a claim

### 30-Minute Talk: "Designing Agent Protocols with Adversarial AI Review"
- **Frame:** The methodology story, with AXON as the case study
- **Content:**
  1. The problem: designing agent communication protocols (5 min)
  2. AXON design walkthrough — what we built and why (8 min)
  3. The adversarial process: how Claude↔Codex debate improved the design (10 min)
     - 12 bugs found, 6 missing features identified
     - Example: how Codex's critique of operator precedence led to spec changes
     - Live demo: run a debate on a new design question
  4. Open questions and experiment plan (5 min)
  5. Q&A (2 min)
- **Value prop:** Two takeaways — (1) a concrete approach to agent protocol design, (2) a reusable methodology for AI-assisted design review
- **Risk level:** Medium — requires honest framing about what's validated and what isn't

## Conclusion

The fit is good for a dev conference. The key is honest framing: "here's an open problem, here's our approach, here's how we stress-tested it, here's what we still need to prove." Dev audiences respect intellectual honesty and novel approaches more than polished results.
