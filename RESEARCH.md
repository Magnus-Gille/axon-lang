# Why English Is Not Optimal for Agent-to-Agent Communication

## A Research-Backed Rationale for Designing a New Language

> **Status**: Draft v0.1. Claims are labeled by evidence tier: **Established** (replicated, peer-reviewed), **Supported** (directionally correct, limited studies), **Hypothesis** (plausible but unverified).

### Executive Summary

This document synthesizes findings from information theory, linguistics, AI research, and multi-agent systems to argue that natural language (English) carries significant overhead for agent-to-agent communication, and that a purpose-built language can achieve higher efficiency. The evidence shows that English carries 50-75% redundancy over reliable digital channels [Established], suffers from pervasive structural ambiguity [Established], and uses tokens on syntactic overhead designed for human cognition [Supported]. Whether this overhead is sufficient to justify a new language vs. controlled English with structured tool-calling is an empirical question that benchmarking must settle [see Section 8].

---

## 1. Information-Theoretic Inefficiency of English

### Shannon's Foundational Measurements [Established]

Claude Shannon's seminal 1948 paper *"A Mathematical Theory of Communication"* and his 1951 follow-up *"Prediction and Entropy of Printed English"* established that English text carries far less information per character than its theoretical maximum.

- **Theoretical maximum**: If all 26 letters occurred with equal probability, entropy would be ~4.7 bits/character (assuming equal probability across 26 letters plus space; actual maximum depends on character set assumptions)
- **Actual entropy of English**: Between **0.6 and 1.3 bits/character** when considering long-range statistical dependencies (Shannon, 1951)
- **Redundancy**: Approximately **50% at the 8-character level** (Shannon), rising to **~75% when considering longer-range structure** (later estimates by Cover & King, 1978)

This means that 50-75% of every English message is **predictable under a statistical model** of the language. Over reliable digital channels where error correction is handled at the transport layer, this redundancy is unnecessary for preserving meaning — though it does serve human cognitive functions (ambiguity resolution, speech repair, emphasis).

