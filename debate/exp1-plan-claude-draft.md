# Exp 1: Token Efficiency — Implementation Plan

> DRAFT — pending adversarial review before implementation.

## Research Question

How many tokens does each format need to convey the same semantic content? Is AXON measurably more token-efficient than controlled alternatives?

## Primary Metric

**tokens_per_semantic_unit** = `token_count / semantic_elements_correctly_expressed`

Measured across both `cl100k_base` (GPT-4) and `o200k_base` (GPT-4o) encodings.

## Secondary Metrics

- Raw token counts by condition (already collected in Exp 0)
- Prompt token overhead per condition (system prompt token counts)
- Information density curves (elements vs tokens, by complexity level)
- Token variance within condition (SD across runs)

---

## Data Source: Reuse Exp 0 Outputs

**Proposal**: Reuse the 486 outputs already collected in Exp 0 (3 models x 6 conditions x 9 tasks x 3 runs). No new LLM data generation needed.

**Rationale**:
- The preregistration defines "6 conditions x 9 tasks x N models" as the overall study design — experiments measure different endpoints from the same output corpus
- Exp 0 prompts instruct "Respond with ONLY the message in the required format" — outputs are pure format with no commentary, exactly what token efficiency needs
- Token counts already collected; only semantic element scoring is new
- All 3 models at 3 runs per cell = 81 observations per condition (above the 54 minimum, below the 162 target in the preregistration)

**Risk**: If Exp 0 tasks turn out to be poorly suited for density measurement (e.g., tasks don't vary element count enough), we add supplementary tasks. But the 9 existing tasks span 4–22 elements, which is a 5.5x range — likely sufficient.

---

## Design Decision 1: Semantic Element Taxonomy

A "semantic element" is a single, atomic piece of information that the task requires the output to express. Elements are defined at the task level (ground truth) and scored at the output level (did this output express it?).

### Element Categories

| Category | Description | Example | Count Rule |
|----------|-------------|---------|------------|
| **Identity** | Sender or receiver agent | `@agent-a`, `"agent-a"` | 1 per distinct agent referenced |
| **Intent** | Performative / speech act | `QRY`, `"query"`, "asks" | 1 per message |
| **Content-fact** | A distinct fact, value, or parameter | `uptime:99.7%`, `"branch":"main"` | 1 per atomic key-value or fact |
| **Metadata** | Protocol envelope field | `id:"m1"`, `"timestamp":...` | 1 per field (only when task requires) |
| **Structural** | Composition operator | `->` (sequence), `&` (parallel) | 1 per operator instance |
| **Causal** | Causal relationship | `<-` (because), "caused by" | 1 per causal link |
| **Threading** | Reply linkage between messages | `re:"m1"`, "in reply to" | 1 per correct link |

### Counting Principles

1. **Atomicity**: `{repo:"acme", branch:"main", commit:"abc123"}` = 3 content-facts, not 1 record
2. **Task-grounded**: Only elements explicitly required by the task instruction count. Bonus elements don't add to the score (but don't penalize either)
3. **Multi-message tasks**: Element count spans all required messages. A 3-message conversation with threading has elements from all 3 messages
4. **Receivers**: Multi-agent routing (`@w1, @w2, @w3`) counts as 3 identity elements if the task specifies 3 workers

---

## Design Decision 2: Task Element Annotations

Precise element enumeration for each of the 9 Exp 0 tasks:

### L1-01: Simple Status Query (4 elements)
| # | Element | Category | What to check |
|---|---------|----------|---------------|
| 1 | Sender = agent A | Identity | Any reference to the sending agent |
| 2 | Receiver = agent B | Identity | Any reference to the receiving agent |
| 3 | Query intent | Intent | Query/ask performative expressed |
| 4 | Target = web server | Content-fact | The server being queried |

