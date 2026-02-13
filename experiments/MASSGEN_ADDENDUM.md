# Exploratory MassGen Addendum

> Exploratory extension to the pre-registered AXON evaluation (Track A).
> Tests whether AXON's measured advantages survive in a realistic multi-agent orchestration environment.
> Frozen before any exploratory runs. All results labeled exploratory per deviation protocol (PREREGISTRATION.md:158-162).

## Motivation

The pre-registered experiments (Exp 0-5) test communication format in isolation via single LLM calls with controlled prompts. This is necessary for internal validity — it isolates the format variable from orchestration effects. But AXON's stated purpose is agent-to-agent communication in real multi-agent systems. If format advantages disappear when agents coordinate through an orchestration layer, the practical value of the finding is limited.

This addendum tests **ecological validity**: do pre-registered effects replicate when the same 6 conditions are embedded in MassGen's multi-agent coordination framework?

**Research question**: Does the format × orchestration interaction preserve, amplify, or eliminate the effects measured in isolation?

## Trigger Condition

This addendum activates only after **all of the following**:

1. Pre-registered Exp 0-5 analyses are complete and reported
2. At least one primary endpoint (Exp 1 or Exp 3) shows a statistically significant AXON advantage (d >= 0.5 after Holm-Bonferroni correction)
3. Pre-registered results are written up in publication-ready form

If AXON shows no significant advantage in the pre-registered experiments, this addendum does not run. There is nothing to test for ecological validity if the base effect does not exist.

## Scope

### Experiments Replicated

Two experiments are replicated — the two where multi-agent realism is most relevant:

| Prereg Exp | Addendum ID | Rationale |
|------------|-------------|-----------|
| Exp 3: Compositionality | MG-3 | AXON's composition operators (`->`, `<-`, `&`, `\|`) are designed for multi-agent coordination. Testing whether they help when agents actually coordinate (not just generate static messages) is the highest-value ecological test. |
| Exp 4: Multi-Turn Coherence | MG-4 | Reply threading, context maintenance, and performative transitions are inherently conversational. MassGen's multi-turn buffer provides a realistic conversation environment. |

Exp 0 (learnability), Exp 1 (token efficiency), and Exp 5 (cross-model variance) are not replicated because they measure properties of individual messages, not agent interactions. Exp 2 (parse accuracy under noise) tests robustness to perturbation, which is orthogonal to orchestration.

### Conditions

Same 6 conditions as pre-registered (PREREGISTRATION.md:12-18). MassGen is infrastructure, not a condition. All conditions use identical MassGen configuration.

1. Free-form English
2. Structured English
3. Instruction-matched English
4. JSON Function Calling
5. FIPA-ACL
6. AXON

## MassGen Configuration

### Version Pin

```
massgen == <version pinned at time of first run>
```

Record the exact version in the results file. If MassGen releases a breaking change mid-experiment, complete all remaining cells on the pinned version before considering an upgrade.

### Frozen YAML Configuration

```yaml
# experiments/massgen/config_base.yaml
# Shared across ALL 6 conditions — do not modify per-condition.

agents:
  - id: "agent_alpha"
    backend:
      type: "<model_family_1>"       # e.g., "claude"
      model: "<model_1>"             # e.g., "claude-sonnet-4-5-20250929"
      temperature: 0.0
      max_tokens: 4096
    system_message: "${CONDITION_PROMPT}"  # Injected per-condition

  - id: "agent_beta"
    backend:
      type: "<model_family_1>"
      model: "<model_1>"
      temperature: 0.0
      max_tokens: 4096
    system_message: "${CONDITION_PROMPT}"

  - id: "agent_gamma"
    backend:
      type: "<model_family_1>"
      model: "<model_1>"
      temperature: 0.0
      max_tokens: 4096
    system_message: "${CONDITION_PROMPT}"

orchestrator:
  coordination:
    voting_sensitivity: "balanced"
    max_new_answers_per_agent: 3
    max_new_answers_global: null
    answer_novelty_requirement: "lenient"   # Do not filter format-specific outputs
    fairness_enabled: true
    fairness_lead_cap_answers: 2
    max_midstream_injections_per_round: 3
    enable_planning_mode: false             # No dry-run — measure raw coordination
    persona_generator:
      enabled: false                        # No persona diversity — isolate format variable
  dspy:
    enabled: false                          # No question paraphrasing — same task across agents

timeout:
  orchestrator_timeout_seconds: 300
  initial_round_timeout_seconds: 120
  subsequent_round_timeout_seconds: 90
  round_timeout_grace_seconds: 60

ui:
  display_type: "headless"
  logging_enabled: true
```

### What Varies Per Condition

Only the `system_message` field changes. Each condition's system message is the same prompt used in the pre-registered experiments, extended with a MassGen coordination preamble:

```
You are one of several agents coordinating on a task. When communicating
with other agents (via ask_others or in your answers), use the following
format: [CONDITION-SPECIFIC FORMAT INSTRUCTIONS FROM PREREG PROMPT]
```

The preamble is identical across conditions (only the format instructions differ). Preamble token count is recorded and reported.

### What Is Held Constant

- Agent count: 3 per task (matches Exp 3 design)
- Model: same model for all agents within a run (within-subjects, matching prereg)
- Temperature: 0.0
- MassGen coordination settings: identical across conditions
- Diversity mechanisms: all disabled (persona generation off, DSPy paraphrasing off, novelty requirement lenient)
- Timeout configuration: identical

## MG-3: Compositionality in Orchestration

### Design

Replicates Exp 3's four tasks in a live multi-agent environment:

