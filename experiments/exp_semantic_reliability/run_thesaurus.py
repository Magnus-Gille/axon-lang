#!/usr/bin/env python3
"""Wild experiment 2 (firmed) — the SHARED THESAURUS in the PROMPT.

Diagnosis (exp.1 + failure analysis): structured-output errors are SYSTEMATIC semantic-
role confusion (recipient leaks into `target`/`source`; cause/source/root confused). The
schema pins names+types but not slot MEANING. Shreider (Ю.А. Шрейдер) semantic information
theory: meaning is relative to the receiver's THESAURUS; the error is a sender/receiver
thesaurus MISMATCH, not channel noise (which is why the self-consistency repetition code
gave +0.000 — it corrects variance, and this is bias).

Fix: align the thesaurus — give the EMITTER the per-field semantic definitions. Two
placements compared, because WHERE matters:
  schema-desc : descriptions inside the json_schema (response_format)  -> the box drops
                them (structure-only enforcement); no effect.
  prompt      : the same definitions in the user PROMPT                -> the model sees
                them; fixes the role confusion.

Usage: python run_thesaurus.py --model qwen3-30b-instruct --reps 3
"""
from __future__ import annotations
import argparse, json, os, sys, statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
PILOT = os.path.join(HERE, "..", "exp_incontext_dsl"); M5 = os.path.join(HERE, "..", "exp_m5_falsification")
sys.path.insert(0, PILOT); sys.path.insert(0, M5)
from run_structured import schema_for, SYS
import conditions as C, scoring_lib as S
from m5_client import chat


def emit(model, t, thesaurus):
    user = f"Intent:\n{t['nl_intent']}\n\n"
    if thesaurus:
        user += ("Fill these fields with EXACTLY this meaning:\n"
                 + "\n".join(f"- {k}: {C.FIELD_HINTS.get(k,'')}" for k in t["fields"]) + "\n\n")
    user += "Emit the JSON object."
    r = chat(model, [{"role": "system", "content": SYS}, {"role": "user", "content": user}],
             max_tokens=600, temperature=0.2, response_format=schema_for(t))
    if not r["ok"]:
        return None
    try:
        o = json.loads(r["content"]); return o if isinstance(o, dict) else None
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="qwen3-30b-instruct")
    ap.add_argument("--reps", type=int, default=3)
    args = ap.parse_args()
    tasks = json.load(open(os.path.join(M5, "tasks.json")))["tasks"]
    bare_runs, thes_runs = [], []
    for rep in range(args.reps):
        b, th = [], []
        for t in tasks:
            ob = emit(args.model, t, False); op = emit(args.model, t, True)
            b.append(S.score_task({f: ob.get(f) for f in t["fields"]} if ob else None, t)[0])
            th.append(S.score_task({f: op.get(f) for f in t["fields"]} if op else None, t)[0])
        bare_runs.append(st.mean(b)); thes_runs.append(st.mean(th))
        print(f"  rep{rep}: bare={st.mean(b):.3f} thesaurus-in-prompt={st.mean(th):.3f}", flush=True)
    bm, tm = st.mean(bare_runs), st.mean(thes_runs)
    bs = st.pstdev(bare_runs) if len(bare_runs) > 1 else 0
    ts = st.pstdev(thes_runs) if len(thes_runs) > 1 else 0
    print(f"\n[{args.model}] reps={args.reps}  bare={bm:.3f}±{bs:.3f}  "
          f"thesaurus-in-prompt={tm:.3f}±{ts:.3f}  delta={tm-bm:+.3f}")


if __name__ == "__main__":
    main()
