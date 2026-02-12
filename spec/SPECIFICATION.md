# AXON Language Specification — v0.1-experimental

## Agent eXchange Optimized Notation

> **Status**: v0.1-experimental. Efficiency claims are hypotheses pending benchmarking.

---

## 1. Design Goals

AXON is a plain-text language designed for efficient agent-to-agent communication. It targets:

1. **Information density**: Minimum tokens/characters per unit of meaning
2. **Unambiguous grammar**: Every valid expression has exactly one parse tree
3. **Mechanical parseability**: Context-free grammar, parseable in linear time
4. **Speech-act semantics**: Every message explicitly encodes intent
5. **Compositionality**: Complex messages composed from simple, typed primitives
6. **Plain-text constraint**: Expressible using printable ASCII + common symbols

## 2. Core Concepts

### 2.1 Message Structure

Every AXON message is a **speech act** with exactly three parts:

```
PERFORMATIVE(@sender>@receiver): content
```

- **Performative**: What kind of speech act this is
- **Routing**: Who sends to whom
- **Content**: The structured payload

### 2.2 Compliance Tiers

AXON defines three compliance tiers. Implementations declare which tier they support.

#### Tier 1: Core Valid (minimum parseable message)

Required metadata: `id`, `%%` (protocol version).

```
[id:"m1", %%:1]
QRY(@a>@b): status(@x)
```

#### Tier 2: Interop Compliant (recommended for multi-agent systems)

Adds required: `re` (reply-to), `ts` (timestamp), `ctx` (conversation ID).
Optional at this tier: `sig` (signature), `authz` (authorization scope).

```
[id:"m2", %%:1, re:"m1", ts:1707600000, ctx:"conv-42"]
RPL(@b>@a): {status:#healthy, uptime:99.7%}
```

#### Tier 3: Production Certified (for deployment)

Adds: `sig` (signature), `authz` (authorization scope), `tenant`, `err_ns` (error namespace).

```
[id:"m3", %%:1, re:"m2", ts:1707600001, ctx:"conv-42", sig:"ed25519:...", authz:"role:admin", tenant:"acme"]
CMD(@admin>@server): restart()
```

### 2.3 Character Budget

AXON uses special characters as **structural operators** to eliminate verbose keywords:

| Symbol | Meaning | Replaces |
|--------|---------|----------|
| `>` | directed to | "to", "for", "addressed to" |
| `@` | reference/identity | "the agent named", "identified as" |
| `#` | tag/category | "categorized as", "of type" |
| `$` | variable/binding | "the value of", "let X be" |
| `%` | percentage/ratio | "percent", "out of 100" |
| `&` | conjunction (AND) | "and", "also", "additionally" |
| `\|` | disjunction (OR) | "or", "alternatively" |
| `!` | negation/urgency | "not", "urgent", "immediately" |
| `~` | approximate/fuzzy | "approximately", "about", "roughly" |
| `^` | priority/escalation | "important", "priority level" |
| `*` | wildcard endpoint | "any agent", "broadcast" |
| `=` | equality/assignment | "is equal to", "defined as" |
| `_` | null value | "nothing", "empty", "no value" |
| `:` | has-property/contains | "has", "contains", "with property" |
| `.` | path separator | "of the", "'s", "belonging to" |
| `..` | range | "from X to Y", "between" |
| `->` | implies/then/sequence | "therefore", "then", "followed by" |
| `<-` | because/caused-by | "because", "due to", "since" |
| `<` `>` `<=` `>=` `!=` | comparison | "less than", "greater than", etc. |

## 3. Performatives

AXON defines a fixed core set of performatives (speech acts). Each has formally defined preconditions and effects.

### 3.1 Information Performatives

