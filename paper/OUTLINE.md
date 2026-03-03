# Paper Outline: Benchmarking Agent Communication Formats for LLM-to-LLM Communication

## Central Thesis

> Structured agent communication formats vary in whether compositional relationships are intrinsic (native to syntax) or extrinsic (expressed through contracts). We evaluate 8 formats across compositionality, reliability, and efficiency on a 9-task benchmark spanning three complexity levels and three LLMs. Intrinsic composition operators achieve the highest compositional accuracy while maintaining the lowest cross-model variance, but strict syntax increases fragility under perturbation.

---

## 1. Introduction (~1.5 pages)

- Multi-agent LLM systems are proliferating (A2A, MCP, AutoGen, CrewAI)
- Communication format is an under-studied variable: most frameworks default to JSON or natural language
- ProtocolBench (ICLR 2026) shows protocol choice varies performance by 36.5% — but at the transport layer, not the content format layer
- **Gap**: No controlled comparison of message *content* formats for LLM-to-LLM communication
- SEMAP demonstrates that adding behavioral contracts to JSON reduces failures by 47–70% — does format-level structure provide additional benefit?
- We contribute:
  1. A 9-task benchmark with 3 complexity levels testing compositionality operators (sequence, parallel, alternative, causation, nesting)
  2. Controlled comparison of 8 formats: 3 English baselines, JSON FC, JSON+Contracts, FIPA-ACL, AXON (novel), AISP
  3. Evaluation across 3 LLMs (Claude Haiku, Claude Sonnet, GPT-5.3 Codex)
  4. Evidence that intrinsic vs extrinsic compositionality is the key axis of variation

## 2. Related Work (~2 pages)

### 2.1 Agent Communication Protocols
- **Transport layer** (settled): A2A (Google), MCP (Anthropic), unified under AAIF/Linux Foundation (Dec 2025)
- **Content format layer** (unsettled): JSON (universal default), TOON (Nov 2025, data serialization), YAML codified prompts, FIPA-ACL (historical)
- NLIP (Ecma TC-56, Dec 2025): ratified envelope standard
- Agora (Oxford): meta-protocol negotiation, theoretical only
- We evaluate at the content format layer, complementary to transport-layer work

### 2.2 Format Benchmarking
- **ProtocolBench** (ICLR 2026): 4-axis evaluation (success, latency, overhead, robustness) with ProtocolRouter — evaluates *protocols*, we evaluate *content formats*
- **StructEval** (TMLR 2025): 18 formats, 44 tasks — focuses on *generation correctness* (can the LLM produce valid format X?), we focus on *communicative effectiveness* (does format X convey compositional meaning?)
- **ReliabilityBench** (Jan 2026): chaos-engineering reliability surface R(k,ε,λ) — our Exp 2 parallels their perturbation approach at the message format level
- **A2ASecBench** (ICLR 2026): security benchmark for A2A — orthogonal (security vs compositionality)
- "Beyond Self-Talk" survey: identifies efficiency/security/scalability gaps in MAS communication

### 2.3 Structured Contracts and Behavioral Specifications
- **SEMAP** (Oct 2025): behavioral contracts (pre/post-conditions, lifecycle stages) over A2A/JSON reduce failures by 47–70%
- Our JSON+Contracts condition directly tests SEMAP's thesis: can extrinsic contracts close the compositionality gap with intrinsic operators?
- **Key distinction**: SEMAP adds *extrinsic* structure (rules about what the JSON must contain); AXON provides *intrinsic* structure (composition operators as first-class syntax)

### 2.4 Token Efficiency
- TOON (Nov 2025): 30–60% savings for tabular data, TypeScript SDK, real adoption
- "Token-Efficient Codified Communication" (arXiv 2507.03254): YAML prompts reduce tokens
- Falling inference costs reduce the importance of token efficiency alone
- We report efficiency but pivot to reliability/compositionality as primary metrics

### 2.5 Speech-Act Theory in Agent Communication
- KQML (1993), FIPA-ACL (2002): foundational speech-act models
- AXON modernizes the tradition: token-optimized, LLM-native syntax
- Agora: meta-protocol negotiation using "Protocol Documents" — complementary

## 3. Experimental Conditions (~1.5 pages)

