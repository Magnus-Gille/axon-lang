# Agent-to-Agent Communication Ecosystem Landscape (Feb 2026)

## Purpose

Map the full ecosystem of agent communication protocols, formats, and standards as of February 2026. Assess where AXON fits (if at all), identify direct competitors, and evaluate whether a pivot is needed.

---

## 1. The Ecosystem Map

The landscape has **five distinct layers**. Understanding which layer AXON operates at is critical for positioning.

### Layer 1: Transport/Infrastructure Protocols (HOW agents connect)

| Protocol | Backer | Transport | Message Format | Status | Stars/Adoption |
|----------|--------|-----------|----------------|--------|----------------|
| **MCP** | Anthropic → AAIF/Linux Foundation | JSON-RPC 2.0 over stdio/SSE/HTTP | JSON-RPC | **De facto standard** for agent-tool. 10,000+ servers. Adopted by ChatGPT, Gemini, Copilot, Cursor | ~40k GitHub stars |
| **A2A** | Google → Linux Foundation | JSON-RPC 2.0 over HTTPS, gRPC, SSE | JSON-RPC + Agent Cards | **Emerging standard** for agent-agent. 150+ orgs. ACP merged in. v0.3 released | ~20k GitHub stars |
| **ACP** | IBM BeeAI → merged into A2A | REST HTTP + WebSocket | JSON + multipart | **Deprecated** — merged into A2A under Linux Foundation (Aug 2025) | N/A |
| **ANP** | Agent Network Protocol community | HTTPS P2P, DID-based identity | JSON-LD + semantic descriptions | **Regional** — primarily Chinese AI ecosystem | ~2k GitHub stars |
| **NLIP** | Ecma International (TC-56) | HTTP, AMQP, WebSocket | Multimodal envelope (text, structured data, binary) | **Ratified standard** (Dec 2025) — ECMA-430 through ECMA-434. 5 standards published | Formal standard body |
| **AITP** | NEAR Foundation | Thread-based messaging | Capabilities + structured messages | **Early** — RFC Feb 2025 | Small |
| **LMOS** | Eclipse Foundation | HTTP, MQTT, AMQP | JSON-LD + semantic models | **Incubation** | Eclipse ecosystem |

### Layer 2: Discovery/Metadata (WHO agents are)

| Standard | Purpose | Format | Relationship to A2A/MCP |
|----------|---------|--------|------------------------|
| **Agent Cards** (A2A) | Agent capability advertisement | JSON | Core part of A2A |
| **agents.json** | Web service declaration for agents | JSON (like robots.txt) | Complementary |
| **AGENTS.md** | Project guidance for coding agents | Markdown | Contributed to AAIF by OpenAI |

### Layer 3: Data/Content Formats (WHAT the payload looks like)

| Format | Focus | Token Efficiency vs JSON | Adoption | Notes |
|--------|-------|--------------------------|----------|-------|
| **JSON** | Universal default | Baseline | Universal | Every LLM API uses it. Training distribution advantage |
| **TOON** | Token-optimized data serialization | 30-60% savings (tabular data) | Early (Nov 2025) | MIT license, TypeScript SDK. 74% accuracy vs JSON 70% |
| **YAML** | Human-readable config | ~30% savings vs JSON | Common in configs | Better LLM accuracy per some benchmarks |
| **Markdown** | Natural language with structure | 20-35% savings vs JSON | Very common | Aligns with LLM training data |
| **JSON-LD** | Semantic web linked data | More verbose than JSON | Niche | Used by LMOS, ANP |
| **AISP** | "AI-Structured Prompt" document format | 5.1x *more* tokens than AXON (our benchmarks) | npm package, 1 contributor | H2M document format, not M2M. v5.1. See `experiments/exp_aisp_comparison/` |
| **AXON** | Token-optimized agent messages with speech-act semantics | ~32% savings vs JSON FC (our benchmarks) | Research only | This project |

### Layer 4: Agent Frameworks (internal communication patterns)

| Framework | Communication Model | Protocol Support | Notes |
|-----------|-------------------|------------------|-------|
| **AutoGen** (Microsoft) | Conversational — agents chat in NL | No native MCP/A2A yet | Popular for research |
| **CrewAI** | Role-based task delegation | A2A support added | Growing adoption |
| **LangGraph** (LangChain) | Graph-based state machines | No native A2A | Most flexible |
| **OpenAgents** | MCP + A2A native | Both MCP and A2A | Newest entrant |
| **BeeAI** (IBM) | Platform-based orchestration | Now uses A2A (was ACP) | Enterprise focus |

### Layer 5: Academic/Research (papers, benchmarks, proposals)