| Performative | Meaning | Precondition | Effect |
|-------------|---------|--------------|--------|
| `INF` | Inform | Sender believes P | Receiver knows sender believes P |
| `QRY` | Query | Sender wants to know P | Receiver knows sender wants P |
| `RPL` | Reply | Responding to a QRY | Sender provides requested information |
| `CFM` | Confirm | Verifying a truth-apt claim | Receiver knows P is confirmed true |
| `DNY` | Deny | Negating a truth-apt claim | Receiver knows P is confirmed false |
| `ERR` | Error | Processing failed | Receiver knows about failure (semantic) |

### 3.2 Action Performatives

| Performative | Meaning | Precondition | Effect |
|-------------|---------|--------------|--------|
| `REQ` | Request | Sender wants receiver to act | Receiver knows action is requested |
| `CMD` | Command | Sender has authority | Receiver must act (or refuse with REJ) |
| `PRO` | Propose | Sender offers a plan | Receiver may accept/reject/counter |
| `ACC` | Accept | Responding to PRO | Proposal is agreed upon |
| `REJ` | Reject | Responding to PRO | Proposal is declined |
| `CTR` | Counter | Responding to PRO | Alternative proposal offered |
| `DEL` | Delegate | Sender passes responsibility | Receiver takes ownership |
| `CAN` | Cancel | Sender revokes prior act | Prior act is void |

### 3.3 State Performatives

| Performative | Meaning | Precondition | Effect |
|-------------|---------|--------------|--------|
| `SUB` | Subscribe | Wants ongoing updates | Sender receives future updates on topic |
| `UNS` | Unsubscribe | Has active subscription | Subscription is terminated |
| `PUB` | Publish | Broadcasting to subscribers | All subscribers receive update |
| `ACK` | Acknowledge | Received a message (transport-level) | Sender knows message was received |
| `NAK` | Negative Ack | Cannot process message (protocol-level) | Sender knows message was not processed |
| `SYN` | Synchronize | Aligning state | Agents compare and align state |

### 3.4 Performative Transition Rules

To prevent confusion between similar performatives:

- `ACK` is **transport-level**: "I received your message" (no semantic judgment)
- `NAK` is **protocol-level**: "I cannot process this" (with reason: `invalid`, `unauthorized`, `busy`, `unsupported`)
- `CFM`/`DNY` respond only to **truth-apt claims** (INF, QRY responses)
- `ACC`/`REJ` respond only to **proposals** (PRO, CTR)
- `ERR` reports **semantic/application failures** (task failed, resource not found)

### 3.5 Extension Mechanism

Domain-specific performatives use the `X.` namespace prefix:

```
X.trade.BID(@buyer>@exchange): {symbol:"AAPL", qty:100, limit:150.00usd}
X.trade.FILL(@exchange>@buyer): {qty:100, price:149.50usd}
```

Custom performatives must document preconditions and effects following the same pattern as core performatives.

## 4. Grammar (EBNF)

### 4.1 Document Structure

```ebnf
document       = { full_message } EOF ;
full_message   = [ meta ] message ;
message        = performative routing ":" expression ;
```

### 4.2 Performatives and Routing

```ebnf
performative   = core_perf | ext_perf ;
core_perf      = "INF" | "QRY" | "RPL" | "CMD" | "REQ" | "PRO"
               | "ACC" | "REJ" | "CTR" | "DEL" | "CAN" | "CFM"
               | "DNY" | "ERR" | "ACK" | "NAK" | "SYN"
               | "SUB" | "UNS" | "PUB" ;
ext_perf       = "X" "." identifier "." identifier ;

routing        = "(" endpoint ">" endpoint ")" ;
endpoint       = agent | wildcard | agent_list ;
agent          = "@" qualified_id ;
wildcard       = "*" ;
agent_list     = "[" agent { "," agent } "]" ;
```

### 4.3 Expressions (Precedence-Based)

Operators are listed from **lowest to highest** precedence. All binary operators are **left-associative** except `<-` which is **right-associative**.

