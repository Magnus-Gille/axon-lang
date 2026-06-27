#!/usr/bin/env python3
"""Wild experiment 4 — INDEPENDENT verifier breaks the shared-bias blind spot.

Exps 1 & 3 showed same-model methods (self-consistency, same-model verification) can't
catch the systematic role-confusion errors: generation and verification share the same
wrong thesaurus, so the model judges its own error as correct. The cross-lingual synthesis
(mech 2, listener>speaker asymmetry; mech 1 ARQ "independent view") predicts a GENUINELY
INDEPENDENT evaluator — a different model family, with the shared thesaurus — should see it.

Test: sender = qwen3-30b (box); verifier = `claude -p` (independent frontier, local CLI,
zero box cost), given intent + emitted fields + the shared thesaurus. Detection recall vs
the same-model 0.14 baseline.

Usage: python run_indep_verify.py
"""
from __future__ import annotations
import json, os, subprocess, sys, statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
PILOT = os.path.join(HERE, "..", "exp_incontext_dsl"); M5 = os.path.join(HERE, "..", "exp_m5_falsification")
sys.path.insert(0, PILOT); sys.path.insert(0, M5)
from run_structured import schema_for, SYS
import conditions as C, scoring_lib as S
from m5_client import chat


def emit_bare(t):
    r = chat("qwen3-30b-instruct", [{"role": "system", "content": SYS},
             {"role": "user", "content": f"Intent:\n{t['nl_intent']}\n\nEmit the JSON object."}],
             max_tokens=600, temperature=0.2, response_format=schema_for(t))
    try:
        o = json.loads(r["content"]); return {f: o.get(f) for f in t["fields"]} if isinstance(o, dict) else {}
    except Exception:
        return {}


def claude_verify(t, fields):
    body = "\n".join(f"- {k} = {json.dumps(fields.get(k))}" for k in t["fields"])
    thes = "\n".join(f"- {k}: {C.FIELD_HINTS.get(k,'')}" for k in t["fields"])
    prompt = (f"You are Agent B receiving a message. Sender intent:\n{t['nl_intent']}\n\n"
              f"Decoded field values:\n{body}\n\nThe agreed meaning of each field:\n{thes}\n\n"
              "Watch for role confusion (recipient vs target/source, cause vs source). For each "
              "field, is its value correct given the intent and agreed meaning? "
              'Return ONLY JSON, e.g. {"speech_act": true, "target": false}.')
    try:
        p = subprocess.run(["claude", "-p", prompt], capture_output=True, text=True,
                           timeout=120, stdin=subprocess.DEVNULL)
        a = json.loads(C.extract_json(p.stdout))
        return {k: (a.get(k) is False) for k in t["fields"]}
    except Exception:
        return {k: False for k in t["fields"]}


def main():
    tasks = json.load(open(os.path.join(M5, "tasks.json")))["tasks"]
    tp = fp = fn = tn = 0
    for t in tasks:
        fields = emit_bare(t)
        wrong = {k: S.score_field(t["fields"][k], fields.get(k)) < 1.0 for k in t["fields"]}
        flagged = claude_verify(t, fields)
        for k in t["fields"]:
            if flagged[k] and wrong[k]: tp += 1
            elif flagged[k] and not wrong[k]: fp += 1
            elif not flagged[k] and wrong[k]: fn += 1
            else: tn += 1
        print(f"{t['id']} wrong={[k for k in wrong if wrong[k]]} flagged={[k for k in flagged if flagged[k]]}", flush=True)
    rec = tp/(tp+fn) if tp+fn else 0; prec = tp/(tp+fp) if tp+fp else 0
    print(f"\nINDEPENDENT verifier (claude -p): recall={rec:.2f} precision={prec:.2f}  tp={tp} fp={fp} fn={fn}")
    print(f"(same-model verifier was recall=0.14; predicted independent >> same-model)")


if __name__ == "__main__":
    main()
