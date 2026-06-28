#!/usr/bin/env python3
"""Collect custom-DSL emissions on capable senders + score DETERMINISTICALLY.

For each (model, task): emit one DSL line, then a deterministic consumer parses it
(dsl.parse) and scores fidelity vs ground truth (scoring_lib, no LLM). Records
validity (deterministic parse) + neutral tokens + deterministic fidelity.

Usage: python run_dsl.py --model qwen3-30b-instruct [--model ...]
"""
from __future__ import annotations
import argparse, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
M5 = os.path.join(HERE, "..", "exp_m5_falsification")
sys.path.insert(0, HERE)
sys.path.insert(0, M5)
import dsl
import scoring_lib as S
from m5_client import chat

try:
    import tiktoken
    _ENC = tiktoken.get_encoding("cl100k_base")
    ntok = lambda s: len(_ENC.encode(s or ""))
except Exception:
    ntok = lambda s: max(1, round(len(s or "") / 4))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", action="append", required=True)
    ap.add_argument("--out", default=os.path.join(HERE, "results", "dsl.jsonl"))
    ap.add_argument("--max-tokens", type=int, default=400)
    args = ap.parse_args()
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    tasks = json.load(open(os.path.join(M5, "tasks.json")))["tasks"]

    done = set()
    if os.path.exists(args.out):
        for l in open(args.out):
            try:
                done.add(json.loads(l)["key"])
            except Exception:
                pass
    out = open(args.out, "a")
    for model in args.model:
        nok = nvalid = 0
        for t in tasks:
            key = f"{model}|dsl|{t['id']}|0"
            if key in done:
                continue
            r = chat(model, dsl.build_messages(t), max_tokens=args.max_tokens, temperature=0.2)
            msg = dsl.clean(r["content"]) if r["ok"] else ""
            valid = dsl.valid(msg) if r["ok"] else False
            fid, _ = S.score_task(dsl.parse(msg) if valid else None, t)
            rec = {"key": key, "model": model, "condition": "dsl", "task_id": t["id"],
                   "level": t["level"], "ok": r["ok"], "valid": valid, "msg": msg,
                   "neutral_tokens": ntok(msg), "det_fidelity": fid,
                   "latency_s": r["latency_s"], "error": r["error"]}
            out.write(json.dumps(rec) + "\n")
            out.flush()
            nok += int(r["ok"]); nvalid += int(valid)
            print(f"[{model}] {t['id']} valid={valid} ntok={rec['neutral_tokens']} "
                  f"fid={fid:.2f} :: {msg[:60]}", flush=True)
        print(f"[{model}] DONE ok={nok} valid={nvalid}/{len(tasks)}", flush=True)


if __name__ == "__main__":
    main()