```ebnf
expression     = causal_expr ;

(* Precedence 1 — lowest: causal chains *)
causal_expr    = sequence_expr { "<-" sequence_expr } ;

(* Precedence 2: sequential chains *)
sequence_expr  = parallel_expr { "->" parallel_expr } ;

(* Precedence 3: parallel composition *)
parallel_expr  = disjunct_expr { "&" disjunct_expr } ;

(* Precedence 4: disjunction *)
disjunct_expr  = comparison { "|" comparison } ;

(* Precedence 5: comparison *)
comparison     = assign_expr [ comp_op assign_expr ] ;
comp_op        = "<" | ">" | "<=" | ">=" | "!=" | "=" ;

(* Precedence 6: range *)
assign_expr    = primary [ ".." primary ] ;

(* Precedence 7 — highest: primary expressions *)
primary        = "~" primary
               | atom
               | tag_expr
               | call_expr
               | list
               | record
               | "(" expression ")"
               | nested_message ;
```

### 4.4 Atoms and Compounds

```ebnf
atom           = string | number | boolean | null | ref | var | path ;

string         = '"' { char | escape } '"' ;
escape         = "\\" ( '"' | "\\" | "n" | "t" ) ;
(* Reserved, not yet implemented: | "u{" hex_digit "}" *)
number         = [ "-" ] digit { digit } [ "." digit { digit } ] [ unit ] ;
boolean        = "T" | "F" ;
null           = "_" ;
ref            = "@" qualified_id ;
var            = "$" qualified_id ;
path           = qualified_id ;

qualified_id   = identifier { "." identifier } ;
identifier     = letter { letter | digit | "-" | "_" } ;
letter         = "a".."z" | "A".."Z" ;
digit          = "0".."9" ;

tag_expr       = "#" qualified_id [ record ] ;

call_expr      = qualified_id "(" [ arg_list ] ")" ;
arg_list       = argument { "," argument } ;
argument       = expression | identifier ":" expression ;

list           = "[" [ expression { "," expression } ] "]" ;
record         = "{" [ field { "," field } ] "}" ;
field          = identifier ":" expression ;

nested_message = performative routing ":" expression ;

unit           = "%" | "ms" | "s" | "min" | "h" | "d"
               | "B" | "KB" | "MB" | "GB"
               | "tok" | "usd" | "eur" ;
```

### 4.5 Metadata

```ebnf
meta           = "[" meta_field { "," meta_field } "]" ;
meta_field     = meta_key ":" expression ;
meta_key       = core_meta_key | identifier ;
core_meta_key  = "id" | "re" | "ts" | "ttl" | "^" | "ctx" | "%%"
               | "sig" | "authz" | "tenant" | "err_ns" ;
```

### 4.6 Comments and Whitespace

```ebnf
comment        = "(*" { any | comment } "*)" ;   (* nestable *)
whitespace     = " " | "\t" | "\r" | "\n" ;
```

Messages are separated by whitespace. Whitespace within a message is insignificant except inside strings.

## 5. Operator Precedence Table

| Level | Operator | Associativity | Meaning |
|-------|----------|---------------|---------|
| 1 (lowest) | `<-` | Right | Causation / because |
| 2 | `->` | Left | Sequence / then |
| 3 | `&` | Left | Parallel / and |
| 4 | `\|` | Left | Disjunction / or |
| 5 | `< > <= >= != =` | None | Comparison |
| 6 | `..` | None | Range |
| 7 (highest) | `~` (prefix) | Right | Approximate |

Parentheses `()` override precedence.

## 6. Type System

### 6.1 Primitive Types

| Type | Syntax | Examples |
|------|--------|---------|
| String | `"..."` | `"hello"`, `"error: timeout"` |
| Integer | digits | `42`, `-7`, `0` |
| Float | digits.digits | `3.14`, `-0.5` |
| Boolean | `T` / `F` | `T`, `F` |
| Null | `_` | `_` |
| Reference | `@name` | `@agent-1`, `@db-service` |
| Tag | `#name` | `#urgent`, `#task`, `#bug` |
| Variable | `$name` | `$result`, `$x` |

