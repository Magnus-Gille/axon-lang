# AXON Publishability, Use Cases & Testability Assessment

**Author**: Claude Code (draft for adversarial review)

## 1. Publishability

AXON sits at the intersection of multi-agent systems, programming language design, and LLM efficiency. The most natural home is multi-agent systems.

### Realistic targets (ordered by likelihood):
- **Workshop papers at AAMAS, NeurIPS, or ICML** on LLM-based agents or multi-agent communication — most achievable (60-70% with solid experiments)
- **AAMAS main conference** — natural fit for agent communication languages (30-40%, needs strong empirical results)
- **ArXiv preprint** — always available, builds visibility
- **Top-tier AI conferences** (NeurIPS, ICML main track) — unlikely unless results are striking

### Novelty framing:
The pitch is NOT "we invented agent communication languages" (FIPA-ACL/KQML did this in the 1990s). The framing is: "the LLM era changes the cost model fundamentally — tokens are money, context windows are finite, and agents now generate natural language by default, which reintroduces all the ambiguity that formal protocols were designed to eliminate."

### The methodology angle:
The adversarial Claude-Codex debate process is independently publishable. "Using adversarial AI review to stress-test research before human peer review" is novel. This might be more publishable than AXON itself.

### Bottom line:
Publication requires empirical results. A spec alone won't clear peer review.

## 2. Use Cases — Why Would Anyone Adopt This?

### Token efficiency is necessary but not sufficient.
50-66% fewer tokens means lower cost and latency. But JSON function calling and controlled English templates also achieve good token efficiency. If the only advantage is fewer tokens, AXON loses on adoption cost.

### The real value proposition (all three need to hold):

1. **Unambiguous intent.** Speech-act performatives (QRY vs CMD vs REQ vs PRO) make communication type explicit. English is ambiguous ("you should restart the server" — suggestion? command? observation?). JSON function calling doesn't capture this naturally.

2. **Composable coordination patterns.** Operators (`->` sequence, `&` parallel, `<-` causation) express multi-step plans in a single message. Harder in English or flat JSON.

3. **Protocol-level reasoning.** Negotiation patterns (PRO/CTR/ACC/REJ) enable structured negotiation at scale. Ad-hoc English breaks down with 10+ agents.

### Target users:
- Teams running multi-agent pipelines at scale
- Agent orchestration frameworks (CrewAI, AutoGen, LangGraph) as internal protocol
- Agent-to-agent API builders

### Honest risk:
Controlled English + function calling gets 80% of the benefit with 0% adoption cost. AXON must prove the remaining 20% justifies a new syntax.

## 3. Concrete Testing

### Core experiment design:

**3-5 multi-agent coordination tasks:**
- Incident response triage
- CI/CD pipeline orchestration
- Data processing pipeline
- Multi-agent negotiation (resource allocation)

**5 conditions:**
1. Free English
2. Structured/controlled English
3. JSON function calling
4. AXON
5. (Optional) FIPA-ACL style

**4 metrics:**
- Task success rate
- Token count
- Error recovery
- Cost (API dollars)

### The result that matters:
"AXON achieves equal or higher task success rates while using significantly fewer tokens." If success rate drops, the argument falls apart.

### What kills the project:
If JSON function calling matches AXON on both success rate and token efficiency, AXON has no reason to exist.

### What makes it publishable regardless:
Pre-registered experiment with honest negative results is a useful contribution.

## 4. Two publishable contributions:
1. **The language experiment** — empirical question, publishable regardless of answer
2. **The adversarial methodology** — novel, practical, orthogonal to AXON's success