### L1-02: Simple Inform (5 elements)
| # | Element | Category | What to check |
|---|---------|----------|---------------|
| 1 | Sender = agent B | Identity | Sending agent |
| 2 | Receiver = agent A | Identity | Receiving agent |
| 3 | Inform intent | Intent | Inform/tell performative |
| 4 | Status = healthy | Content-fact | Server health status |
| 5 | Uptime = 99.7% | Content-fact | Numeric uptime value |

### L1-03: Simple Error Report (5 elements)
| # | Element | Category | What to check |
|---|---------|----------|---------------|
| 1 | Sender = service agent | Identity | Sending agent |
| 2 | Receiver = caller agent | Identity | Receiving agent |
| 3 | Error intent | Intent | Error performative |
| 4 | Error code = 404 | Content-fact | Numeric error code |
| 5 | Error description = not found | Content-fact | Human-readable description |

### L2-01: Request with Structured Data (6 elements)
| # | Element | Category | What to check |
|---|---------|----------|---------------|
| 1 | Sender = CI agent | Identity | Sending agent |
| 2 | Receiver = builder agent | Identity | Receiving agent |
| 3 | Request intent | Intent | Request/command performative |
| 4 | Repository name | Content-fact | Some repo identifier |
| 5 | Branch name | Content-fact | Some branch identifier |
| 6 | Commit hash/ref | Content-fact | Some commit identifier |

### L2-02: Proposal with Counter (11 elements)
| # | Element | Category | What to check |
|---|---------|----------|---------------|
| 1 | Sender = supplier | Identity | First message sender |
| 2 | Receiver = buyer | Identity | First message receiver |
| 3 | Propose intent | Intent | Proposal performative |
| 4 | Item = widgets | Content-fact | Product identifier |
| 5 | Quantity = 10000 | Content-fact | Numeric quantity |
| 6 | Price = $2.50 | Content-fact | Per-unit price |
| 7 | Counter sender = buyer | Identity | Second message sender |
| 8 | Counter intent | Intent | Counter performative |
| 9 | Counter price = $2.20 | Content-fact | Counter offer amount |
| 10 | Market average = $2.15 | Content-fact | Justification data point |
| 11 | Justification present | Content-fact | Some reasoning for counter |

### L2-03: Multi-Agent Task Distribution (9 elements)
| # | Element | Category | What to check |
|---|---------|----------|---------------|
| 1 | Sender = planner | Identity | Sending agent |
| 2 | Receiver = worker 1 | Identity | First recipient |
| 3 | Receiver = worker 2 | Identity | Second recipient |
| 4 | Receiver = worker 3 | Identity | Third recipient |
| 5 | Request intent | Intent | Command/request performative |
| 6 | Task type = data processing | Content-fact | What kind of task |
| 7 | Range segment 1 (0-1000) | Content-fact | First data range |
| 8 | Range segment 2 (1001-2000) | Content-fact | Second data range |
| 9 | Range segment 3 (2001-3000) | Content-fact | Third data range |

### L3-01: Chained Pipeline with Metadata (8 elements)
| # | Element | Category | What to check |
|---|---------|----------|---------------|
| 1 | Sender = orchestrator | Identity | Sending agent |
| 2 | Receiver = pipeline agent | Identity | Receiving agent |
| 3 | Request intent | Intent | Request performative |
| 4 | Action 1: fetch URL | Structural | First pipeline step |
| 5 | Action 2: parse as JSON | Structural | Second pipeline step |
| 6 | Action 3: store in database | Structural | Third pipeline step |
| 7 | Message ID present | Metadata | id field |
| 8 | Protocol version present | Metadata | version/protocol field |

### L3-02: Incident Response with Causal Chain (10 elements)
| # | Element | Category | What to check |
|---|---------|----------|---------------|
| 1 | Sender = monitor | Identity | Sending agent |
| 2 | Receiver (any) | Identity | Receiving agent |
| 3 | Alert/publish intent | Intent | Alert performative |
| 4 | Severity = 2 | Content-fact | Severity level |
| 5 | Priority = 4 | Content-fact | Priority level |
| 6 | Service = payments | Content-fact | Affected service |
| 7 | Latency > 2s | Content-fact | Threshold value |
| 8 | Causal: pool exhaustion | Causal | First causal link |
| 9 | Causal: traffic spike | Causal | Root cause |
| 10 | Resolution recommendation | Content-fact | Suggested fix |