### 6.2 Compound Types

| Type | Syntax | Example |
|------|--------|---------|
| List | `[a, b, c]` | `[1, 2, 3]`, `[@a, @b]` |
| Record | `{k:v, ...}` | `{name:"x", val:42}` |
| Range | `a..b` | `1..10`, `0%..100%` |
| Tagged Record | `#tag{...}` | `#task{id:"t-1", status:#done}` |

### 6.3 Semantic Tags

Tags annotate expressions with semantic categories:

```
#task{id:"t-42", status:#done, owner:@agent-3}
```

Ontology-qualified tags use dotted paths for domain grounding:

```
#ont.industrial.temp{val:342.5, unit:#celsius, loc:@zone-3}
```

### 6.4 Minimal Typing Rules

These normative rules prevent cross-implementation divergence:

1. **Unit categories**: Units belong to categories (time: ms/s/min/h/d, size: B/KB/MB/GB, currency: usd/eur, ratio: %). Comparison operators between different categories are invalid.
2. **Operator admissibility**: `..` (range) requires both operands to be the same type. `&` and `|` require operands to be expressions (not raw atoms in non-boolean context).
3. **Variable scope**: Variables (`$x`) are bound at message level. A variable referenced in content must either be defined earlier in the same message's expression tree or be a well-known protocol variable.

### 6.5 Variables

Variables (`$name`) represent bindings within message scope. They enable:

```
REQ(@a>@b): fetch($url) -> parse(#json) -> store(@db, $result)
```

Here `$url` is an input binding (must be resolved by context) and `$result` is an output binding (produced by `parse`).

## 7. Message Metadata

### 7.1 Metadata Fields by Tier

| Field | Tier 1 | Tier 2 | Tier 3 | Type | Constraint | Meaning |
|-------|--------|--------|--------|------|------------|---------|
| `id` | Required | Required | Required | string | non-empty | Unique message identifier |
| `%%` | Required | Required | Required | number | positive integer | Protocol version (must be supported) |
| `re` | Optional | Required | Required | string | valid message id | In-reply-to message ID |
| `ts` | Optional | Required | Required | number | positive integer | Unix timestamp (seconds) |
| `ctx` | Optional | Required | Required | string | non-empty | Conversation/context ID |
| `ttl` | Optional | Optional | Optional | number | positive integer | Time-to-live (seconds) |
| `^` | Optional | Optional | Optional | number | integer 0-5 | Priority (0=low, 5=critical) |
| `sig` | — | Optional | Required | string | non-empty | Cryptographic signature |
| `authz` | — | Optional | Required | string | non-empty | Authorization scope |
| `tenant` | — | — | Required | string | non-empty | Tenant identifier |
| `err_ns` | — | — | Required | string | non-empty | Error namespace for taxonomy |

Duplicate metadata keys within a single meta block are invalid and must be rejected.

### 7.2 Examples by Tier

**Tier 1 — Core Valid:**
```
[id:"m1", %%:1]
QRY(@a>@b): status(@web-server)
```

**Tier 2 — Interop Compliant:**
```
[id:"m2", %%:1, re:"m1", ts:1707600000, ctx:"ops-42"]
RPL(@b>@a): {status:#healthy, uptime:99.7%, latency:45ms}
```

**Tier 3 — Production Certified:**
```
[id:"m3", %%:1, re:"m2", ts:1707600001, ctx:"ops-42", sig:"ed25519:abc123", authz:"role:ops", tenant:"acme", err_ns:"acme.infra"]
INF(@b>@a): #all-clear
```

## 8. Composition Patterns

### 8.1 Conditional Content

```
REQ(@scheduler>@worker): if(load < 80%, exec(#task-42), queue(#task-42))
```

### 8.2 Chained Actions (Sequence)

```
REQ(@orchestrator>@pipeline): fetch($url) -> parse(#json) -> store(@db, $result)
```

### 8.3 Parallel Actions

