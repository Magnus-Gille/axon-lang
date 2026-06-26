#!/usr/bin/env python3
"""Condition prompts for the falsification campaign.

Five conditions, all given EQUAL scaffolding (a concise format description + 2
few-shot examples that do NOT overlap the test tasks) to keep the comparison
fair (see experiments/FAIRNESS.md). The encoder (Agent A) turns a natural-
language intent into ONE message in the condition's format. A single fixed
decoder (Agent B) then extracts the canonical fields back out — uniformly, the
same way for every format — so fidelity differences reflect the FORMAT, not the
decoder.
"""
from __future__ import annotations

import re

CONDITIONS = ["axon", "json", "json_schema", "struct_english", "fipa_acl"]

# ── Encoder system prompts ──────────────────────────────────────────────────

_AXON = """You are Agent A in an agent-to-agent system. Encode each intent as ONE AXON message that Agent B will machine-parse.

AXON syntax:
- A message is:  PERF(@sender>@receiver): expression
- Performatives: QRY(query) RPL(reply) INF(inform) REQ(request) CMD(command) PRO(propose) ACC(accept) REJ(reject) CTR(counter) DEL(delegate) ERR(error) ACK SUB(subscribe) PUB(publish)
- Records: {key:value, ...}   Lists: [a,b,c]   Tags: #name   Refs: @agent   Vars: $x
- Numbers may carry units inline: 99.7%, 45ms, 30s, 2.50usd. Booleans: T / F. Null: _
- Composition operators: A->B (sequence/then), A&B (parallel/and), A|B (or), X<-Y (X because/caused-by Y), lo..hi (range)
- Conditionals: if(cond, then, else)
- A message may nest as a value: DEL(@x>@y): REQ(@y>@z): act()
Use the sender/receiver named in the intent; if the sender is unspecified, use @a.

Examples:
QRY(@a>@b): status(@service-x)
REQ(@mgr>@team): analyze($d) & validate($d) <- #priority{level:1}

Output ONLY the single AXON message. No prose, no markdown fences."""

_JSON = """You are Agent A in an agent-to-agent system. Encode each intent as ONE compact JSON object that Agent B will parse. Use clear descriptive keys; preserve the order of any steps with arrays. Output minified JSON.

Examples:
{"act":"query","to":"@b","subject":"status","target":"@service-x"}
{"act":"request","to":"@team","actions":["analyze","validate"],"parallel":true}

Output ONLY the JSON object. No prose, no markdown fences."""

_JSON_SCHEMA = """You are Agent A in an agent-to-agent system. Encode each intent as ONE JSON message conforming to this envelope contract:
{
  "speech_act": "<one of: query|inform|request|command|propose|accept|reject|counter|delegate|error|subscribe>",
  "sender": "<@agent>",
  "receiver": "<@agent or [list of @agent]>",
  "content": { ...task-specific fields... }
}
Rules:
- speech_act MUST be one of the listed verbs.
- Put all payload data inside content.
- Preserve ordering of steps using JSON arrays.
- For a number that has a unit, encode it as {"value": N, "unit": "..."}.

Examples:
{"speech_act":"query","sender":"@a","receiver":"@b","content":{"subject":"status","target":"@service-x"}}
{"speech_act":"request","sender":"@mgr","receiver":"@team","content":{"actions":["analyze","validate"],"parallel":true,"priority":1}}

Output ONLY the JSON message. No prose, no markdown fences."""

_STRUCT_ENGLISH = """You are Agent A in an agent-to-agent system. Convey each intent to Agent B as ONE clear, structured English message. Be explicit and unambiguous: state the speech act (e.g. "I query", "I request", "I inform"), name the recipient, and include every data field and value. Preserve the order of any steps. Keep it to one tight message.

Examples:
"I (agent A) query agent B for the status of service @service-x."
"I (the manager) request that the team perform two actions in parallel: analyze the data and validate the data (priority 1)."

Output ONLY the message. No markdown, no preamble."""

_FIPA_ACL = """You are Agent A in an agent-to-agent system. Encode each intent as ONE FIPA-ACL message in this shape:
(<performative>
  :sender <@agent> :receiver <@agent>
  :content "<content as a nested S-expression>"
  :language axon-lite :ontology agents)
Performatives: query-ref, inform, request, cfp, propose, accept-proposal, reject-proposal, agree, failure, subscribe.

Examples:
(query-ref :sender @a :receiver @b :content "(status @service-x)" :ontology agents)
(request :sender @mgr :receiver @team :content "(parallel (analyze data) (validate data))" :ontology agents)

Output ONLY the FIPA-ACL message. No prose, no markdown fences."""

_ENCODER_SYS = {
    "axon": _AXON,
    "json": _JSON,
    "json_schema": _JSON_SCHEMA,
    "struct_english": _STRUCT_ENGLISH,
    "fipa_acl": _FIPA_ACL,
}


def build_encode_messages(task: dict, condition: str) -> list[dict]:
    sys = _ENCODER_SYS[condition]
    user = f"Intent to convey:\n{task['nl_intent']}\n\nEmit the single message now."
    return [{"role": "system", "content": sys}, {"role": "user", "content": user}]


# ── Decoder (Agent B) — uniform across conditions ───────────────────────────
#
# The decoder is given the SAME structural knowledge the encoder had (a brief
# primer for every format) plus the shared field schema (one-line semantics per
# requested key). This mirrors a real receiving agent that knows both the wire
# format and the task schema, and removes two confounds that would otherwise
# inflate JSON's edge: (1) only JSON is self-describing to a naive reader, and
# (2) bare field names like subject/target are ambiguous without the schema.