### 3.1 Format Descriptions (Table 1)
| # | Condition | Type | Composition Style | Key Features |
|---|-----------|------|-------------------|--------------|
| 1 | Free English | Baseline | Implicit | No format constraints |
| 2 | Structured English | Baseline | Implicit | Section headers required |
| 3 | Instruction-Matched English | Control | Implicit | Same instruction volume as AXON |
| 4 | JSON Function Calling | Structured | Extrinsic | Standard JSON objects |
| 5 | JSON + Contracts | Structured | Extrinsic | JSON + pre/postconditions + lifecycle (SEMAP-inspired) |
| 6 | FIPA-ACL | Structured | Mixed | Historical speech-act format |
| 7 | AXON | Structured | Intrinsic | Native operators: `->`, `&`, `\|`, `<-`, nesting |
| 8 | AISP | Structured | Extrinsic | 5-block document format (exploratory) |

### 3.2 Fairness Protocol
- Identical task descriptions across all conditions
- Format-specific system prompts matched for instruction volume (±20%)
- Same 3 LLMs, same 3 runs per cell
- Pre-registered analysis plan + exploratory deviation notices for AISP/JSON+Contracts

### 3.3 Models
- Claude Haiku 4.5, Claude Sonnet 4.5, GPT-5.3 Codex
- CLI-based generation (zero API cost): `claude -p`, `codex exec`

## 4. Tasks and Scoring (~1.5 pages)

### 4.1 Task Design (9 tasks, 3 complexity levels)
- **Level 1**: Single operation (inform, query, delegate)
- **Level 2**: Two-step compositions (sequence, parallel, conditional)
- **Level 3**: Three+ step compositions with nesting and mixed operators

### 4.2 Scoring Framework
- **Hybrid approach**: machine extractors for structured formats + 3-judge LLM panel for English/unstructured
- **Element rate**: proportion of task elements correctly expressed
- **Composition rate**: proportion of compositional relationships correctly expressed
- **Failure rate**: proportion of outputs that fail format validation
- Cross-validation: 94.1% machine-judge agreement (30-item sample)

### 4.3 Composition Operators Evaluated
| Operator | AXON Syntax | JSON+Contracts Equivalent | English Equivalent |
|----------|-------------|---------------------------|-------------------|
| Sequence | `->` | `"relation": "sequence"` | "then", "after" |
| Parallel | `&` | `"relation": "parallel"` | "simultaneously", "while" |
| Alternative | `\|` | `"relation": "alternative"` + condition | "or", "if...else" |
| Causation | `<-` | `"relation": "causal"` + caused_by | "because", "therefore" |
| Nesting | `(...)` | Nested objects | Subordinate clauses |

## 5. Results (~3 pages)

### 5.1 Compositionality (Primary — Exp 3)
- **Table 2**: Composition rate by condition × model
- AXON: 66.2% composition rate (highest)
- JSON FC: 24.9% (lowest structured format)
- English baselines: 46–61% (judge-scored)
- Pairwise: AXON vs JSON FC +41.2%, d=1.05, p<0.0001 (Holm-corrected)
- **Key finding**: Intrinsic operators (AXON) outperform extrinsic contracts (JSON+Contracts) and implicit expression (English)

### 5.2 Token Efficiency (Secondary — Exp 1)
- **Table 3**: tok/unit by condition × model
- AXON: 15.4 tok/unit (best among structured), 0% failure rate
- JSON FC: 22.6 tok/unit, 27.2% failure rate
- AXON vs JSON FC: ~32% better (bootstrap CI excludes zero, d=-0.43)
- Prompt overhead breakeven: 7 messages vs JSON FC
- **Caveat**: Free English beats AXON on efficiency (16.3 tok/unit) but with 11.1% failure rate

### 5.3 Reliability Under Perturbation (Exp 2)
- **Table 4**: Structural preservation rate under character deletion, token swap, truncation
- English: 100% (trivially — any text passes)
- FIPA-ACL: 90% (lenient validation)
- AXON: 16.2%, JSON FC: 17.8% (similarly fragile)
- **Interpretation**: Strict syntax = fragile but provides "checksum effect" — corrupted messages are reliably detected, not silently degraded
- Interaction: perturbation type × condition is significant