```
REQ(@manager>@team): analyze($data) & summarize($data) & validate($data)
```

### 8.4 Reasoning / Causal Chains

```
INF(@monitor>@admin): #alert{level:3} <- cpu > 95% <- #spike{src:@web-server}
```

### 8.5 Nested Delegation

```
DEL(@ceo>@vp): REQ(*>@team): complete(#project-x) <- deadline("2025-03-01")
```

## 9. Conversation Protocols

### 9.1 Query-Reply

```
QRY(@a>@b): status(@service-x)
RPL(@b>@a): {status:#healthy, uptime:99.7%, latency:45ms}
```

### 9.2 Propose-Accept/Reject/Counter

```
PRO(@a>@b): {action:#migrate, target:@server-2, window:"02:00-04:00"}
CTR(@b>@a): {action:#migrate, target:@server-2, window:"04:00-06:00"} <- load.peak("02:00-03:00")
ACC(@a>@b): _
```

### 9.3 Subscribe-Publish-Unsubscribe

```
SUB(@dashboard>@monitor): #metrics{src:@prod, interval:30s}
PUB(@monitor>@dashboard): {cpu:72%, mem:4.2GB, reqs:1250}
PUB(@monitor>@dashboard): {cpu:68%, mem:4.1GB, reqs:1180}
UNS(@dashboard>@monitor): #metrics{src:@prod}
```

### 9.4 Multi-Agent Coordination

```
REQ(@planner>[@w1, @w2, @w3]): {
  task:#data-process,
  split:[0..1000, 1001..2000, 2001..3000],
  merge:@planner,
  deadline:300s
}
ACK(@w1>@planner): _
ACK(@w2>@planner): _
ACK(@w3>@planner): _
```

### 9.5 Negative Acknowledgment

```
NAK(@b>@a): {reason:#unauthorized, detail:"missing role:admin"}
NAK(@b>@a): {reason:#invalid, detail:"unknown performative"}
NAK(@b>@a): {reason:#busy, retry_after:30s}
```

## 10. Error Handling

Errors carry structured diagnostic information:

```
ERR(@service>@caller): {
  code:404,
  what:"resource not found",
  ref:@missing-item,
  retry:F,
  suggest:QRY(@caller>@registry): locate(@missing-item)
}
```

NAK reason codes (protocol-level):
- `#invalid` — malformed or unparseable message
- `#unauthorized` — insufficient permissions
- `#busy` — receiver overloaded, retry later
- `#unsupported` — unknown performative or feature

## 11. Ontology References

AXON supports referencing shared ontologies via dotted tag paths:

```
INF(@sensor>@controller): #ont.industrial.temp{val:342.5, unit:#celsius, loc:@zone-3}
```

## 12. Escaping and Encoding

- Strings use `"` delimiters with `\"` for literal quotes and `\\` for literal backslash
- Newlines in strings: `\n`, tabs: `\t`
- Unicode: `\u{XXXX}` within strings (reserved, not yet implemented)
- Binary data: base64-encoded strings with `#b64` tag: `#b64{"data":"SGVsbG8="}`

## 13. Protocol Versioning

The `%%` metadata field declares the protocol version. Agents must reject messages with unsupported versions via NAK:

```
NAK(@b>@a): {reason:#unsupported, detail:"%%:2 not supported, max:1"}
```

## 14. Reserved for Future Extension

- `&&` — transaction boundaries (see Transaction Profile)
- `||` — fallback chains
- `^^` — encryption envelope
- `~~` — approximate matching/fuzzy query

---

## Appendix A: Comparison with Existing Approaches

This comparison evaluates full communication stacks, not just wire formats.