| Work | Venue | Key Finding |
|------|-------|-------------|
| **ProtocolBench** (2025) | arXiv 2510.17149 | Protocol choice varies performance by 36.5%. No single protocol dominates all scenarios |
| **LACP** | NeurIPS 2025 AI4NextG | Telecom-inspired 3-layer architecture proposal for standardization |
| **"Beyond Self-Talk"** (2025) | arXiv 2502.14321 | Communication-centric survey: 5 architectures, efficiency/security/scalability gaps |
| **Agora** (Oxford) | arXiv 2410.11905 | Meta-protocol negotiation via Protocol Documents. Theoretical only, no implementation |
| **Token-Efficient Codified Communication** (2025) | arXiv 2507.03254 | YAML-based codified prompts reduce tokens vs NL Chain-of-Thought |
| **Survey of AI Agent Protocols** (2025) | arXiv 2504.16736 | Comprehensive taxonomy of MCP, ACP, A2A, ANP + 10 others |

### The Governance Convergence

In December 2025, the **Agentic AI Foundation (AAIF)** was formed under the Linux Foundation, unifying:
- **MCP** (Anthropic) — agent-to-tool standard
- **A2A** (Google) + **ACP** (IBM, merged in) — agent-to-agent standard
- **AGENTS.md** (OpenAI) — project guidance standard
- **goose** (Block) — agent framework

Platinum members: **AWS, Anthropic, Block, Bloomberg, Cloudflare, Google, Microsoft, OpenAI**

This means the protocol layer is effectively settled: **MCP for tools, A2A for agents**, both under neutral governance with all major AI companies participating.

---

## 2. Where AXON Actually Sits

### AXON is a Layer 3 entity, not Layer 1

AXON does NOT define:
- Transport (HTTPS, gRPC, WebSocket)
- Discovery (Agent Cards, capability advertisement)
- Authentication/security infrastructure
- Task lifecycle management
- Streaming/async patterns
- Session management

AXON DOES define:
- A compact, token-efficient **message content format**
- **Speech-act semantics** (performatives: QRY, INF, REQ, CMD, etc.)
- **Structured routing** (@sender>@receiver)
- **Metadata** (id, timestamps, protocol version)
- **Compositionality** (nested expressions, typed primitives)

In A2A terms, AXON would be the content of a `Part` within a `Message`. A2A's `Part` supports arbitrary content types. AXON could be a `text/axon` content type.

### The critical framing problem

AXON was conceived as a complete "language for agent-to-agent communication." But the ecosystem has evolved such that:

1. **Transport** is handled by A2A/MCP (HTTPS + JSON-RPC)
2. **Discovery** is handled by Agent Cards
3. **Security** is handled by the protocol layer (OAuth2, mTLS, API keys)
4. **Task management** is handled by A2A's task lifecycle

What's LEFT for AXON is the **content format** — the actual structured payload of an agent message. This is a much narrower (but still meaningful) niche than originally conceived.

---

## 3. Direct Competitors (at AXON's actual layer)

### Tier 1: Primary competitors

**1. Plain JSON (the incumbent)**
- Used by A2A, MCP, and every framework
- LLMs trained extensively on it
- Verbose but universal
- AXON's Exp 1 shows ~32% token savings over JSON FC

**2. TOON (Token-Oriented Object Notation)**
- Released Nov 2025, MIT license
- Same thesis as AXON: tokens are expensive, optimize the format
- 30-60% savings for tabular data
- But targets **data serialization** (arrays, records), NOT agent messages
- No speech-act semantics, no routing, no performatives
- More like a JSON replacement for data payloads than a communication language
- Has TypeScript SDK, Wikipedia page, real adoption in LLM tooling (n8n, Zapier)

**3. Natural Language (the dark horse)**
- Most multi-agent frameworks (AutoGen, CrewAI) default to NL
- Research ("Beyond Self-Talk") shows NL works well for high-level coordination
- Zero barrier to adoption — no format agreement needed
- But: ambiguous, verbose, hard to parse programmatically

**4. AISP (AI-Structured Prompt)**
- v5.1, npm package, 1 contributor, 7 commits, zero tests in repo
- Claims to be an agent communication standard, but is a **human-to-machine document format** (mandatory 5-block structure: Header, Body, Footer, Validation, Metadata)
- Our benchmarks show AISP uses **5.1x more tokens** than AXON for identical content (231 vs 45 tok avg)
- Validation rigor: AXON detects 65% of malformed inputs vs AISP 30%
- Research methodology: AXON 20/20 vs AISP 0/20
- Fundamentally different design goals (H2M vs M2M), but occupies nearby keyword space
- Full analysis: `experiments/exp_aisp_comparison/RESULTS.md`, `debate/aisp-analysis.md`

