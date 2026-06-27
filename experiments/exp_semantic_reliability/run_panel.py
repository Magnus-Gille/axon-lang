#!/usr/bin/env python3
"""Push detection past 0.50 — an INDEPENDENT VERIFIER PANEL (diverse framings).

A single independent verifier hit recall 0.50. The synthesis (mech 1/2) says the
gain is on the receiver side and from INDEPENDENT views; a panel of diverse framings
(direct / round-trip / adversarial) should union to higher recall while precision
stays usable. All framings run on claude -p (off-box, independent of the qwen3-30b
sender), so this is a pure detection study; then ARQ-patch the union and re-score.

Framings (the panel):
  direct      : per-field correct? (+ shared thesaurus)
  roundtrip   : restate each field in plain English, THEN judge vs intent (decode-then-check)
  adversarial : assume ≥1 field is wrong (esp. role swaps); name the wrong ones

Usage: python run_panel.py
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


def emit_bare(t):
    r = chat(MODEL, [{"role": "system", "content": SYS},
             {"role": "user", "content": f"Intent:\n{t['nl_intent']}\n\nEmit the JSON object."}],
             max_tokens=600, temperature=0.2, response_format=schema_for(t))
    try:
        o = json.loads(r["content"]); return {f: o.get(f) for f in t["fields"]} if isinstance(o, dict) else {}
    except Exception:
        return {}


def claude(prompt):
    try:
        r = subprocess.run(["claude", "-p", prompt], capture_output=True, text=True, timeout=120, stdin=subprocess.DEVNULL)
        return C.extract_json(r.stdout)
    except Exception:
        return ""


def framing(t, fields, mode):
    body = "\n".join(f"- {k} = {json.dumps(fields.get(k))}" for k in t["fields"])
    thes = "\n".join(f"- {k}: {C.FIELD_HINTS.get(k,'')}" for k in t["fields"])
    base = f"Sender intent:\n{t['nl_intent']}\n\nDecoded message fields:\n{body}\n\nAgreed field meanings:\n{thes}\n\n"
    if mode == "direct":
        ask = 'For each field, is its value correct given the intent and meaning? Return ONLY JSON like {"target": false}.'
    elif mode == "roundtrip":
        ask = ('First, restate in plain English what EACH field asserts. Then, comparing to the true intent, '
               'mark each field correct/wrong. Return ONLY JSON like {"target": false}.')
    else:  # adversarial
        ask = ('Assume the sender likely SWAPPED at least one entity into the wrong slot (recipient into '
               'target/source, cause into source, etc). Identify which fields are wrong. Return ONLY JSON like {"target": false}.')
    try:
        a = json.loads(claude(base + ask))
        return {k for k in t["fields"] if a.get(k) is False}
    except Exception:
        return set()


def patch(t, fields, flagged):
    out = dict(fields)
    for k in flagged:
        r = chat(MODEL, [{"role": "user", "content":
                 f"Intent:\n{t['nl_intent']}\n\nThe field '{k}' means: {C.FIELD_HINTS.get(k,'')}\n"
                 f"Give ONLY the correct value for '{k}' (JSON value, no key, no prose)."}],
                 max_tokens=120, temperature=0.0)
        try:
            out[k] = json.loads(C.extract_json(r["content"]) or r["content"].strip())
        except Exception:
            out[k] = r["content"].strip()
    return out


def main():
    tasks = json.load(open(os.path.join(M5, "tasks.json")))["tasks"]
    agg = {n: dict(tp=0, fp=0, fn=0) for n in ("direct", "roundtrip", "adversarial", "union", "majority")}
    base_fid, union_fid = [], []
    for t in tasks:
        f = emit_bare(t)
        wrong = {k: S.score_field(t["fields"][k], f.get(k)) < 1.0 for k in t["fields"]}
        flags = {m: framing(t, f, m) for m in ("direct", "roundtrip", "adversarial")}
        cnt = {k: sum(k in flags[m] for m in flags) for k in t["fields"]}
        flags["union"] = {k for k in t["fields"] if cnt[k] >= 1}
        flags["majority"] = {k for k in t["fields"] if cnt[k] >= 2}
        for n in agg:
            for k in t["fields"]:
                fl = k in flags[n]
                if fl and wrong[k]: agg[n]["tp"] += 1
                elif fl and not wrong[k]: agg[n]["fp"] += 1
                elif not fl and wrong[k]: agg[n]["fn"] += 1
        base_fid.append(S.score_task(f, t)[0])
        union_fid.append(S.score_task(patch(t, f, flags["union"]), t)[0])
        print(f"{t['id']} done", flush=True)
    print(f"\nbaseline fidelity={st.mean(base_fid):.3f}  union-ARQ fidelity={st.mean(union_fid):.3f}  "
          f"delta={st.mean(union_fid)-st.mean(base_fid):+.3f}\n")
    print(f"{'detector':<12}{'recall':>8}{'prec':>7}{'tp':>4}{'fp':>4}{'fn':>4}")
    for n in ("direct", "roundtrip", "adversarial", "union", "majority"):
        d = agg[n]; rec = d["tp"]/(d["tp"]+d["fn"]) if d["tp"]+d["fn"] else 0
        prec = d["tp"]/(d["tp"]+d["fp"]) if d["tp"]+d["fp"] else 0
        print(f"{n:<12}{rec:>8.2f}{prec:>7.2f}{d['tp']:>4}{d['fp']:>4}{d['fn']:>4}")


if __name__ == "__main__":
    main()
