#!/usr/bin/env python3
"""Encode pass: Agent A turns each intent into a condition-format message.

ONE model per invocation (the M5 box serves one model at a time; swapping is a
multi-minute cold-load, so we drain a whole model before switching). Serial only
— the box rejects concurrent requests with 503. Resumable: re-running skips
cells already present in the output JSONL.

Records per cell: cleaned message, format validity, M5 token usage + latency,
and a neutral tiktoken count so cross-condition token efficiency is measured in
model-independent units.

Usage:
  python run_encode.py --model qwen3-30b-instruct --runs 2 \
      --out results/encode.jsonl
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "src"))

import conditions as C
from m5_client import chat

try:
    import tiktoken

    _ENC = tiktoken.get_encoding("cl100k_base")

    def ntok(s: str) -> int:
        return len(_ENC.encode(s or ""))
except Exception:  # pragma: no cover - fallback if tiktoken missing
    def ntok(s: str) -> int:
        return max(1, round(len((s or "")) / 4))

# Per-model completion budget. Thinking models burn tokens on a hidden reasoning
# channel and return empty content if starved, so give them generous room.
# Reasoning models spend most of the budget on a hidden reasoning channel and
# return EMPTY/truncated content if starved (observed: gemma4 burned all 1500 on
# reasoning, finish_reason=length, msg=""). Give heavy reasoners generous room.
MAXTOK = {
    "qwen35-a3b": 4000,
    "tongyi-dr": 4000,
    "gpt-oss-120b": 4000,
    "gemma4": 6000,
    "qwen3-30b-instruct": 1200,
    "qwen3-coder-next-80b": 1200,
    "mellum": 800,
}


def axon_valid(src: str) -> bool:
    try:
        import axon_parser as ap

        msgs = ap.Parser(ap.Lexer(src).tokenize()).parse()
        return len(msgs) >= 1
    except Exception:
        return False


def validity(condition: str, msg: str) -> bool:
    if not msg or not msg.strip():
        return False
    if condition == "axon":
        return axon_valid(msg)
    if condition in ("json", "json_schema"):
        try:
            json.loads(C.extract_json(msg))
            return True
        except Exception:
            return False
    if condition == "fipa_acl":
        s = msg.strip()
        return s.startswith("(") and s.count("(") == s.count(")") and s.count("(") >= 1
    if condition == "struct_english":
        return True  # prose is "valid" by construction
    return False


def load_existing(path: str) -> set[str]:
    keys = set()
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                try:
                    r = json.loads(line)
                    keys.add(r["key"])
                except Exception:
                    pass
    return keys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--runs", type=int, default=2)
    ap.add_argument("--conditions", default=",".join(C.CONDITIONS))
    ap.add_argument("--tasks", default="")
    ap.add_argument("--out", default=os.path.join(HERE, "results", "encode.jsonl"))
    ap.add_argument("--tasks-file", default=os.path.join(HERE, "tasks.json"))
    ap.add_argument("--temp", type=float, default=0.2)
    ap.add_argument("--max-tokens", type=int, default=0)
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    tasks = json.load(open(args.tasks_file))["tasks"]
    if args.tasks:
        want = set(args.tasks.split(","))
        tasks = [t for t in tasks if t["id"] in want]
    conds = args.conditions.split(",")
    maxtok = args.max_tokens or MAXTOK.get(args.model, 1500)

    done = load_existing(args.out)
    cells = []
    for run in range(args.runs):
        for t in tasks:
            for cond in conds:
                cells.append((run, t, cond))
    if args.limit:
        cells = cells[: args.limit]

    out = open(args.out, "a")
    n_done = n_ok = n_valid = 0
    t_start = time.time()
    for i, (run, task, cond) in enumerate(cells):
        key = f"{args.model}|{cond}|{task['id']}|{run}"
        if key in done:
            continue
        msgs = C.build_encode_messages(task, cond)
        r = chat(args.model, msgs, max_tokens=maxtok, temperature=args.temp)
        msg = C.extract_message(r["content"], cond) if r["ok"] else ""
        valid = validity(cond, msg) if r["ok"] else False
        usage = r.get("usage", {})
        rec = {
            "key": key,
            "model": args.model,
            "condition": cond,
            "task_id": task["id"],
            "level": task["level"],
            "category": task["category"],
            "run": run,
            "ok": r["ok"],
            "valid": valid,
            "msg": msg,
            "raw": r["content"][:4000],
            "reasoning_chars": len(r.get("reasoning") or ""),
            "completion_tokens": usage.get("completion_tokens"),
            "prompt_tokens": usage.get("prompt_tokens"),
            "neutral_tokens": ntok(msg),
            "latency_s": r["latency_s"],
            "finish_reason": r.get("finish_reason"),
            "error": r["error"],
            "attempts": r.get("attempts"),
        }
        out.write(json.dumps(rec) + "\n")
        out.flush()
        n_done += 1
        n_ok += int(r["ok"])
        n_valid += int(valid)
        rate = (time.time() - t_start) / n_done
        print(
            f"[{args.model}] {i+1}/{len(cells)} {cond}/{task['id']}/r{run} "
            f"ok={r['ok']} valid={valid} ntok={rec['neutral_tokens']} "
            f"lat={r['latency_s']}s ~{rate:.1f}s/cell",
            flush=True,
        )
    print(
        f"[{args.model}] DONE encoded={n_done} ok={n_ok} valid={n_valid} "
        f"elapsed={time.time()-t_start:.0f}s",
        flush=True,
    )


if __name__ == "__main__":
    main()