### Tier 2: Adjacent/partial competitors

**5. Codified YAML prompts**
- Used in "Token-Efficient Codified Communication" (arXiv 2507.03254)
- Structured role/tool/plan specs in YAML
- Token-efficient, but a prompting strategy, not a communication format

**6. FIPA-ACL**
- Same speech-act model as AXON
- But XML-based (very verbose), no modern adoption
- AXON is essentially "FIPA-ACL for the LLM era" — same ideas, token-optimized

**7. Agora (Oxford meta-protocol)**
- Allows agents to negotiate communication formats dynamically
- In theory, agents could negotiate to use AXON via Agora
- But Agora is theoretical only, no implementation

### Tier 3: Non-competitors (different layer)

A2A, MCP, ACP, ANP, NLIP, AITP, LMOS, AG-UI — all operate at the transport/protocol layer. They define HOW agents connect, not WHAT the message content looks like. They are **complementary** to AXON, not competitive.

---

## 4. SWOT Analysis for AXON

### Strengths
- **Empirical evidence**: Only project with controlled, multi-model benchmarks comparing agent message formats (Exp 0, Exp 1)
- **Speech-act semantics**: Well-grounded in KQML/FIPA-ACL tradition; A2A lacks this
- **Token efficiency**: ~32% better than JSON FC, validated across 3 models × 9 tasks
- **Formal grammar**: Unambiguous EBNF, reference parser, conformance tests
- **Research rigor**: Pre-registered experiments, cross-validation, adversarial review

### Weaknesses
- **Zero adoption**: Only used in this research project
- **Training distribution mismatch**: LLMs aren't trained on AXON; they are trained on JSON/NL
- **Network effect problem**: Both sender AND receiver must support AXON
- **Narrow scope**: Only covers message content, not transport/discovery/security
- **No SDK**: Only a Python reference parser, no production libraries

### Opportunities
- **A2A content type**: Position as a `text/axon` MIME type within A2A messages
- **TOON collaboration**: TOON + AXON = data format + message format (complementary)
- **Research contribution**: The empirical methodology (7-condition benchmark) is valuable independent of AXON
- **Standard body input**: Feed findings into AAIF/NLIP standardization processes
- **Agora integration**: If meta-protocol negotiation takes off, AXON is a negotiable format option

### Threats
- **Token costs plummeting**: As inference gets cheaper, token efficiency matters less
- **A2A momentum**: If A2A defines content conventions (they may), AXON becomes redundant
- **JSON inertia**: JSON is "good enough" and universally understood
- **TOON traction**: If TOON expands to messages, it occupies AXON's niche with more adoption
- **LLM capabilities improving**: Future models may handle NL perfectly, eliminating the need for structured formats

---

## 5. The Pivot Question

### Option A: Stay Course — AXON as research language
**Thesis**: The research question "does message format affect multi-agent performance?" is still open and empirically interesting. AXON is the vehicle for answering it.
- **Pro**: The experiments are rigorous and the question is genuinely unaddressed in the literature
- **Pro**: The adversarial methodology (Track B) is independently publishable
- **Con**: AXON itself won't be adopted; the contribution is the findings, not the format
- **Risk**: Medium — publishable regardless, but "yet another format nobody uses"

### Option B: Pivot to A2A Content Format
**Thesis**: Reposition AXON not as a standalone language but as a token-efficient content type within the A2A ecosystem.
- **Pro**: Rides A2A's momentum, solves the adoption problem
- **Pro**: A2A explicitly supports arbitrary content types in Parts
- **Con**: Requires building an A2A SDK/adapter, significant engineering
- **Con**: A2A community may not care about token efficiency at the content layer
- **Risk**: High engineering effort, uncertain community reception

### Option C: Pivot to Pure Methodology Contribution
**Thesis**: The real contribution is the 7-condition benchmark methodology, not AXON itself. Pivot the paper to "how to benchmark agent communication formats" with AXON as one data point.
- **Pro**: ProtocolBench (arXiv 2510.17149) validates that format benchmarking is a needed area
- **Pro**: The methodology is novel: speech-act scoring, multi-model, cross-validated
- **Pro**: More publishable — contributes a benchmark, not "my format is better"
- **Con**: Diminishes AXON's role to one condition among seven
- **Risk**: Low — the methodology contribution stands on its own

### Option D: Merge Direction with TOON
**Thesis**: TOON handles data, AXON handles messages. Propose a joint "token-efficient agent communication stack."
- **Pro**: Complementary strengths, combined adoption potential
- **Con**: TOON is a solo project with no indication of wanting collaborators
- **Risk**: Depends entirely on TOON maintainer receptivity