### L3-03: Full Conversation with Threading (22 elements)
| # | Element | Category | What to check |
|---|---------|----------|---------------|
| 1-3 | 3x message IDs | Metadata | Each message has id |
| 4-6 | 3x protocol versions | Metadata | Each message has version |
| 7-9 | 3x timestamps | Metadata | Each message has timestamp |
| 10-11 | 2x reply-to links | Threading | Messages 2,3 link to prior |
| 12 | Msg 1: sender A | Identity | Query sender |
| 13 | Msg 1: receiver B | Identity | Query receiver |
| 14 | Msg 1: query intent | Intent | Diagnostic query |
| 15 | Msg 2: sender B | Identity | Reply sender |
| 16 | Msg 2: receiver A | Identity | Reply receiver |
| 17 | Msg 2: reply intent | Intent | Reply performative |
| 18 | Msg 2: bottleneck info | Content-fact | Diagnostic finding |
| 19 | Msg 2: connection stats | Content-fact | Numeric stats |
| 20 | Msg 3: sender A | Identity | Request sender |
| 21 | Msg 3: receiver B | Identity | Request receiver |
| 22 | Msg 3: request scaling | Intent+Content | Scaling request |

**Element count distribution**: 4, 5, 5, 6, 11, 9, 8, 10, 22 — mean 8.9, range [4, 22]

---

## Design Decision 3: Scoring Approach

### LLM Judge with Element Checklist

For each (task, condition, output) triple, an LLM judge receives:
1. The task instruction
2. The complete element checklist for that task
3. The raw output

The judge marks each element as:
- **present_correct** (1): Element is expressed accurately
- **present_incorrect** (0): Element is expressed but wrong (e.g., wrong value)
- **absent** (0): Element is not expressed at all

**Score** = count(present_correct) / total_elements

### Judge Configuration

**2-judge panel** (not 3-way):
- Judge A: Claude Sonnet (via `claude -p`)
- Judge B: GPT-5.3 Codex (via `codex exec`)
- Agreement rule: Both must agree. Disagreements flagged for manual review
- Checklist scoring is low-ambiguity (element present or not), so 2 judges should suffice

**Rationale for 2 vs 3 judges**: The FAIRNESS.md 3-way protocol is designed for subjective quality assessment (Exp 3, Exp 4). Element presence/absence is near-binary — "Is there a sender agent? Is there a 404 code?" — so the marginal value of a third judge is low. We validate this assumption by measuring inter-judge agreement on a calibration set.

### Judge Prompt Template

```
You are scoring an agent-to-agent communication message for information completeness.

TASK: {task_instruction}

REQUIRED ELEMENTS:
{numbered_element_checklist}

OUTPUT TO SCORE:
{raw_output}

For each required element, respond with EXACTLY one line:
{element_number}. PRESENT — {brief justification}
OR
{element_number}. ABSENT — {what's missing}
OR
{element_number}. INCORRECT — {what's wrong}

Score every element. Do not skip any.
```

### Calibration

Before scoring all 486 outputs:
1. Manually score 18 outputs (1 per condition x 3 tasks spanning L1-L3) as ground truth
2. Run both judges on these 18
3. Compute judge vs ground-truth agreement (target: >90% per-element)
4. If agreement is low, refine prompt and re-calibrate

---

## Design Decision 4: Handling Invalid Outputs

Exp 0 had some invalid outputs (validation failures). Two approaches:

**Option A (Include)**: Invalid outputs are scored for semantic elements normally. An output that fails AXON parsing but still contains recognizable elements gets partial credit. Token efficiency = tokens / elements_present.