| Feature | English | JSON + Schema + Envelope | FIPA-ACL + SL | **AXON** |
|---------|---------|--------------------------|----------------|----------|
| Unambiguous grammar | No | Partial (schema-dependent) | Yes | Yes (pending conformance tests) |
| Speech-act semantics | No | No (layered externally) | Yes | Yes |
| Token-efficient | No | Moderate | No | Hypothesis (pending benchmarks) |
| Machine-parseable | Hard | Yes | Yes | Yes |
| Compositional | Yes | Limited | Limited | Yes |
| Plain-text | Yes | Yes | Yes | Yes |
| Typed | No | Yes (with JSON Schema) | Yes | Yes (minimal normative rules) |
| Self-describing | Yes | Partial (needs schema ref) | Yes | Envelope + shared schemas |
| Ecosystem maturity | Dominant | Dominant | Legacy | Draft |

## Appendix B: Profiles (Normative Patterns)

### B.1 Transaction Profile

For transactional workflows, use `PRO`/`ACC`/`REJ`/`CAN` with these standardized metadata fields:

```
[id:"m1", %%:1, txn_id:"tx-42", txn_state:#proposed]
PRO(@coordinator>@participant): {action:#debit, amount:100usd, account:@acct-1}

[id:"m2", %%:1, re:"m1", txn_id:"tx-42", txn_state:#accepted]
ACC(@participant>@coordinator): _

[id:"m3", %%:1, txn_id:"tx-42", txn_state:#committed]
CMD(@coordinator>@participant): commit(txn:"tx-42")

(* Or on failure: *)
[id:"m3", %%:1, txn_id:"tx-42", txn_state:#aborted]
CAN(@coordinator>@participant): txn("tx-42") <- timeout(30s)
```

Transaction states: `#proposed` → `#accepted` → `#committed` | `#aborted`

### B.2 Coordination Profile

For vote/quorum operations:

```
REQ(@coordinator>[@voter-1, @voter-2, @voter-3]): {
  vote_id:"v-1",
  question:#approve-deploy,
  threshold:2,
  deadline:60s
}
RPL(@voter-1>@coordinator): {vote_id:"v-1", vote:#yes}
RPL(@voter-2>@coordinator): {vote_id:"v-1", vote:#yes}
RPL(@voter-3>@coordinator): {vote_id:"v-1", vote:#no}
INF(@coordinator>[@voter-1, @voter-2, @voter-3]): {
  vote_id:"v-1",
  result:#approved,
  tally:{yes:2, no:1},
  threshold_met:T
}
```

## Appendix C: Known Gaps

> These are documented limitations of v0.1-experimental. Each is classified by severity and impact on Experiment 0 eligibility.

| # | Gap | Severity | Exp 0 Impact | Status |
|---|-----|----------|--------------|--------|
| 1 | `\u{XXXX}` unicode escapes defined in grammar but not implemented in parser | Low | None — no test case requires unicode escapes | Reserved |
| 2 | Variable scope rules are informal ("message level") with no formal binding semantics | Medium | Low — Exp 0 tasks use simple single-message variable references | Spec-ambiguous |
| 3 | No formal error recovery strategy — parser aborts on first error | Medium | None — Exp 0 measures correctness, not error recovery | Deferred |
| 4 | `&` and `|` operator admissibility rules (§6.4) are not enforced by parser | Low | None — validator handles semantic checks | Deferred to validator |
| 5 | Unit category cross-comparison (§6.4 rule 1) not enforced at parse time | Low | None — validator handles semantic checks | Deferred to validator |
| 6 | Transaction profile metadata keys (`txn_id`, `txn_state`) not in core meta_key set | Low | None — profile extensions now supported via `meta_key = core_meta_key \| identifier` | Resolved |

### Bug Classifications (from adversarial review)

**Gate-blocking (fixed in v0.1-experimental):**
- Identifier legality: digit-first segments were accepted by parser but forbidden by spec grammar
- Unclosed comment EOF: parser silently consumed instead of raising error
- `a->b` tokenization: `-` in identifiers consumed the `-` from `->` operator
- Duplicate metadata keys: silently overwritten instead of rejected

**Non-blocking (deferred):**
- Remaining items from debate/summary.md — semantic checks delegated to validator
