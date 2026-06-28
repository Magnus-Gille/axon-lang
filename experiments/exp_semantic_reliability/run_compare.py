#!/usr/bin/env python3
"""Multi-rep comparison of the semantic-reliability mechanisms (rigor pass).

Single-run n=14 deltas were noisy and the thesaurus showed run-dependent regressions
(it over-deliberates ENUM fields like speech_act while fixing entity-role fields).
This measures mean±SD over reps for the conditions that matter:

  bare        : structured outputs, keys+types only
  thes_full   : + thesaurus (semantic descriptions) for ALL fields, in the prompt
  thes_sel    : + thesaurus for non-ENUM fields only (avoid enum over-deliberation)
  bare_arq    : bare + INDEPENDENT verifier (claude -p) detect + ARQ patch

Sender/patcher = qwen3-30b (box); verifier = claude -p (off-box, independent).
Usage: python run_compare.py --reps 3
"""
from __future__ import annotations
import argparse, json, os, subprocess, sys, statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
PILOT = os.path.join(HERE, "..", "exp_incontext_dsl"); M5 = os.path.join(HERE, "..", "exp_m5_falsification")
sys.path.insert(0, PILOT); sys.path.insert(0, M5)
from run_structured import schema_for, SYS
import conditions as C, scoring_lib as S
from m5_client import chat
MODEL = "qwen3-30b-instruct"


def hints(t, mode):
    ks = [k for k in t["fields"] if mode == "full" or t["fields"][k]["kind"] != "enum"]
    return "\n".join(f"- {k}: {C.FIELD_HINTS.get(k,'')}" for k in ks)


def emit(t, thes_mode):
    u = f"Intent:\n{t['nl_intent']}\n\n"
    if thes_mode:
        u += "Fill these fields with EXACTLY this meaning:\n" + hints(t, thes_mode) + "\n\n"
    u += "Emit the JSON object."
    r = chat(MODEL, [{"role": "system", "content": SYS}, {"role": "user", "content": u}],
             max_tokens=600, temperature=0.3, response_format=schema_for(t))
    try:
        o = json.loads(r["content"]); return {f: o.get(f) for f in t["fields"]} if isinstance(o, dict) else {}
    except Exception:
        return {}


def claude_flags(t, fields):
    body = "\n".join(f"- {k} = {json.dumps(fields.get(k))}" for k in t["fields"])
    thes = "\n".join(f"- {k}: {C.FIELD_HINTS.get(k,'')}" for k in t["fields"])
    p = (f"You are Agent B receiving a message. Sender intent:\n{t['nl_intent']}\n\nDecoded fields:\n{body}\n\n"
         f"Agreed meaning:\n{thes}\n\nWatch for role confusion (recipient vs target/source). For each field, "
         'is its value correct? Return ONLY JSON, e.g. {"target": false, "subject": true}.')
    try:
        r = subprocess.run(["claude", "-p", p], capture_output=True, text=True, timeout=120, stdin=subprocess.DEVNULL)
        a = json.loads(C.extract_json(r.stdout))
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
    ap = argparse.ArgumentParser(); ap.add_argument("--reps", type=int, default=3); args = ap.parse_args()
    tasks = json.load(open(os.path.join(M5, "tasks.json")))["tasks"]
    conds = ["bare", "thes_full", "thes_sel", "bare_arq"]
    runs = {c: [] for c in conds}
    for rep in range(args.reps):
        acc = {c: [] for c in conds}
        for t in tasks:
            fb = emit(t, None)
            acc["bare"].append(S.score_task(fb, t)[0])
            acc["thes_full"].append(S.score_task(emit(t, "full"), t)[0])
            acc["thes_sel"].append(S.score_task(emit(t, "sel"), t)[0])
            flags = claude_flags(t, fb)
            acc["bare_arq"].append(S.score_task(patch(t, fb, flags) if flags else fb, t)[0])
        for c in conds:
            runs[c].append(st.mean(acc[c]))
        print(f"  rep{rep}: " + "  ".join(f"{c}={st.mean(acc[c]):.3f}" for c in conds), flush=True)
    print("\n=== mean ± SD over reps (qwen3-30b sender, claude -p verifier) ===")
    for c in conds:
        m = st.mean(runs[c]); s = st.pstdev(runs[c]) if len(runs[c]) > 1 else 0
        print(f"  {c:<10} {m:.3f} ± {s:.3f}")


if __name__ == "__main__":
    main()
