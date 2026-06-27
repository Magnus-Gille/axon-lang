#!/usr/bin/env python3
"""End-to-end semantic-reliability pipeline — the integrated solution.

Stacks the three confirmed mechanisms and measures the full ladder + cost:
  1. PREVENTION  : emit with the shared thesaurus in the prompt (Shreider alignment)
  2. DETECTION   : an INDEPENDENT verifier (claude -p + thesaurus) flags suspect fields
                   (same-model can't — shared-bias blind spot)
  3. CORRECTION  : ARQ-patch only the flagged fields (Burnashev decision-feedback)

Reports fidelity at each stage for two emitters (bare vs thesaurus) and the verify cost.
Sender/patcher = qwen3-30b (box, stays loaded — no cold-swap); verifier = claude -p (off-box).

Usage: python run_pipeline.py
"""
from __future__ import annotations
import json, os, subprocess, sys, statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
PILOT = os.path.join(HERE, "..", "exp_incontext_dsl"); M5 = os.path.join(HERE, "..", "exp_m5_falsification")
sys.path.insert(0, PILOT); sys.path.insert(0, M5)
from run_structured import schema_for, SYS
import conditions as C, scoring_lib as S
from m5_client import chat
MODEL = "qwen3-30b-instruct"


def emit(t, thesaurus):
    user = f"Intent:\n{t['nl_intent']}\n\n"
    if thesaurus:
        user += "Fill these fields with EXACTLY this meaning:\n" + \
                "\n".join(f"- {k}: {C.FIELD_HINTS.get(k,'')}" for k in t["fields"]) + "\n\n"
    user += "Emit the JSON object."
    r = chat(MODEL, [{"role": "system", "content": SYS}, {"role": "user", "content": user}],
             max_tokens=600, temperature=0.2, response_format=schema_for(t))
    try:
        o = json.loads(r["content"]); return {f: o.get(f) for f in t["fields"]} if isinstance(o, dict) else {}
    except Exception:
        return {}


def claude_flags(t, fields):
    body = "\n".join(f"- {k} = {json.dumps(fields.get(k))}" for k in t["fields"])
    thes = "\n".join(f"- {k}: {C.FIELD_HINTS.get(k,'')}" for k in t["fields"])
    prompt = (f"You are Agent B receiving a message. Sender intent:\n{t['nl_intent']}\n\n"
              f"Decoded field values:\n{body}\n\nAgreed meaning of each field:\n{thes}\n\n"
              "Watch for role confusion (recipient vs target/source, cause vs source). For each "
              'field, is its value correct? Return ONLY JSON, e.g. {"target": false, "subject": true}.')
    try:
        p = subprocess.run(["claude", "-p", prompt], capture_output=True, text=True, timeout=120, stdin=subprocess.DEVNULL)
        a = json.loads(C.extract_json(p.stdout))
        return {k for k in t["fields"] if a.get(k) is False}
    except Exception:
        return set()


def patch(t, fields, flagged):
    out = dict(fields)
    for k in flagged:
        hint = C.FIELD_HINTS.get(k, "")
        r = chat(MODEL, [{"role": "user", "content":
                 f"Intent:\n{t['nl_intent']}\n\nThe field '{k}' means: {hint}\n"
                 f"Give ONLY the correct value for '{k}' (a JSON value, no key, no prose)."}],
                 max_tokens=120, temperature=0.0)
        try:
            out[k] = json.loads(C.extract_json(r["content"]) or r["content"].strip())
        except Exception:
            out[k] = r["content"].strip()
    return out


def main():
    tasks = json.load(open(os.path.join(M5, "tasks.json")))["tasks"]
    rows = {"bare": [], "bare+arq": [], "thes": [], "thes+arq": []}
    nflag = npatch_help = 0
    for t in tasks:
        fb = emit(t, False); ft = emit(t, True)
        rows["bare"].append(S.score_task(fb, t)[0]); rows["thes"].append(S.score_task(ft, t)[0])
        for tag, f in [("bare+arq", fb), ("thes+arq", ft)]:
            flags = claude_flags(t, f)
            nflag += len(flags)
            pf = patch(t, f, flags) if flags else f
            before = S.score_task(f, t)[0]; after = S.score_task(pf, t)[0]
            if after > before + 0.01:
                npatch_help += 1
            rows[tag].append(after)
        print(f"{t['id']} bare={rows['bare'][-1]:.2f} thes={rows['thes'][-1]:.2f} "
              f"bare+arq={rows['bare+arq'][-1]:.2f} thes+arq={rows['thes+arq'][-1]:.2f}", flush=True)
    print("\n=== FIDELITY LADDER (qwen3-30b sender, claude -p verifier) ===")
    for k in ("bare", "bare+arq", "thes", "thes+arq"):
        print(f"  {k:<10} {st.mean(rows[k]):.3f}")
    print(f"\nverify flags raised={nflag}  patches that helped={npatch_help}")
    print(f"cost: +1 independent verify call/msg; +1 patch call per flagged field")


if __name__ == "__main__":
    main()