| Task | Agents | What Changes vs Prereg |
|------|--------|----------------------|
| Info aggregation | 3 agents each hold partial data | Agents actually exchange messages via MassGen instead of generating static composed messages |
| Scheduling | 3 agents with availability constraints | Agents negotiate through MassGen's coordination rounds instead of producing a single composed proposal |
| Pipeline | 3 agents in processing chain | Agents pass intermediate results through `ask_others()` instead of expressing the full pipeline in one message |
| Consensus | 3 agents voting on options | Agents use MassGen's native voting + format-specific proposals |

### Primary Endpoint

**Orchestrated composition success rate**: Proportion of tasks where agents successfully coordinate to produce the correct outcome, as judged by the same 3-way LLM panel (FAIRNESS.md:30-47).

### Secondary Endpoints

- **Format adherence rate**: Proportion of inter-agent messages that conform to the specified format (did agents actually use AXON/JSON/English as instructed, or did they drift to natural language?)
- **Coordination rounds to completion**: Number of MassGen orchestration rounds before consensus
- **Total tokens consumed**: Across all agents and rounds (comparable to prereg Exp 3 token counts, adjusted for orchestration overhead)

### Comparison to Prereg

The key analysis is the **format × setting interaction**:

```
outcome ~ condition * setting + (1|task) + (1|model)
```

Where `setting` is a 2-level factor: `isolated` (prereg) vs. `orchestrated` (MassGen). A significant interaction means the format's effect changes under orchestration. Report:

- Main effect of condition (does format still matter?)
- Main effect of setting (does orchestration help or hurt overall?)
- Interaction (does orchestration differentially affect some formats?)

## MG-4: Multi-Turn Coherence in Orchestration

### Design

Replicates Exp 4's 5-turn conversation protocol, but agents converse through MassGen's buffer injection mechanism instead of generating a monolithic 5-turn transcript.

- 2 agents per conversation (matches Exp 4's dyadic design)
- Each agent takes turns responding, with MassGen managing the conversation buffer
- Same rubric dimensions: reply threading, context maintenance, performative appropriateness

### Primary Endpoint

**Orchestrated coherence score**: Average across rubric dimensions, judged by the 3-way LLM panel on the actual conversation transcript extracted from MassGen logs.

### Secondary Endpoints

- **Reply-link accuracy**: Does the conversation maintain correct threading through MassGen's buffer?
- **Format drift rate**: At which turn do agents start deviating from the specified format (if at all)?
- **Buffer injection fidelity**: Does MassGen's anonymized answer sharing preserve the format-specific structure?

### Comparison to Prereg

Same interaction analysis as MG-3:

```
coherence ~ condition * setting + (1|task) + (1|model)
```

## Statistical Analysis

### Relationship to Pre-Registered Analyses

Pre-registered results are reported first, in full, without modification. Exploratory results are reported in a separate section clearly labeled "Exploratory: Ecological Validity Extension."

### Analysis Plan

- Same mixed-effects framework as prereg (PREREGISTRATION.md:108-116)
- Additional fixed effect: `setting` (isolated vs. orchestrated)
- Additional interaction term: `condition × setting`
- Same multiple comparison correction: Holm-Bonferroni across 5 pairwise comparisons per experiment
- Effect sizes: Cohen's d with 95% bootstrap CIs (BCa, 10,000 resamples)

### Variance Contingency

MassGen's orchestration may inflate variance (non-deterministic coordination timing, buffer injection ordering). If observed variance in MG-3 or MG-4 exceeds 2x the prereg variance for the same experiment:

1. Increase runs from 3 to 6 per cell to maintain power
2. Report the variance inflation factor
3. Discuss whether orchestration-induced variance is a meaningful finding (some formats may be more robust to orchestration noise than others)

### Sample Size

- MG-3: 4 tasks × 6 conditions × N models × 3 runs = 72N observations (minimum 72 with 1 model, target 144 with 2 models)
- MG-4: 9 tasks × 6 conditions × N models × 3 runs = 162N observations (matching prereg)
- Variance contingency: double runs if needed (6 per cell)

## Reporting

### Required

- All endpoints with 95% CIs
- Format × setting interaction tests with effect sizes
- Format adherence rate (critical: if agents don't use the specified format under orchestration, the result is about format robustness, not format effectiveness)
- MassGen version, configuration hash, and full YAML
- Comparison table: prereg effect size vs. exploratory effect size per condition pair

### Interpretation Guide

| Scenario | Interpretation |
|----------|---------------|
| Prereg effect replicates under orchestration (interaction n.s.) | AXON advantage is robust to realistic deployment |
| Prereg effect amplifies under orchestration (significant positive interaction) | Structured formats benefit more from orchestration (strongest result) |
| Prereg effect disappears under orchestration (significant negative interaction) | Format advantages are artifacts of isolated testing; practical value is limited |
| Agents drift away from specified format under orchestration | The format's learnability doesn't persist under coordination pressure; report format drift as a finding |

## Limitations

1. **Single orchestration framework**: Results are specific to MassGen's coordination mechanism (anonymous buffer injection, voting-based consensus). Other frameworks (AutoGen, CrewAI, LangGraph) may interact differently with format.
2. **Orchestration overhead**: MassGen adds coordination tokens that are independent of format. This inflates total token counts. Net format-specific tokens should be reported alongside gross totals.
3. **Framework maturity**: MassGen is actively maintained but relatively new. Pin the version and report any bugs or unexpected behaviors encountered.
4. **Not pre-registered**: This entire addendum is exploratory. Effect sizes and p-values should be interpreted as hypothesis-generating, not confirmatory.
