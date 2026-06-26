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


# Minimum decode-success rate for a reader arm to carry fidelity signal. Below
# this, the arm is an infra failure (e.g. the weak qwen35-a3b reader returned
# HTTP 530 on 118/131 calls) and its "fidelity" is meaningless, not low.
MIN_DECODE_SUCCESS = 0.5


def decoded_ok(key, decmap):
    """A row counts as decoded only if it produced a dict of recovered fields
    with no parse error — not a null/error placeholder from a failed call."""
    d = decmap.get(key)
    if d is None:
        return False
    if d.get("parse_err") is not None:
        return False
    return isinstance(d.get("recovered"), dict)


def fid(key, decmap):
    e = enc.get(key)
    if not e or not e.get("ok"):
        return None
    if not decoded_ok(key, decmap):
        return None  # infra/parse failure — excluded, NOT scored as zero
    return score_task(decmap[key].get("recovered"), tasks[e["task_id"]])[0]


# cells = axon / json_schema that are ok
def cells(cond):
    return [k for k, e in enc.items() if e["condition"] == cond and e.get("ok") and (e.get("msg") or "").strip()]

print("## Receiver-capability: fidelity by reader strength")
print("(fidelity computed over DECODED-OK rows only; arms below "
      f"{int(MIN_DECODE_SUCCESS*100)}% decode-success are inconclusive)")
print(f"{'condition':<14}{'reader':<22}{'n_ok':>5}{'n_att':>6}{'decode%':>9}{'fidelity':>10}")
trend = {}
for cond in ("axon", "json_schema"):
    ks = cells(cond)
    for rname, dmap in readers.items():
        n_att = len(ks)
        vals = [fid(k, dmap) for k in ks]
        vals = [v for v in vals if v is not None]
        decode_rate = (len(vals) / n_att) if n_att else 0.0
        if not vals:
            print(f"{cond:<14}{rname:<22}{0:>5}{n_att:>6}{decode_rate:>8.0%}{'  no-data':>10}")
            continue
        m = st.mean(vals)
        if decode_rate < MIN_DECODE_SUCCESS:
            # report the rate but suppress fidelity as a trend point
            print(f"{cond:<14}{rname:<22}{len(vals):>5}{n_att:>6}{decode_rate:>8.0%}"
                  f"{'  inconcl.':>10}")
            continue
        trend.setdefault(cond, {})[rname] = m
        print(f"{cond:<14}{rname:<22}{len(vals):>5}{n_att:>6}{decode_rate:>8.0%}{m:>10.3f}")
    print()

print("## Trend (mid -> strong reader; weak arm excluded as inconclusive)")
for cond, r in trend.items():
    if "mid (qwen3-30b)" in r and "strong (coder-80b)" in r:
        delta = r["strong (coder-80b)"] - r["mid (qwen3-30b)"]
        print(f"{cond:<14} mid={r['mid (qwen3-30b)']:.3f} "
              f"strong={r['strong (coder-80b)']:.3f}  "
              f"Δ(strong-mid)={delta:+.3f}")
print("(among capable readers, flat AXON fidelity => the capability floor is on")
print(" the WRITER, not the reader. The weak qwen35-a3b reader arm is suppressed")
print(" above because its decode-success collapsed — an infra failure, not low fidelity.)")