> Source: Shannon, C.E. (1951). "Prediction and Entropy of Printed English." *Bell System Technical Journal*. ([PDF](https://www.princeton.edu/~wbialek/rome/refs/shannon_51.pdf))

> Source: Cover, T.M. & King, R.C. (1978). "A Convergent Gambling Estimate of the Entropy of English." *IEEE Trans. Information Theory*.

### The Universal ~39 bits/second Regularity [Established]

Coupé et al. (2019) demonstrated across 17 languages and 9 language families that human speech converges on approximately **39.15 bits per second** of information transmission. Languages with faster speech rates compensate with lower information density per syllable, and vice versa.

This is an empirical cross-linguistic regularity reflecting human cognitive processing characteristics — not a hard universal constraint on information encoding. AI agents can process thousands of tokens per second, meaning the human-centric design of natural language does not exploit the bandwidth available in machine-to-machine channels.

> Source: Coupé, C., Oh, Y.M., Dediu, D., & Pellegrino, F. (2019). "Different languages, similar encoding efficiency." *Science Advances*, 5(9). ([DOI](https://www.science.org/doi/10.1126/sciadv.aaw2594))

### Prompt Compression Demonstrates the Redundancy [Supported]

Microsoft's LLMLingua research (EMNLP 2023, ACL 2024) demonstrated that natural language prompts can be **compressed up to 20x with minimal performance loss in best-case scenarios** when communicating with LLMs. Typical compression ratios are lower (2-5x) depending on content type and task sensitivity.

Key findings:
- GPT-4 can recover key information from heavily compressed prompts
- Natural language tokens carry **varying amounts of information** — many are low-information
- Compression effectiveness depends on domain and task structure

The 20x figure represents a best-case ceiling, not a typical result. Nonetheless, even conservative estimates (2-5x) indicate substantial redundancy in natural language for machine consumption.

> Source: Jiang, H., et al. (2023). "LLMLingua: Compressing Prompts for Accelerated Inference of Large Language Models." *EMNLP 2023*. ([arXiv](https://arxiv.org/abs/2310.05736))

> Source: Microsoft Research — LLMLingua Project ([Link](https://llmlingua.com/))

---

## 2. Ambiguity: English's Structural Problem for Machine Communication

### Pervasive Multi-Level Ambiguity [Established]

English exhibits ambiguity at every linguistic level:

- **Lexical**: "bank" has 10+ meanings; "set" has hundreds of definitions (OED, 2nd ed.)
- **Syntactic**: "I saw the man with the telescope" — who has the telescope?
- **Semantic**: "Every student read a book" — the same book, or different books?
- **Pragmatic**: "Can you pass the salt?" — a question about ability, or a request?
- **Referential**: "After John talked to Bill, he left" — who left?

Research on AI systems shows that **wholly unambiguous communication is impossible using an inherently ambiguous natural language** (Bender et al., CEUR-WS Vol-2916). While humans resolve ambiguity through shared world knowledge and conversational context, agents operating across different domains and without shared embodied experience lack this grounding.

> Source: Bender, E.M. et al. "Impossibility of Unambiguous Communication as a Source of Failure in AI Systems." *CEUR-WS Vol-2916*. ([PDF](https://ceur-ws.org/Vol-2916/paper_14.pdf))

### LLMs Still Struggle With Ambiguity [Supported]

Research (2024) shows that ChatGPT and similar models **struggle with linguistically complex sentences**, particularly those with semantic ambiguity and language games. This is documented across multiple model families, not only ChatGPT. LLMs rely on statistical patterns that can fail when context is ambiguous or when sentences require pragmatic reasoning.

> Source: Cogent Arts & Humanities (2024). "Big claims, low outcomes: fact checking ChatGPT's efficacy in handling linguistic creativity and ambiguity." ([DOI](https://www.tandfonline.com/doi/full/10.1080/23311983.2024.2353984))

---

## 3. Historical Agent Communication Languages

### KQML and FIPA-ACL (1990s-2000s) [Established]

The AI research community recognized decades ago that natural language is inadequate for formal agent communication. Two landmark languages were developed:

**KQML** (Knowledge Query and Manipulation Language) introduced:
- Structured message formats based on **speech-act theory** (Searle, 1969; Austin, 1962)
- **Performatives** encoding message intent (tell, ask, reply, achieve, etc.)
- Separation of communication protocol from content language

**FIPA-ACL** (Foundation for Intelligent Physical Agents) refined this with:
- ~20 standard **communicative acts** with formal semantics
- Semantics defined in modal logic (beliefs, desires, intentions)
- Strict boundaries — agents cannot directly modify each other's knowledge state

Both demonstrated that **structured, formally-defined communication improves reliability and interoperability** for multi-agent coordination. Their key insight: messages should be *actions* (speech acts), not just information transfer. Neither achieved widespread adoption, partly due to verbosity (XML-based) and the complexity of their formal semantics.

> Source: Finin, T., et al. (1994). "KQML as an Agent Communication Language." *CIKM '94*.

> Source: FIPA Specification (2002). "FIPA ACL Message Structure Specification." ([Link](http://www.fipa.org/specs/fipa00061/SC00061G.html))

---

## 4. Emergent Languages: What Agents Invent When Left to Their Own Devices

### Facebook/Meta's Negotiation Agents (2017) [Supported — suggestive case study]

In a well-known experiment by Lewis, Yarats, Dauphin, Parikh, and Batra at Facebook AI Research, negotiation agents trained to communicate **diverged from English** when there was no reward for staying in English. They developed their own compressed conventions for negotiation.

This is a suggestive case study showing that agents optimizing purely for task performance may abandon natural language conventions. It does not prove that purpose-built languages are globally superior — the emergent protocols were task-specific and not designed for general interoperability.

> Source: Lewis, M., et al. (2017). "Deal or No Deal? End-to-End Learning for Negotiation Dialogues." ([arXiv](https://arxiv.org/abs/1706.05125))

### Emergent Language Research (2023-2025) [Supported]

A comprehensive survey (Autonomous Agents and Multi-Agent Systems, 2025) of emergent language research shows that when agents develop communication through reinforcement learning, the resulting languages exhibit:

- **Compositionality**: Close meanings map to nearby messages
- **Structure**: Combinatorial and compositional, similar to natural language grammar but more regular
- **Efficiency**: Optimized for task performance rather than human readability
- **Topographic similarity**: Higher degrees when trained with feedback

These findings suggest that unconstrained optimization for agent coordination tends toward compact, structured communication. However, emergent languages are typically task-specific and lack the interpretability and generality needed for open-world deployment.

> Source: "Emergent language: a survey and taxonomy." *Autonomous Agents and Multi-Agent Systems* (2025). ([Springer](https://link.springer.com/article/10.1007/s10458-025-09691-y))

---

## 5. The Lojban Precedent: Logic-Based Language Design

### Lojban and Lojban++ [Established — for formal properties; Hypothesis — for performance claims]

Lojban is a constructed language based on predicate logic. Its relevant formal properties:

- Grammar based on **predicate logic** — sentences built around predicates and ordered arguments
- **No irregular forms** in spelling or grammar
- **Parseable like a programming language** — mechanical parsing is trivial
- Syntactic ambiguity can be eliminated by design

Ben Goertzel's **Lojban++** variant (2013) specifically proposed using this approach as an interlingua for human-AGI communication, arguing that logic-based language design dramatically improves machine parseability. Whether this translates to measurable performance benefits in practice remains untested.

> Source: Goertzel, B. (2013). "Lojban++: An Interlingua for Communication Between Humans and AGIs." *AGI 2013*. ([Springer](https://link.springer.com/chapter/10.1007/978-3-642-39521-5_3))

---

## 6. Modern Protocol Research: The Current State (2024-2025)

### The Agent Protocol Fragmentation Problem [Established]

A comprehensive survey (arXiv:2504.16736, 2025) identifies **fundamental fragmentation** in how LLM agents communicate today, comparing the situation to the "protocol wars" of early networking. Currently no standard exists for agent-to-agent communication, with MCP, A2A, and various proprietary formats competing.

> Source: "A Survey of AI Agent Protocols" (2025). ([arXiv](https://arxiv.org/abs/2504.16736))

### LACP: Telecom-Inspired Protocol (NeurIPS 2025) [Supported — proposed, not validated]

The LLM Agent Communication Protocol draws from telecommunications to propose a three-layer architecture ensuring semantic clarity, transactional integrity, and security. It argues that every agent message must be authenticated, semantically grounded, and transactionally atomic. LACP is a proposed design; no deployment-scale validation results are available.

> Source: Li, X., et al. (2025). "LLM Agent Communication Protocol (LACP)." *NeurIPS 2025 AI4NextG Workshop*. ([arXiv](https://arxiv.org/abs/2510.13821))

### Agora: The Meta-Protocol Approach (Oxford, 2024) [Supported]

Agora demonstrates that agents using natural language for all communication are **approximately 5x more expensive** than agents that negotiate efficient protocols for frequent communication patterns.

Key finding: In a 100-agent simulation, the percentage of queries requiring LLM processing dropped from 80% to 30% as agents established efficient communication protocols. This suggests significant potential for cost reduction through structured communication, though the specific 5x figure is from a single simulation study.

> Source: "A Scalable Communication Protocol for Networks of Large Language Models." ([arXiv](https://arxiv.org/abs/2410.11905))

### IETF Token-Efficient Data Layer Draft (2025) [Proposed]

An IETF Internet-Draft (December 2025) explicitly addresses "token/context bloat" in agentic communication, referencing MCP and A2A protocols. It proposes a token-efficient data layer for agent-to-agent exchanges. This confirms that the problem AXON targets — token overhead in structured agent communication — is now recognized at the standards level.

> Source: Chang, D. et al. (2025). "Token-efficient Data Layer for Agentic Communication." IETF Internet-Draft. ([Link](https://www.ietf.org/archive/id/draft-chang-agent-token-efficient-00.html))

### TOON: Token-Optimized Data Format (2025) [Supported]

Token-Oriented Object Notation (TOON) achieves **~60% fewer tokens than JSON** for structured data while maintaining full semantic fidelity. This demonstrates that even simple format optimization yields significant savings for machine-to-machine data exchange.

> Source: TOON Format ([GitHub](https://github.com/toon-format/toon))

---

## 7. Synthesis: Design Principles for an Optimal Agent Language

From this research, the design principles for an efficient agent-to-agent language:

| Principle | Rationale | Evidence Tier | Source |
|-----------|-----------|---------------|--------|
| **Zero syntactic ambiguity** | English ambiguity causes parsing failures | Established | Bender et al.; Lojban |
| **Minimal redundancy** | English is 50-75% redundant over digital channels | Established | Shannon (1951) |
| **Speech-act semantics** | Intent must be explicit, not inferred | Established | KQML; FIPA-ACL |
| **Compositional structure** | Complex meanings from simple primitives | Supported | Emergent language research |
| **Token-efficient encoding** | Reduce unnecessary overhead | Supported | LLMLingua; TOON |
| **Formally parseable grammar** | Mechanical parsing, no heuristics | Established | Lojban; formal languages |
| **Envelope + shared schemas** | Reduce per-message overhead | Supported | Protocol survey (2025) |
| **Typed content** | Prevent type confusion errors | Established | Programming language theory |

### Why Not Just Use JSON/Protocol Buffers?

Structured data formats solve the parsing problem but **lack built-in semantics**. A JSON message like `{"action": "request", "data": {...}}` has no formally defined meaning — the semantics are in documentation, not in the language. FIPA-ACL showed that formal semantic definitions of communicative acts improve reliability for multi-agent coordination. However, JSON + schema + envelope is a strong baseline that AXON must demonstrably improve upon.

### Why Not Just Use English With Conventions?

Prompt compression research shows that natural language is **2-20x more verbose than necessary** (range reflects best-case vs. typical compression). Even with conventions, English retains its ambiguity, irregular grammar, and token-inefficient encoding. The Agora protocol demonstrated approximately 5x cost reduction by moving away from natural language for routine communication.

---

## 8. Counter-Arguments: The Case for English

Intellectual honesty requires acknowledging English's significant advantages:

### Interoperability
English is the de facto standard for LLM communication. All major models are trained primarily on English text. Using a purpose-built language requires every participating agent to support it — a significant adoption barrier.

### Auditability
Human operators need to inspect, debug, and audit agent communications. A new language adds a translation layer that can obscure meaning during incident response.

### Open-World Adaptability
English can express arbitrary concepts without schema updates. A formal language may struggle with novel domains not anticipated by its designers.

### Transition Costs
The tooling ecosystem (logging, monitoring, testing) is built for natural language and JSON. Adopting a new language requires building this infrastructure from scratch.

### Controlled English + Function Calling
Modern LLMs with structured output capabilities (function calling, JSON mode) may achieve most of the benefits of a purpose-built language while retaining English's interoperability. This is the strongest baseline that AXON must be compared against.

**Whether AXON's information-density advantage outweighs these costs is an empirical question** that only reproducible benchmarking can settle [Hypothesis].

---

## 9. Recommended Architecture: Hybrid Deployment

Based on the evidence, the recommended architecture is **hybrid**:

- **AXON for agent-to-agent loops**: Where information density, unambiguous parsing, and explicit intent labeling provide the most value
- **English for human-facing interfaces**: Where readability, auditability, and familiarity matter most
- **Translation layer**: Bidirectional AXON-to-English conversion for human inspection

This avoids the false binary of "replace English entirely" vs. "English is good enough."

---

## Conclusion

The evidence is convergent and suggestive: English is a brilliant language for humans communicating over noisy channels with shared cultural context. For agents communicating over reliable digital channels, it carries significant unnecessary overhead. A purpose-built language that combines:

1. The **explicit intent labeling** inspired by FIPA-ACL [Established precedent]
2. The **unambiguous grammar** of Lojban [Established formal property]
3. The **token efficiency** of TOON [Supported by measurements]
4. The **compositionality** of emergent agent languages [Supported by research]
5. The **speech-act foundation** of KQML [Established precedent]

...has strong theoretical grounding for achieving efficiency gains, though the specific magnitude of improvement over controlled-English baselines remains to be measured.

This is the rationale for **AXON** (Agent eXchange Optimized Notation). Preliminary pilot data (n=8 hand-crafted examples) shows ~66% token reduction vs. verbose English equivalents, but this figure cannot be generalized until reproducible benchmarking with standardized baselines is completed.
