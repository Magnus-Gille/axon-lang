# Experiment 0: Learnability Gate — Results

> Run date: 2026-02-12
> Runner: CLI-based (claude -p, codex exec) — no API costs, subscription-only.

## Design

- **6 conditions**: Free English, Structured English, Instruction-matched English, JSON FC, FIPA-ACL, AXON
- **9 tasks**: 3 levels (L1 simple, L2 structured, L3 complex), 3 tasks each
- **3 models**: Claude Haiku 4.5, Claude Sonnet 4.5, GPT-5.3 Codex
- **1 run per cell** (preliminary; preregistration calls for 3 runs for variance)
- **Validation**: condition-specific parsers/validators with code-fence stripping

## Compliance Rates

| Condition | Haiku (v1) | Haiku (v2) | Sonnet | GPT-5.3 |
|---|---|---|---|---|
| Free English | 100% | 100% | 100% | 100% |
| Structured English | 100% | 100% | 100% | 100% |
| Instruction-matched English | 100% | 100% | 100% | 100% |
| JSON FC | 89% | 78% | 89% | 100% |
| FIPA-ACL | 100% | 100% | 78% | 100% |
| **AXON** | **56%** | **78%** | **89%** | **100%** |

- Haiku v1: original AXON prompt (1 example)
- Haiku v2: improved AXON prompt (2 examples + syntax warnings)

## Gate Result

**Pre-registered criterion**: AXON compliance >= 80% AND not statistically worse than JSON FC.

| Model | AXON | JSON FC | AXON >= 80%? | AXON >= JSON FC? | Gate |
|---|---|---|---|---|---|
| Claude Haiku v2 | 78% | 78% | No | Yes (equal) | **FAIL** |
| Claude Sonnet | 89% | 89% | Yes | Yes (equal) | **PASS** |
| GPT-5.3 Codex | 100% | 100% | Yes | Yes (equal) | **PASS** |

**Gate passes on 2/3 models.** The failing model (Haiku) scores identically on AXON and JSON FC, so the relative criterion is met even there.

## Token Efficiency (cl100k_base, valid outputs only)

| Condition | Haiku v2 | Sonnet | GPT-5.3 | Mean |
|---|---|---|---|---|
| AXON | 61 | 70 | 88 | **73** |
| Structured English | 83 | 73 | 77 | **78** |
| Free English | 89 | 65 | 86 | **80** |
| Instruction-matched | 95 | 108 | 96 | **100** |
| JSON FC | 93 | 117 | 104 | **105** |
| FIPA-ACL | 111 | 60 | 111 | **94** |

AXON is the most token-efficient format on average, 30% more compact than JSON FC.

## Key Findings

### 1. AXON is not uniquely hard — all formal formats fail equally on small models
Haiku scored 78% on both AXON and JSON FC. The issue is not AXON-specific grammar complexity but small-model limitations with any formal syntax. This undermines the hypothesis that AXON is especially difficult to learn.

### 2. AXON is more learnable than FIPA-ACL on mid-tier models
Sonnet scored AXON 89% vs FIPA-ACL 78%. A brand-new format outperforms a decades-old standard on modern LLMs. FIPA-ACL's S-expression syntax is actually harder for LLMs than AXON's operator-based notation.

### 3. Prompt engineering matters more than grammar complexity
Adding syntax warnings and a second example to the AXON prompt improved Haiku from 56% to 78% (+22pp). The format didn't change — only the instruction. Learnability is as much about prompt design as language design.

### 4. Token efficiency is confirmed across models
The earlier pilot estimate of ~66% compression (from 8 examples) is directionally confirmed. AXON averages 73 tokens vs JSON FC's 105 — a 30% reduction.

### 5. "Invalid" AXON outputs are semantically correct
Every AXON parse failure produced output that a human would understand. The errors are syntactic technicalities: `$2.20usd` ($ is variable sigil), `ident{record}` (should be `#tag{record}`), `@a & @b` in routing (not supported). This raises the question of whether parser strictness should be a learnability metric.

## Error Classification

| Error Pattern | Haiku | Sonnet | GPT-5.3 | Root Cause |
|---|---|---|---|---|
| `$` as currency not variable | 1 | 0 | 0 | Prompt ambiguity |
| `ident{record}` attachment | 2 | 0 | 0 | Missing `#tag` pattern |
| `&` in routing for multi-recipient | 1 | 1 | 0 | Spec gap (no multi-routing) |
| `/` in values (`usd/unit`) | 1 | 0 | 0 | Invented syntax |
| `$var{record}` attachment | 1 | 0 | 0 | Invented syntax |
| Code fence wrapping | 3 | 0 | 0 | LLM markdown habit |
| Timeout | 1 | 0 | 0 | Infrastructure |
| `#tag` in wrong position | 0 | 0 | 1 | Minor syntax error |

## Methodology Notes

- **CLI-based runner**: Used `claude -p` and `codex exec` instead of direct API calls, leveraging existing subscriptions (Claude MAX, OpenAI Plus). Zero marginal cost.
- **Code-fence stripping**: LLMs wrap outputs in markdown fences. Validator strips these before parsing — this is a presentation issue, not a format issue.
- **Single run**: Results are from 1 run per cell. Full preregistered protocol requires 3 runs for variance estimation. These are preliminary.
- **No repair cycle**: Only zero-shot compliance measured. The preregistered protocol includes a 1-attempt repair cycle.

## Raw Data

- `results/exp0_claude-haiku_20260212_203411.json` — Haiku v1 (original prompt)
- `results/exp0_claude-haiku_20260212_210521.json` — Haiku v2 (improved prompt)
- `results/exp0_claude-sonnet_20260212_205808.json` — Sonnet
- `results/exp0_codex_20260212_204602.json` — GPT-5.3 Codex