### Option E: Abandon AXON, Focus on Format Benchmarking
**Thesis**: The format itself is a distraction. The field needs empirical evidence about format choice. Build a reusable benchmark framework.
- **Pro**: Most useful to the community
- **Pro**: Directly cited by ProtocolBench, LACP, and "Beyond Self-Talk" research gaps
- **Con**: Loses the "design" contribution — the creative part of the project
- **Risk**: Low, but less exciting

---

## 6. Assessment: What the Ecosystem Actually Needs

Based on the landscape analysis, the ecosystem has:

**Settled**: Transport/protocol layer (A2A + MCP under AAIF)
**Settling**: Discovery/metadata (Agent Cards, agents.json)
**Unsettled**: Message content format — everyone defaults to JSON or NL, nobody has rigorously asked "is this optimal?"
**Missing**: Empirical evidence for format choice in multi-agent communication

AXON sits in the **unsettled** zone, and the research methodology addresses the **missing** piece. This is actually a good position — the infrastructure is being built, but nobody is optimizing the payload.

### Recommendation

**Option C (methodology contribution) is the strongest path**, with AXON as a concrete design artifact demonstrating that format optimization is possible and measurable. The paper becomes: "We designed AXON to test the hypothesis that message format matters, built a rigorous benchmark, and found [results]. Here's the benchmark for others to use."

Option B (A2A integration) is a good **follow-up** project if the paper lands and there's interest.

---

## 7. Key Takeaways

1. **AXON is NOT competing with A2A/MCP** — they operate at different layers. This is good news.
2. **TOON is the closest competitor** — same token-efficiency thesis, but for data, not messages. Watch closely.
3. **The protocol layer is settled** — don't try to compete here. Embrace A2A as transport.
4. **The content format layer is wide open** — nobody is optimizing it, nobody has benchmarks.
5. **The research methodology is the real differentiator** — 7-condition controlled benchmarking is novel.
6. **Token efficiency alone won't win** — costs are dropping. The speech-act semantics and unambiguity arguments may age better.
7. **NLIP (Ecma) is worth watching** — formal standard body ratification could set conventions.

---

## Sources

### Protocols & Standards
- [A2A Protocol Specification](https://a2a-protocol.org/latest/specification/)
- [MCP Specification](https://modelcontextprotocol.io/specification/2025-11-25)
- [AAIF Announcement](https://www.linuxfoundation.org/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation)
- [NLIP Standards (Ecma)](https://ecma-international.org/news/ecma-international-approves-nlip-standards-suite-for-universal-ai-agent-communication/)
- [ACP merged into A2A](https://lfaidata.foundation/communityblog/2025/08/29/acp-joins-forces-with-a2a-under-the-linux-foundations-lf-ai-data/)
- [ANP GitHub](https://github.com/agent-network-protocol/AgentNetworkProtocol)
- [AITP by NEAR](https://aitp.dev)
- [LMOS (Eclipse)](https://github.com/eclipse-lmos)
- [AG-UI Protocol](https://docs.ag-ui.com/)
- [agents.json](https://github.com/nicepkg/agents-json)

### Data Formats
- [TOON Format](https://github.com/toon-format/toon) — Token-Oriented Object Notation
- [TOON vs JSON analysis](https://jduncan.io/blog/2025-11-11-toon-vs-json-agent-optimized-data/)

### Research Papers
- [Survey of Agent Interoperability Protocols](https://arxiv.org/abs/2505.02279) — MCP, ACP, A2A, ANP comparison
- [Survey of AI Agent Protocols](https://arxiv.org/abs/2504.16736) — Comprehensive taxonomy
- [ProtocolBench](https://arxiv.org/abs/2510.17149) — Protocol benchmarking, no single protocol dominates
- [LACP](https://arxiv.org/abs/2510.13821) — Telecom-inspired standardization proposal (NeurIPS 2025)
- [Beyond Self-Talk](https://arxiv.org/abs/2502.14321) — Communication-centric MAS survey
- [Token-Efficient Codified Communication](https://arxiv.org/abs/2507.03254) — YAML codified prompts
- [Agora Protocol](https://arxiv.org/abs/2410.11905) — Oxford meta-protocol negotiation
- [A2A Protocol Criticism](https://medium.com/@ckekula/everything-wrong-with-agent2agent-a2a-protocol-7e5ae8d4ab2b)
- [A2A Adoption Analysis](https://blog.fka.dev/blog/2025-09-11-what-happened-to-googles-a2a/)

### Framework Comparisons
- [Agent Framework Comparison 2026](https://openagents.org/blog/posts/2026-02-23-open-source-ai-agent-frameworks-compared)
- [Protocol Comparison (ANP blog)](https://agent-network-protocol.com/blogs/posts/agent-communication-protocols-comparison.html)