### 5.4 Cross-Model Consistency (Exp 5)
- **Table 5**: Cross-model SD and CV by condition
- AXON: lowest variance on both tok/unit (SD=0.484) and composition rate (SD=0.048)
- JSON FC: highest variance (SD=2.09 tok/unit, SD=0.121 composition)
- Levene's test underpowered (n=3 models) but direction consistent

### 5.5 Error Taxonomy
- **Figure 1**: Error distribution by condition
- AXON: 94% bimodal (64% perfect, 30% compositional collapse, 6% mixed)
- English: nearly all partial composition (broad middle)
- JSON FC: 27% structural failure, 42% compositional collapse
- **Interpretation**: AXON produces clear success/failure signal; English degrades gracefully but ambiguously

### 5.6 Round-Trip Decomposition (Exp 3 Phase 2)
- 177 cross-model decompositions: Codex→Sonnet (63), Haiku→Codex (53), Sonnet→Haiku (61)
- 176/177 (99%) produced parseable JSON decompositions
- All conditions achieve high decomposition parseability (96–100%)
- Avg steps extracted: 4.8–6.5 per output; avg relationships: 5.3–7.8
- Nesting detected in 85–100% of outputs across conditions
- Sonnet→Haiku and Codex→Sonnet: 100% parseability; Haiku→Codex: 98%
- **Interpretation**: All formats are decomposable by a different model; the advantage of structured formats is in the *original composition*, not in downstream decomposability

### 5.7 JSON+Contracts vs AXON (Exploratory)
- Direct comparison of extrinsic contracts (SEMAP-inspired) vs intrinsic operators
- JSON+Contracts: 51.6% composition rate, 0% failure rate (81 cells, 3 models × 9 tasks × 3 runs)
- Contracts nearly double JSON FC's composition rate (+24.0%): extrinsic contracts DO help
- But AXON still leads by 15.4%: intrinsic operators provide additional benefit beyond contracts
- JSON+Contracts by model: Haiku 44.8%, Sonnet 57.2%, Codex 53.0%
- **Key finding**: Contracts and intrinsic operators operate at different levels — complementary, not substitutive

## 6. Discussion (~2 pages)

### 6.1 Intrinsic vs Extrinsic Compositionality
- The central finding: format-level syntax for composition (AXON's `->`, `&`, `|`) is more effective than contract-level rules (JSON+Contracts' `"relation": "sequence"`)
- This parallels programming language design: first-class features > library patterns
- SEMAP's contribution is real (contracts help) but operates at a different level than intrinsic syntax

### 6.2 The Reliability-Fragility Tradeoff
- Strict formats (AXON, JSON) are fragile under perturbation but provide clear error detection
- Lenient formats (English, FIPA-ACL) degrade gracefully but ambiguously
- For production multi-agent systems: prefer clear failure signals over ambiguous degradation
- ReliabilityBench's chaos-engineering framework could extend this analysis

### 6.3 Token Efficiency is Necessary but Not Sufficient
- AXON saves ~32% vs JSON FC — meaningful but not transformative
- Falling inference costs reduce the marginal value of efficiency
- The compositionality and reliability advantages are more durable
- Prompt overhead amortizes after ~7 messages (acceptable for multi-turn conversations)

### 6.4 Cross-Model Consistency as a Desirable Property
- AXON's lowest cross-model variance suggests more predictable behavior across LLMs
- Important for production systems that may swap models

### 6.5 Limitations
- 3 LLMs is thin for random-effects modeling (convergence caveats)
- AXON is out-of-distribution for all tested LLMs (training data bias)
- 9 tasks may not capture all real-world composition patterns
- English judge scoring may inflate composition rates for English conditions
- AISP and JSON+Contracts are exploratory (post-pre-registration)

## 7. Conclusion (~0.5 pages)

- First controlled comparison of 8 message content formats for LLM-to-LLM communication
- Intrinsic compositionality (native syntax operators) outperforms extrinsic contracts and implicit expression
- AXON achieves highest composition rate (66.2%), lowest cross-model variance, and competitive token efficiency
- The benchmark methodology is independently valuable: reusable task set, hybrid scoring, fairness protocol
- Format choice at the content layer matters, even when transport is standardized

## Appendices

### A. System Prompts (all 8 conditions)
### B. Task Descriptions and Expected Compositions
### C. Scoring Rubric and Judge Prompt
### D. Full Statistical Tables
### E. Pre-Registration and Deviation Notices
### F. AXON Grammar (EBNF)
