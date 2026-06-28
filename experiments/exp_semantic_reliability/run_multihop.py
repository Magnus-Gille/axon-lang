#!/usr/bin/env python3
"""Multi-hop compounding — does thesaurus mismatch get WORSE down an agent chain?

Real agent systems relay messages A→B→C... Each hop, an agent reads the previous message
and re-emits the same content for the next hop. If field names are ambiguous, does
role-confusion COMPOUND (fidelity decays per hop)? Does thesaurus alignment hold the line?

Per hop the agent receives the prior structured message and re-emits it (same schema).
Fidelity is scored vs the ORIGINAL ground truth at every hop. Bare vs thesaurus-in-prompt,
on the deliberately-ambiguous fresh tasks (where confusion is strongest).

Usage: python run_multihop.py --hops 3
"""
from __future__ import annotations
import argparse, json, os, sys, statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
PILOT = os.path.join(HERE, "..", "exp_incontext_dsl"); M5 = os.path.join(HERE, "..", "exp_m5_falsification")
sys.path.insert(0, PILOT); sys.path.insert(0, M5)
from run_structured import schema_for, SYS
import scoring_lib as S
from m5_client import chat
MODEL = "qwen3-30b-instruct"


def thes_block(t):
    return "Each field means EXACTLY:\n" + "\n".join(f"- {k}: {t['hints'].get(k,'')}" for k in t["fields"]) + "\n\n"


def emit0(t, thes):
    u = f"Intent:\n{t['nl_intent']}\n\n" + (thes_block(t) if thes else "") + "Emit the JSON object."
    return _call(t, u)


def relay(t, prev, thes):
    u = (f"You are a relay agent. You RECEIVED this message:\n{json.dumps(prev)}\n\n"
         "Relay the SAME information onward as a JSON object with the same keys.\n\n"
         + (thes_block(t) if thes else "") + "Emit the JSON object.")
    return _call(t, u)


def _call(t, user):
    r = chat(MODEL, [{"role": "system", "content": SYS}, {"role": "user", "content": user}],
             max_tokens=600, temperature=0.2, response_format=schema_for(t))
    try:
        o = json.loads(r["content"]); return {k: o.get(k) for k in t["fields"]} if isinstance(o, dict) else {}
    except Exception:
        return {}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--hops", type=int, default=3); args = ap.parse_args()
    tasks = json.load(open(os.path.join(HERE, "amb_tasks.json")))["tasks"]
    for thes in (False, True):
        per_hop = [[] for _ in range(args.hops + 1)]
        for t in tasks:
            msg = emit0(t, thes)
            per_hop[0].append(S.score_task(msg, t)[0])
            for h in range(1, args.hops + 1):
                msg = relay(t, msg, thes)
                per_hop[h].append(S.score_task(msg, t)[0])
        label = "thesaurus" if thes else "bare"
        ladder = "  ".join(f"h{h}={st.mean(per_hop[h]):.3f}" for h in range(args.hops + 1))
        print(f"[{label}] fidelity by hop:  {ladder}", flush=True)
    print("\n(bare decaying across hops = compounding; thesaurus flat = alignment holds the chain)")


if __name__ == "__main__":
    main()
