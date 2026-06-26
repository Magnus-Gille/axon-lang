#!/usr/bin/env python3
"""Decode pass: a single fixed decoder (Agent B) reads each encoded message and
recovers the canonical field tuple as JSON — uniformly for every condition, so
fidelity differences reflect the FORMAT, not a per-condition decoder.

We decode every successfully-encoded message (valid or not): a real receiver
still tries to extract meaning from a slightly-malformed message, and that
robustness is itself part of what we are measuring.

Usage:
  python run_decode.py --decoder qwen3-30b-instruct \
      --in results/encode.jsonl --out results/decode.jsonl
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


def load_existing(path: str) -> set[str]:
    keys = set()
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                try:
                    keys.add(json.loads(line)["key"])
                except Exception:
                    pass
    return keys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--decoder", default="qwen3-30b-instruct")
    ap.add_argument("--in", dest="inp", default=os.path.join(HERE, "results", "encode.jsonl"))
    ap.add_argument("--out", default=os.path.join(HERE, "results", "decode.jsonl"))
    ap.add_argument("--tasks-file", default=os.path.join(HERE, "tasks.json"))
    ap.add_argument("--max-tokens", type=int, default=800)
    args = ap.parse_args()

    tasks = {t["id"]: t for t in json.load(open(args.tasks_file))["tasks"]}
    encs = []
    with open(args.inp) as f:
        for line in f:
            try:
                r = json.loads(line)
            except Exception:
                continue
            if r.get("ok") and (r.get("msg") or "").strip():
                encs.append(r)

    done = load_existing(args.out)
    out = open(args.out, "a")
    n = ok = parsed = 0
    t0 = time.time()
    todo = [e for e in encs if e["key"] not in done]
    for i, e in enumerate(todo):
        task = tasks[e["task_id"]]
        msgs = C.build_decode_messages(e["msg"], task)
        r = chat(args.decoder, msgs, max_tokens=args.max_tokens, temperature=0.0)
        recovered, perr = None, None
        if r["ok"]:
            try:
                recovered = json.loads(C.extract_json(r["content"]))
                if not isinstance(recovered, dict):
                    recovered, perr = None, "not_object"
            except Exception as ex:
                perr = f"{type(ex).__name__}: {ex}"
        rec = {
            "key": e["key"],
            "decoder": args.decoder,
            "model": e["model"],
            "condition": e["condition"],
            "task_id": e["task_id"],
            "level": e["level"],
            "run": e["run"],
            "encode_valid": e.get("valid"),
            "recovered": recovered,
            "decode_ok": r["ok"],
            "parse_err": perr,
            "raw": r["content"][:2000],
            "latency_s": r["latency_s"],
            "error": r["error"],
        }
        out.write(json.dumps(rec) + "\n")
        out.flush()
        n += 1
        ok += int(r["ok"])
        parsed += int(recovered is not None)
        if (i + 1) % 10 == 0 or i == 0:
            rate = (time.time() - t0) / n
            print(
                f"[decode {args.decoder}] {i+1}/{len(todo)} ok={ok} parsed={parsed} ~{rate:.1f}s/cell",
                flush=True,
            )
    print(
        f"[decode {args.decoder}] DONE n={n} ok={ok} parsed={parsed} elapsed={time.time()-t0:.0f}s",
        flush=True,
    )


if __name__ == "__main__":
    main()
