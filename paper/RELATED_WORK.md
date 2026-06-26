# Related Work (Draft)

## 2.1 Agent Communication Protocols and Standards

The agent communication ecosystem has undergone rapid consolidation. The Agentic AI Foundation (AAIF), formed under the Linux Foundation in December 2025, unified the two dominant protocol families: MCP (Anthropic) for agent-to-tool communication and A2A (Google) for agent-to-agent coordination, with IBM's ACP merging into A2A and OpenAI contributing AGENTS.md. This effectively settles the *transport layer* — how agents connect — with all major AI companies (AWS, Anthropic, Google, Microsoft, OpenAI) participating in governance.

At the *content format layer* — what the message payload looks like — no comparable convergence has occurred. A2A's `Part` structure supports arbitrary content types but makes no recommendation about optimal format. Most frameworks default to plain JSON or natural language. TOON (Token-Oriented Object Notation, Nov 2025) targets token efficiency for data serialization, achieving 30–60% savings on tabular data, but is designed for structured data payloads rather than agent messages with speech-act semantics. NLIP (Ecma TC-56, Dec 2025) ratified an envelope standard (ECMA-430 through ECMA-434) that specifies multimodal message wrapping but is similarly agnostic to content format optimization.

Our work evaluates *content format* alternatives within this settled transport infrastructure. AXON could serve as a `text/axon` content type within A2A messages, complementary to rather than competitive with the transport layer.

## 2.2 Format and Protocol Benchmarking

Several recent benchmarks evaluate aspects of agent communication, though none directly compares message content formats for compositionality.

**ProtocolBench** (ICLR 2026) provides the closest methodological template, evaluating multi-agent protocols along four axes: task success, end-to-end latency, message overhead, and failure-time robustness. Their ProtocolRouter learns to select protocols per-scenario based on requirements and runtime signals. However, ProtocolBench evaluates at the *protocol* level (how agents coordinate), while we evaluate at the *content format* level (how individual messages encode compositional meaning). Their finding that "no single protocol dominates all scenarios" motivates our investigation of whether the same holds for content formats.

**StructEval** (TMLR 2025) benchmarks LLM structural output generation across 18 formats and 44 task types. Their finding that even state-of-the-art models achieve only ~76% average accuracy on structured generation provides calibration context for our validity rates. StructEval measures whether LLMs *can produce* valid instances of a format; we measure whether the format *effectively communicates* compositional relationships.

**ReliabilityBench** (Jan 2026) introduces a chaos-engineering framework for LLM agent reliability, defining a reliability surface R(k,ε,λ) across consistency (k), perturbation robustness (ε), and fault tolerance (λ). Our Experiment 2 parallels their perturbation approach at the message format level: we apply character deletion, token swap, and truncation to test structural preservation across formats. Their finding that perturbations reduce agent success from 96.9% to 88.1% (at ε=0.2) contextualizes our observation that strict formats (AXON, JSON) are more fragile (~16–18% preservation) but provide clearer error detection than lenient formats (FIPA-ACL: 90%, English: 100%).

**A2ASecBench** (ICLR 2026) is the first security benchmark for A2A multi-agent systems, categorizing risks into supply-chain manipulations and protocol-logic weaknesses. While orthogonal to our compositionality focus, their threat taxonomy is relevant to evaluating content format resilience in adversarial settings.

## 2.3 Structured Contracts and Behavioral Specifications

**SEMAP** (Oct 2025) demonstrates that adding explicit behavioral contracts — pre-conditions, post-conditions, lifecycle stage, and verification checkpoints — to agent communication over A2A infrastructure reduces failures by 47–70% on code development and vulnerability detection tasks. This is a significant result that directly challenges whether a *new format* is needed: if behavioral contracts on plain JSON achieve such improvements, is format-level syntax optimization worthwhile?

We address this challenge through our JSON+Contracts condition, which implements SEMAP's core thesis (behavioral contracts added to JSON FC). This allows direct comparison between *extrinsic contracts* (rules about what JSON fields must be present) and *intrinsic composition* (AXON's native operators for sequence, parallel, alternative, and causal relationships). Our central argument is that these approaches operate at different levels and are complementary: contracts specify behavioral expectations, while intrinsic operators encode the compositional structure of multi-step messages. The empirical question is whether intrinsic operators provide additional benefit *beyond* what contracts achieve.

## 2.4 Token Efficiency and Cost Optimization

Token efficiency was originally AXON's headline contribution (~32% savings over JSON FC across 3 models × 9 tasks). However, the landscape has evolved:

- TOON achieves 30–60% savings for tabular data with real-world adoption (n8n, Zapier) and a TypeScript SDK — demonstrating that token optimization within the JSON ecosystem is viable without designing a new format.
- "Token-Efficient Codified Communication" (arXiv 2507.03254) shows that YAML-based codified prompts reduce tokens relative to natural language Chain-of-Thought.
- Rapidly falling inference costs reduce the marginal value of per-message token savings.

We therefore reframe token efficiency as a *secondary* finding, not the primary contribution. The more durable advantages are compositionality (how well formats express multi-step relationships) and reliability (how consistently formats perform across models and under perturbation). Our prompt overhead analysis shows AXON's system prompt amortizes after ~7 messages vs JSON FC, which is acceptable for multi-turn agent conversations but not for single-shot interactions.

## 2.5 Speech-Act Theory in Agent Communication

AXON draws on the speech-act tradition established by KQML (Finin et al., 1993) and FIPA-ACL (FIPA, 2002), which model agent communication as performative acts (inform, request, query, propose, etc.) with formal sender/receiver semantics. Both languages achieved theoretical elegance but suffered from XML verbosity and poor alignment with modern LLM capabilities.

AXON modernizes this tradition: speech-act performatives (INF, QRY, REQ, CMD, etc.) with token-optimized syntax designed for LLM generation and parsing. Our FIPA-ACL condition provides a direct comparison: same speech-act model, different syntax (verbose keyword-value pairs vs compact notation). The Agora project (Oxford) proposes meta-protocol negotiation where agents dynamically agree on communication formats via "Protocol Documents" — a complementary approach where AXON could be one negotiable format option.

The broader multi-agent communication landscape is surveyed in "Beyond Self-Talk" (arXiv 2502.14321), which identifies efficiency, security, and scalability as key gaps in current MAS communication research. Our work addresses the efficiency and compositionality aspects; security analysis (cf. A2ASecBench) and large-scale evaluation (cf. WMAC 2026 themes) remain future work.
