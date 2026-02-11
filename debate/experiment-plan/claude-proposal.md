# AXON Experimental Validation Plan — Opening Position (Claude)

## What Is AXON?

AXON (Agent eXchange Optimized Notation) is a structured, token-efficient notation for agent-to-agent communication. It has:
- 20 core performatives (speech acts: INF, QRY, REQ, PRO, ACC, REJ, etc.)
- Formal EBNF grammar with 7-level operator precedence
- A working Python reference parser (934 lines)
- Pilot data showing ~66% token reduction vs English (n=8, unvalidated)
- Full spec at `spec/SPECIFICATION.md`, parser at `src/axon_parser.py`

## The Question

We want to run experiments that produce publishable results answering: **Does AXON actually improve agent-to-agent communication, and at what cost?**

The concrete use case: two Claude instances debating in headless mode. What changes if they communicate in AXON instead of English?

## Proposed Experiments

### Exp 0: AXON Learnability (Gate Experiment)
- **Question:** Can LLMs generate syntactically valid AXON?
- **Method:** 30 task prompts x 4 prompting strategies (zero-shot, spec-only, 1-shot, 3-shot) x 3 complexity levels x 3 repetitions = 360 generations
- **Metric:** Parse success rate using existing parser's `validate()` function
- **Gate:** Must achieve >=80% validity with few-shot on simple tasks to proceed
- **Why this matters:** StructEval (2025) shows GPT-4o achieves only 76% on structured formats. AXON is novel (not in training data). If LLMs can't produce valid AXON, everything else is moot.

### Exp 1: Static Token Efficiency
- **Question:** How much do tokens shrink, measured with real tokenizers?
- **Method:** 40 semantically equivalent messages expressed in AXON, realistic English, JSON, and YAML. Count tokens with cl100k_base and o200k_base.
- **Key improvement over pilot data:** Replace strawman verbose English ("Hello Agent-B, I am Agent-A. Could you please...") with realistic agent-style English.
- **Stats:** Wilcoxon signed-rank test, Cliff's delta effect size.

### Exp 2: Agent Debate (Primary Use Case)
- **Question:** What changes when two Claude instances debate in AXON vs English?
- **Method:** 10 debate topics x 3 format conditions x 3 reps = 90 debates, 6 turns each
- **Format conditions:**
  1. Free-form English (baseline)
  2. AXON (with spec in system prompt)
  3. Structured English (speech-act labels in natural language — the critical control)
- **Metrics:** Total tokens, API cost, latency (efficiency) + argument quality, semantic fidelity, conclusion quality rated by LLM-judge (quality)
- **Critical design choice:** The Structured English condition isolates whether gains come from the notation itself or from explicit speech-act structure.
- **Known risk:** Tam et al. (2024) showed format restrictions degrade reasoning 10-15%. This experiment directly measures whether that happens.

### Exp 3: Multi-Agent Coordination
- 4 tasks with verifiable ground truth (info aggregation, scheduling, pipeline, consensus)
- 3-4 agents per task, measure task success rate and tokens consumed

### Exp 4: Roundtrip Fidelity
- English→AXON→English translation, measure information preservation
- 40 agent communications, LLM-judge rates fidelity

### Exp 5: Scaling Behavior
- 2, 4, 8, 16 agents, measure if AXON's advantage grows super-linearly
- Power law fit: tokens = a * n^b

## Minimum Viable Paper

Experiments 0 + 1 + 2 = publishable (~$20-30 total API cost). If results are negative, the paper becomes "Can LLMs Adopt Novel Structured Formats?" which is still publishable.

## Key Literature Informing This Design

- **Agora Protocol (Oxford 2024):** Structured protocols yield 5x cost reduction in 100-agent networks
- **ProtocolBench (2025):** Protocol choice varies completion time by up to 36.5%; methodology template for fair comparison
- **"Let Me Speak Freely?" (Tam 2024):** Format restrictions degrade reasoning 10-15% — our biggest risk
- **StructEval (2025):** GPT-4o at 76% for structured formats — learnability is non-trivial
- **Emergence of Machine Language (2025):** LLMs CAN learn non-English encodings with compositionality
- **MARBLE/MultiAgentBench (ACL 2025):** LLM-as-judge methodology for communication quality

## What I Want You to Critique

1. **Experimental design rigor:** Are there confounds I'm missing? Would a peer reviewer reject this?
2. **Missing experiments:** Is there a critical question I'm not asking?
3. **Methodology gaps:** Are the statistical approaches appropriate? Sample sizes sufficient?
4. **Baseline fairness:** Am I being fair to the baselines, or stacking the deck for AXON?
5. **Practical concerns:** Will this actually work with current LLM capabilities?
6. **Publication strategy:** Is the "minimum viable paper" story compelling?
7. **Cost efficiency:** Is there a cheaper way to get the same signal?

Be adversarial. Find the weaknesses. Don't be polite about it.
