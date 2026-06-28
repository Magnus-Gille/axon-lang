#!/usr/bin/env python3
"""A custom, task-specialized DSL for the M5 agent-message family + a DETERMINISTIC
parser. This is the "specialized beats general" arm of the in-context pilot: a
format hand-built for exactly these intents, deterministically parseable (no LLM),
and as compact as the task vocabulary allows.

Grammar (one line):
    <ACT> @sender>@receiver | key=value key=value ...
  ACT  : q inf req cmd pro acc rej ctr del err sub   (fixed verb codes)
  value: scalar | ordered-list a>b>c | set-list a,b,c | bool T/F | null _
Keys are the shared field vocabulary (subject,target,steps,actions,threshold,...).

A deterministic consumer splits on '|', reads the verb, then key=value pairs;
ordered lists split on '>', sets on ','. No model in the loop.
"""
from __future__ import annotations
import re

ACT = {"q": "query", "inf": "inform", "req": "request", "cmd": "command",
       "pro": "propose", "acc": "accept", "rej": "reject", "ctr": "counter",
       "del": "delegate", "err": "error", "sub": "subscribe"}

ENCODER_SYS = """You are Agent A. Encode each intent as ONE line in this compact DSL that a deterministic parser (no LLM) will read:

<ACT> @sender>@receiver | key=value key=value ...

- ACT is one of: q inf req cmd pro acc rej ctr del err sub
- After '|', emit space-separated key=value pairs using the SHORTEST descriptive keys.
- ordered steps: key=a>b>c   unordered set: key=x,y,z   boolean: key=T or key=F   missing: key=_
- numbers carry no unit (just the value). Use the sender/receiver named in the intent (@a if unspecified).

Examples:
q @a>@b | subject=status target=@service-x
req @mgr>@team | actions=analyze,validate parallel=T priority=1

Output ONLY the single DSL line. No prose, no fences."""


def build_messages(task: dict) -> list[dict]:
    user = f"Intent to convey:\n{task['nl_intent']}\n\nEmit the single DSL line now."
    return [{"role": "system", "content": ENCODER_SYS}, {"role": "user", "content": user}]


def parse(msg: str):
    """Deterministic DSL -> field dict. Returns None if it doesn't match the grammar."""
    if not msg or "|" not in msg:
        # allow act-only lines with no payload too
        m = (msg or "").strip()
        if not m:
            return None
        head, _, rest = m.partition("|")
    else:
        head, _, rest = msg.strip().partition("|")
    parts = head.split()
    if not parts:
        return None
    verb = parts[0].lower()
    out = {}
    if verb in ACT:
        out["speech_act"] = ACT[verb]
    else:
        return None  # unknown verb -> deterministic reject
    for tok in rest.split():
        if "=" not in tok:
            continue
        k, v = tok.split("=", 1)
        k = k.strip()
        v = v.strip()
        if v == "_":
            out[k] = None
        elif v in ("T", "F"):
            out[k] = (v == "T")
        elif ">" in v:
            out[k] = [x for x in v.split(">") if x]
        elif "," in v:
            out[k] = [x for x in v.split(",") if x]
        else:
            out[k] = v
    return out


def valid(msg: str) -> bool:
    d = parse(msg)
    return isinstance(d, dict) and "speech_act" in d


_FENCE = re.compile(r"^```[a-z]*\s*|\s*```$")


def clean(raw: str) -> str:
    s = (raw or "").strip()
    s = _FENCE.sub("", s).strip()
    return s.splitlines()[0].strip() if s else ""


if __name__ == "__main__":
    # quick self-check
    ok = "req @mgr>@team | actions=analyze,validate parallel=T"
    d = parse(ok)
    assert d["speech_act"] == "request" and d["actions"] == ["analyze", "validate"] and d["parallel"] is True, d
    assert valid(ok) and not valid("hello world")
    print("dsl selftest: ALL PASS", d)
