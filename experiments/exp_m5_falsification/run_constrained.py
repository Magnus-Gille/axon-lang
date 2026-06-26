#!/usr/bin/env python3
"""Constrained-decoding follow-up (steelman AXON).

The M5 box supports `response_format: json_schema` but NOT grammar-constrained
decoding, so we cannot constrain AXON to its EBNF directly. As an honest proxy we
use **retry-until-valid**: resample (with temperature) up to k times and keep the
first message that PARSES as valid AXON. This removes the selection bias of a
"valid-only" re-slice (it forces the hard, previously-invalid cells to also reach
validity) and prices in the *generation* cost of reaching validity.

Token accounting:
- wire_tokens   = neutral tiktoken count of the FINAL message (what's transmitted;
                  a true constrained decoder would match this at ~1 pass).
- gen_tokens    = SUM of completion_tokens across all attempts (the proxy's cost;
                  a true constrained decoder would pay roughly the 1-pass cost).

Run on the capable models only (where AXON has a chance). Output mirrors the
encode schema so run_decode.py can consume it (condition tagged 'axon_retry').

Usage: python run_constrained.py --out results/constrained_encode.jsonl
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import conditions as C
from m5_client import chat
from run_encode import MAXTOK, ntok, validity

CAPABLE = ["qwen3-30b-instruct", "qwen3-coder-next-80b", "gpt-oss-120b"]


def load_done(path):
    d = set()
    if os.path.exists(path):
        for l in open(path):
            try:
                d.add(json.loads(l)["key"])
            except Exception:
                pass
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default=",".join(CAPABLE))
    ap.add_argument("--k", type=int, default=4)
    ap.add_argument("--temp", type=float, default=0.4)
    ap.add_argument("--out", default=os.path.join(HERE, "results", "constrained_encode.jsonl"))
    ap.add_argument("--tasks-file", default=os.path.join(HERE, "tasks.json"))
    args = ap.parse_args()

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    tasks = json.load(open(args.tasks_file))["tasks"]
    models = args.models.split(",")
    done = load_done(args.out)
    out = open(args.out, "a")

    for model in models:
        budget = MAXTOK.get(model, 1500)
        t0 = time.time()
        n = nvalid = 0
        for task in tasks:
            key = f"{model}|axon_retry|{task['id']}|0"
            if key in done:
                continue
            msgs = C.build_encode_messages(task, "axon")
            gen_tokens = 0
            lat = 0.0
            attempts = 0
            final_msg, final_ok, final_valid = "", False, False
            for a in range(args.k):
                r = chat(model, msgs, max_tokens=budget, temperature=args.temp)
                attempts += 1
                if r["ok"]:
                    gen_tokens += (r["usage"].get("completion_tokens") or 0)
                    lat += (r["latency_s"] or 0)
                    msg = C.extract_message(r["content"], "axon")
                    v = validity("axon", msg)
                    final_msg, final_ok, final_valid = msg, True, v
                    if v:
                        break
                else:
                    final_ok = final_ok or False
            rec = {
                "key": key, "model": model, "condition": "axon_retry",
                "task_id": task["id"], "level": task["level"], "run": 0,
                "ok": final_ok, "valid": final_valid, "msg": final_msg,
                "attempts": attempts,
                "wire_tokens": ntok(final_msg),
                "neutral_tokens": ntok(final_msg),  # alias for run_decode/analyze compatibility
                "gen_tokens": gen_tokens,
                "completion_tokens": gen_tokens,
                "latency_s": round(lat, 2),
            }
            out.write(json.dumps(rec) + "\n")
            out.flush()
            n += 1
            nvalid += int(final_valid)
            print(f"[{model}] {task['id']} valid={final_valid} attempts={attempts} "
                  f"wire={rec['wire_tokens']} gen={gen_tokens}", flush=True)
        print(f"[{model}] DONE n={n} valid={nvalid} elapsed={time.time()-t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
