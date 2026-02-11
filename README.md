# AXON — Agent eXchange Optimized Notation

> **Status**: Draft v0.1 — promising concept, not validated standard. Efficiency claims are hypotheses pending benchmarking.

A purpose-built language for agent-to-agent communication, designed from first principles using information theory, formal linguistics, and multi-agent systems research.

## Why Not English?

English is **50-75% redundant** over digital channels (Shannon, 1951), pervasively ambiguous at every linguistic level, and optimized for human cognitive constraints that don't apply to AI agents. Research shows:

- **Shannon (1951)**: English carries 0.6-1.3 bits/char vs. 4.7 bits/char theoretical max [Established]
- **LLMLingua** (Microsoft, EMNLP 2023): Natural language prompts compress 2-20x with minimal loss [Supported]
- **Agora Protocol** (Oxford, 2024): Agents using natural language cost ~5x more than those with efficient protocols [Supported]
- **FIPA-ACL/KQML**: Decades of research showing speech-act semantics improve agent coordination [Established]

Whether AXON's density advantage justifies adoption over controlled English + function calling is an empirical question — see the full analysis in **[RESEARCH.md](RESEARCH.md)**.

## Quick Look

```
(* Query: "What is the status of the web server?" *)
QRY(@a>@b): status(@web-server)

(* Reply: "Healthy, 99.7% uptime, 45ms latency" *)
RPL(@b>@a): {status:#healthy, uptime:99.7%, latency:45ms}

(* Chain: "Fetch, parse as JSON, then store in DB" *)
REQ(@orchestrator>@worker): fetch($url) -> parse(#json) -> store(@db, $result)

(* Propose: "Migrate to Server-2 between 2-4 AM" *)
PRO(@a>@b): {action:#migrate, target:@server-2, window:"02:00-04:00"}

(* Counter: "4-6 AM instead, because of peak load" *)
CTR(@b>@a): {action:#migrate, target:@server-2, window:"04:00-06:00"} <- load.peak("02:00-03:00")

(* Accept *)
ACC(@a>@b): _
```

## Key Design Principles

| Principle | How AXON Achieves It |
|-----------|---------------------|
| **Zero ambiguity** | Context-free EBNF grammar with exactly one parse per expression |
| **Speech-act semantics** | 20 core performatives with formal preconditions and effects |
| **Token efficiency** | Symbols replace verbose keywords (`>` not "addressed to", `#` not "of type") |
| **Compositionality** | `->` chains, `&` parallelism, `<-` causation, `\|` disjunction |
| **Typed content** | Numbers with units (`45ms`), booleans (`T`/`F`), refs (`@agent`), tags (`#type`) |
| **Three compliance tiers** | Core Valid → Interop Compliant → Production Certified |
| **Plain text** | Pure ASCII with common symbols — no binary encoding needed |

## Language Structure

Every AXON message is a speech act:

```
[metadata]
PERFORMATIVE(@sender>@receiver): content
```

### Performatives

**Information**: `INF` (inform), `QRY` (query), `RPL` (reply), `CFM` (confirm), `DNY` (deny), `ERR` (error)

**Action**: `REQ` (request), `CMD` (command), `PRO` (propose), `ACC` (accept), `REJ` (reject), `CTR` (counter), `DEL` (delegate), `CAN` (cancel)

**State**: `SUB` (subscribe), `UNS` (unsubscribe), `PUB` (publish), `ACK` (acknowledge), `NAK` (negative ack), `SYN` (synchronize)

**Extension**: `X.domain.act` for domain-specific performatives

### Type System

```
"hello"          (* String *)
42               (* Integer *)
3.14             (* Float *)
T / F            (* Boolean *)
_                (* Null *)
@agent-name      (* Reference *)
#category        (* Tag *)
$variable        (* Variable *)
[1, 2, 3]       (* List *)
{key:val}        (* Record *)
0..100           (* Range *)
45ms             (* Number with unit *)
*                (* Wildcard endpoint *)
```

### Compliance Tiers

```
(* Tier 1 — Core Valid *)
[id:"m1", %%:1]
QRY(@a>@b): status(@x)

(* Tier 2 — Interop Compliant *)
[id:"m2", %%:1, re:"m1", ts:1707600000, ctx:"conv-42"]
RPL(@b>@a): {status:#healthy, uptime:99.7%}

(* Tier 3 — Production Certified *)
[id:"m3", %%:1, sig:"ed25519:...", authz:"role:admin", tenant:"acme"]
CMD(@admin>@server): restart()
```

## Repository Structure

```
.
├── README.md                        # This file
├── RESEARCH.md                      # Research rationale with evidence tiers (20+ sources)
├── LICENSE                          # MIT License
├── spec/
│   └── SPECIFICATION.md             # Full language spec (EBNF grammar, 3 compliance tiers)
├── examples/
│   ├── basic.axon                   # Basic examples (8 messages)
│   ├── advanced.axon                # Complex patterns (11 messages)
│   ├── real_world_scenarios.axon    # CI/CD, incident response, fleet coordination (30 messages)
│   └── comparisons.md              # Side-by-side English vs AXON (pilot data)
├── src/
│   └── axon_parser.py              # Reference parser (Python, recursive descent)
└── debate/                          # Adversarial review (Claude vs Codex, 4 rounds)
    ├── summary.md                   # Debate summary and outcomes
    ├── codex-research-critique.md   # 53-point research critique
    ├── codex-spec-critique.md       # ~50-point spec critique (12 bugs found)
    ├── claude-response-1.md         # First response
    ├── codex-rebuttal-1.md          # Codex rebuttal
    ├── claude-response-2.md         # Final response
    └── codex-rebuttal-2.md          # Final assessment
```

## Using the Parser

```bash
# Parse and validate
python3 src/axon_parser.py examples/basic.axon

# Show full AST
python3 src/axon_parser.py --ast examples/basic.axon

# Validate only
python3 src/axon_parser.py --check examples/basic.axon

# Parse from stdin
echo 'QRY(@a>@b): status(@server)' | python3 src/axon_parser.py -
```

The reference parser supports all v0.1 features: 20 core performatives, extension performatives (`X.domain.act`), 7-level operator precedence, comparison operators, named arguments, wildcard routing, dotted qualified identifiers, and three-tier metadata.

## Research Sources

Full citations with evidence tiers in [RESEARCH.md](RESEARCH.md). Key sources:

- Shannon (1951) — Information entropy of English [Established]
- Coupé et al. (2019) — Universal ~39 bits/second rate (*Science Advances*) [Established]
- LLMLingua (Microsoft, EMNLP 2023 / ACL 2024) — Prompt compression [Supported]
- FIPA-ACL / KQML — Speech-act based agent communication [Established]
- Lojban / Lojban++ (Goertzel, 2013) — Unambiguous language design [Established]
- Agora Protocol (Oxford, 2024) — Meta-protocol for LLM networks [Supported]
- LACP (NeurIPS 2025) — Telecom-inspired agent protocol [Supported]
- TOON (2025) — Token-optimized notation [Supported]
- AI Agent Protocol Survey (arXiv:2504.16736, 2025) — Protocol taxonomy [Established]

## Development Process

This language was designed through a structured process:

1. **Research synthesis** — 20+ sources across information theory, linguistics, AI, and multi-agent systems
2. **Language design** — EBNF grammar, speech-act semantics, token-efficient encoding
3. **Reference implementation** — Recursive descent parser in Python
4. **Adversarial review** — 4-round structured debate between Claude (Opus 4.6) and Codex (GPT-5.3), resolving ~85% of ~100 critique points
5. **Revision** — All debate-agreed changes incorporated into spec, parser, and research document
