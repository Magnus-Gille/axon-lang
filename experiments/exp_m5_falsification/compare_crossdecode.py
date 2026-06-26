#!/usr/bin/env python3
"""Receiver-side capability: does recovering AXON need a capable READER?

Re-decodes the same AXON & JSON+Schema messages with readers of different
strength and compares fidelity:
  weak   = qwen35-a3b      (results/decode_weak.jsonl)
  mid    = qwen3-30b       (results/decode.jsonl, the original fixed decoder)
  strong = qwen3-coder-80b (results/decode_coder.jsonl)

If AXON fidelity climbs with reader strength while JSON+Schema stays flat, AXON
has a receiver-side capability floor too (it needs capable agents on BOTH ends).
"""
from __future__ import annotations

import json
import os
import statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
import sys
sys.path.insert(0, HERE)
from scoring_lib import score_task

tasks = {t["id"]: t for t in json.load(open(os.path.join(HERE, "tasks.json")))["tasks"]}
enc = {json.loads(l)["key"]: json.loads(l) for l in open(os.path.join(HERE, "results/encode.jsonl"))}


def load(p):
    fp = os.path.join(HERE, p)
    return {json.loads(l)["key"]: json.loads(l) for l in open(fp)} if os.path.exists(fp) else {}


readers = {
    "weak (qwen35-a3b)": load("results/decode_weak.jsonl"),
    "mid (qwen3-30b)": load("results/decode.jsonl"),
    "strong (coder-80b)": load("results/decode_coder.jsonl"),
}


def fid(key, decmap):
    e = enc.get(key)
    if not e or not e.get("ok"):
        return None
    if key not in decmap:
        return None
    return score_task(decmap[key].get("recovered"), tasks[e["task_id"]])[0]


# cells = axon / json_schema that are ok
def cells(cond):
    return [k for k, e in enc.items() if e["condition"] == cond and e.get("ok") and (e.get("msg") or "").strip()]

print("## Receiver-capability: fidelity by reader strength")
print(f"{'condition':<14}{'reader':<22}{'n':>5}{'fidelity':>10}")
trend = {}
for cond in ("axon", "json_schema"):
    ks = cells(cond)
    for rname, dmap in readers.items():
        vals = [fid(k, dmap) for k in ks]
        vals = [v for v in vals if v is not None]
        if vals:
            m = st.mean(vals)
            trend.setdefault(cond, {})[rname] = m
            print(f"{cond:<14}{rname:<22}{len(vals):>5}{m:>10.3f}")
    print()

print("## Trend (weak -> strong reader)")
for cond, r in trend.items():
    if "weak (qwen35-a3b)" in r and "strong (coder-80b)" in r:
        delta = r["strong (coder-80b)"] - r["weak (qwen35-a3b)"]
        print(f"{cond:<14} weak={r.get('weak (qwen35-a3b)',float('nan')):.3f} "
              f"mid={r.get('mid (qwen3-30b)',float('nan')):.3f} "
              f"strong={r.get('strong (coder-80b)',float('nan')):.3f}  "
              f"Δ(strong-weak)={delta:+.3f}")
print("(AXON Δ >> JSON Δ would mean AXON also needs a capable reader)")