**Option B (Exclude)**: Invalid outputs are excluded from the token efficiency analysis entirely. Only valid outputs contribute.

**Chosen: Option A (Include)** — with a sensitivity analysis excluding invalids.

Rationale: Token efficiency is about format expressiveness, not just valid outputs. A format where you must write 200 tokens to express 5 elements (but it parses) is less efficient than one where 50 tokens express 5 elements (even if it sometimes doesn't parse). However, we report both analyses.

---

## Design Decision 5: Statistical Analysis

Per preregistration:

### Primary Analysis
Mixed-effects model:
```
tokens_per_unit ~ condition + (1|task) + (1|model)
```
- `condition`: fixed effect (6 levels, AXON as reference)
- `task`: random intercept (accounts for task difficulty variation)
- `model`: random intercept (accounts for model verbosity differences)

### Pairwise Comparisons
5 pairwise tests: AXON vs {free_english, structured_english, instruction_matched_english, json_fc, fipa_acl}
- Holm-Bonferroni correction (α = 0.05)
- Report both corrected and uncorrected p-values

### Effect Sizes
- Cohen's d for each pairwise comparison
- 95% bootstrap CI (10,000 resamples, BCa method)

### Both Encodings
All analyses run independently on cl100k_base and o200k_base. Report both; use cl100k_base as primary.

---

## Implementation

### Directory Structure
```
experiments/exp1_token_efficiency/
├── PLAN.md                        # This file
├── tasks/
│   └── element_annotations.json   # Ground truth element definitions
├── scoring/
│   ├── score.py                   # LLM judge-based element scorer
│   └── judge_prompt.txt           # Judge prompt template
├── analysis/
│   └── analyze.py                 # Statistical analysis pipeline
├── results/                       # Scored outputs + analysis artifacts
└── run.py                         # Orchestrator
```

### Dependencies
- Existing: `tiktoken`, `axon_parser` (stdlib)
- New: `scipy` (for mixed-effects bootstrap CI) or `statsmodels` (for `mixedlm`)
- Add to `experiments/requirements.txt`

### Run Protocol
```bash
# Step 1: Score semantic elements in Exp 0 outputs
python3 experiments/exp1_token_efficiency/run.py --score

# Step 2: Run statistical analysis
python3 experiments/exp1_token_efficiency/run.py --analyze

# Step 3: Both steps
python3 experiments/exp1_token_efficiency/run.py --all

# Dry run (show what would be scored)
python3 experiments/exp1_token_efficiency/run.py --dry-run
```

### Data Flow
```
Exp 0 result JSONs (existing)
    ↓
Element Scorer (LLM judge calls)
    ↓
Scored results JSON (output + element scores + token counts)
    ↓
Analysis script
    ↓
Results table + effect sizes + plots
```

---

## Open Questions for Adversarial Review

1. **Data reuse**: Is it methodologically sound to reuse Exp 0 outputs for Exp 1, or does the preregistration imply independent data collection?
2. **Element taxonomy**: Is the taxonomy well-defined enough to be reproducible? Are there edge cases where element boundaries are ambiguous?
3. **2-judge vs 3-judge**: Is dropping to 2 judges for checklist scoring defensible, or does it weaken the FAIRNESS.md commitment?
4. **Include invalids**: Should invalid outputs be included in the efficiency metric or excluded?
5. **Sample size**: 81 per condition (3 models x 9 tasks x 3 runs) — sufficient for medium effects?
6. **Confound — prompt length**: AXON's prompt is 48 lines vs free English's 1 line. Should the efficiency metric account for prompt token overhead?
7. **Confound — multi-message tasks**: L2-02 (2 messages) and L3-03 (3 messages) include threading overhead that disproportionately affects some formats. Should these be analyzed separately?
8. **Density metric pathology**: If an output scores 0 semantic elements but has >0 tokens, tokens/elements is undefined. How to handle?
9. **Element weighting**: All elements count equally. Is sender identity (trivial) really as informative as a causal chain (complex)? Should elements be weighted?