_DECODER_SYS = """You are Agent B, the receiver in an agent-to-agent system. You are given ONE message from Agent A and a schema of fields to extract. Extract the conveyed information into a flat JSON object with EXACTLY the requested keys.

The message may be in any of these formats — read its STRUCTURE correctly:
- AXON: `PERF(@sender>@receiver): payload`. The `(@sender>@receiver)` is the routing ENVELOPE, not content — do NOT treat the receiver as a payload field. Extract from the payload after the colon. `pred(@x)` means property `pred` of `@x`; `a->b->c` is an ordered sequence; `a&b` is a parallel set; `X<-Y` means X caused-by Y; `if(c,t,e)` is a conditional; units are inline (95%, 30s).
- JSON: keys map directly; routing/envelope keys (sender, receiver, to, from) are NOT content unless a field explicitly asks for a recipient.
- FIPA-ACL: `(perf :sender .. :receiver .. :content "(..)")`. :sender/:receiver are envelope; extract from :content.
- English: read for meaning; the agent the message is addressed TO is the receiver (envelope), not a content field unless asked.

Rules:
- Use the given key names verbatim. If a field was not conveyed, set it to null.
- For a number, return just the numeric value (no units, no quotes).
- For a boolean, return true/false.
- For an ordered sequence, return a JSON array in the order conveyed; for an unordered set, a JSON array.
- For an agent reference, return the agent name (with or without a leading @).
Output ONLY minified JSON, nothing else."""

# Shared field-semantic schema: disambiguates field roles for the receiver.
FIELD_HINTS = {
    "speech_act": "the speech act / performative (query, inform, request, propose, counter, delegate, error, subscribe, ...)",
    "target": "the entity the message queries or acts upon (NOT the recipient agent)",
    "subject": "the topic/property being asked about (e.g. status, health)",
    "service": "the service named in the message",
    "status": "the reported status (healthy/ok/down/...)",
    "uptime": "uptime value", "latency": "latency value",
    "action": "the primary action verb", "url": "the URL", "timeout": "timeout value",
    "code": "the numeric error/status code", "reason": "the reason/explanation text",
    "retry": "whether a retry should happen (boolean)",
    "steps": "the ordered list of step/action verbs, in sequence",
    "store_target": "the destination the result is stored in",
    "actions": "the set of action verbs (unordered)",
    "parallel": "whether the actions run in parallel (boolean)",
    "condition_metric": "the metric the condition tests (e.g. load, cpu, status)",
    "threshold": "the threshold numeric value",
    "if_true": "the action verb taken when the condition holds",
    "if_false": "the action verb taken when the condition fails",
    "task_ref": "the referenced task id/name",
    "alert_level": "the alert level number",
    "cause_metric": "the metric that caused the event (e.g. cpu)",
    "cause_threshold": "the numeric threshold the cause exceeded",
    "root_cause": "the underlying root cause (e.g. spike)",
    "source": "the source entity the data/event comes from",
    "recipients": "the set of agents the work is assigned/broadcast to",
    "task": "the task/dataset referenced",
    "merge_to": "the agent results are merged back to",
    "deadline": "the deadline value",
    "item": "the item being proposed/traded", "qty": "the quantity number",
    "price": "the unit price number", "window": "the time window string",
    "delegate_to": "the agent the work is delegated to",
    "inner_action": "the action the delegated party must perform",
    "project": "the project referenced", "interval": "the interval value",
    "metrics": "the set of metrics to subscribe to",
    "first_step": "the first action verb in the plan",
    "condition_value": "the numeric value the condition compares against",
    "if_true_steps": "the ordered steps taken when the condition holds",
    "new_window": "the proposed new time window string",
}


def build_decode_messages(message_text: str, task: dict) -> list[dict]:
    fields = task["fields"]
    schema_lines = []
    for k in fields:
        hint = FIELD_HINTS.get(k, "")
        schema_lines.append(f"- {k}: {hint}" if hint else f"- {k}")
    schema = "\n".join(schema_lines)
    user = (
        f"Message from Agent A:\n{message_text}\n\n"
        f"Extract these fields (shared schema):\n{schema}\n\n"
        f"Return ONLY a minified JSON object with exactly these keys: {list(fields.keys())}"
    )
    return [{"role": "system", "content": _DECODER_SYS}, {"role": "user", "content": user}]


# ── Output cleaning ─────────────────────────────────────────────────────────

_FENCE = re.compile(r"^\s*```[a-zA-Z0-9_-]*\s*|\s*```\s*$")


def extract_message(raw: str, condition: str) -> str:
    """Strip markdown fences and obvious wrapper prose from a model's output.

    Models (esp. gemma4, tongyi-dr) wrap output in ```json fences; some prepend
    a sentence. We keep the fenced block if present, else the raw text trimmed.
    """
    if not raw:
        return ""
    s = raw.strip()
    # If there's a fenced block, take its inner content.
    m = re.search(r"```[a-zA-Z0-9_-]*\s*\n?(.*?)```", s, re.DOTALL)
    if m:
        return m.group(1).strip()
    # Otherwise strip any stray leading/trailing fence markers.
    s = _FENCE.sub("", s).strip()
    return s


def extract_json(raw: str) -> str:
    """Best-effort: pull the first balanced JSON object out of a model reply."""
    s = extract_message(raw, "json")
    start = s.find("{")
    if start == -1:
        return s
    depth = 0
    for i in range(start, len(s)):
        if s[i] == "{":
            depth += 1
        elif s[i] == "}":
            depth -= 1
            if depth == 0:
                return s[start : i + 1]
    return s[start:]
