# Talk 1 — Final (30 minutes)

**Title:** What Happens When You Stop Making Agents Talk Like Humans

**Abstract:** When agents communicate through English or JSON, teams trade off token cost, parseability, and reliability. We benchmarked six formats — free English, structured English, instruction-matched English, JSON function calling, FIPA-ACL, and AXON (a purpose-built agent protocol) — across three LLMs and 486 scored outputs. AXON averaged 15.4 tokens per semantic unit versus 22.6 for JSON function calling (~32% lower), with zero complete failures. English variants were similarly compact when outputs succeeded, but free English failed completely on 11% of attempts in this benchmark.

This talk walks through where current agent communication formats hit their limits, how speech-act theory and information theory informed AXON's design, and what the benchmarks actually show — including the tradeoffs where AXON doesn't win (prompt overhead, no advantage over structured English on compactness). I'll do live side-by-side comparisons of equivalent agent tasks across formats, demonstrate the reference parser, and share the full open-source toolkit (MIT). AXON is early-stage (v0.1) and empirically tested — come stress-test the claims.

**Internal Notes:** Sweden's first national AI prompting champion (2025, 300+ participants). Regular speaker on AI strategy and agentic systems for enterprise audiences including IKEA, Saab, Epidemic Sound, and Koenigsegg. 15+ years enterprise experience in data architecture and AI, including Product Owner of AI Enablement at Scania/Traton.
