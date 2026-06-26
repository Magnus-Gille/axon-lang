#!/usr/bin/env python3
"""Compare AXON baseline vs AXON retry-until-valid (constrained-decoding proxy)
vs the JSON+Schema incumbent, on the 4 models in the retry arm.

Reports, per model and overall:
  - validity% (baseline single-shot vs retry)
  - fidelity over ALL cells (de-biased; invalid -> low/0)
  - wire tokens (transmitted payload) and effective wire tokens (wire/fidelity)
  - generation cost (completion tokens; retry sums across attempts) — the proxy's
    penalty that true constrained decoding would not pay.
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


def load(p):
    return {json.loads(l)["key"]: json.loads(l) for l in open(os.path.join(HERE, p))} if os.path.exists(os.path.join(HERE, p)) else {}


enc = load("results/encode.jsonl")
dec = load("results/decode.jsonl")
cenc = load("results/constrained_encode.jsonl")
cdec = load("results/constrained_decode.jsonl")

MODELS = ["qwen3-30b-instruct", "qwen3-coder-next-80b", "gpt-oss-120b", "gemma4"]


def fid(e, d):
    if not e or not e.get("ok"):
        return 0.0
    rec = d.get("recovered") if d else None
    return score_task(rec, tasks[e["task_id"]])[0]


def summarize(cells):
    # cells: list of (e, d, wire, gen)
    if not cells:
        return None
    fids = [fid(e, d) for e, d, *_ in cells]
    valid = [bool(e.get("valid")) for e, d, *_ in cells]
    wire = [w for *_, w, g in cells]
    gen = [g for *_, g in cells if g]
    mf = st.mean(fids)
    mw = st.mean(wire)
    return {
        "n": len(cells), "valid": 100 * st.mean(valid), "fid": mf,
        "wire": mw, "eff": mw / mf if mf > 0 else float("inf"),
        "gen": st.mean(gen) if gen else 0,
    }


def axon_baseline(model):
    out = []
    for k, e in enc.items():
        if e["model"] == model and e["condition"] == "axon":
            out.append((e, dec.get(k), e.get("neutral_tokens") or 0, e.get("completion_tokens") or 0))
    return out


def axon_retry(model):
    out = []
    for k, e in cenc.items():
        if e["model"] == model and e["condition"] == "axon_retry":
            out.append((e, cdec.get(k), e.get("wire_tokens") or 0, e.get("gen_tokens") or 0))
    return out


def json_schema(model):
    out = []
    for k, e in enc.items():
        if e["model"] == model and e["condition"] == "json_schema":
            out.append((e, dec.get(k), e.get("neutral_tokens") or 0, e.get("completion_tokens") or 0))
    return out


def row(label, s):
    if not s:
        return f"{label:<26} (no data)"
    eff = f"{s['eff']:.1f}" if s["eff"] != float("inf") else "inf"
    return (f"{label:<26} n={s['n']:>2} valid={s['valid']:>5.0f}% fid={s['fid']:.3f} "
            f"wire={s['wire']:>5.1f} eff_wire={eff:>5} gen_tok={s['gen']:>7.0f}")


print("=== AXON: baseline (single-shot) vs retry-until-valid vs JSON+Schema ===\n")
agg = {"base": [], "retry": [], "js": []}
for m in MODELS:
    print(f"-- {m} --")
    b, r, j = axon_baseline(m), axon_retry(m), json_schema(m)
    print(row("axon baseline", summarize(b)))
    print(row("axon retry-until-valid", summarize(r)))
    print(row("json_schema (incumbent)", summarize(j)))
    print()
    agg["base"] += b; agg["retry"] += r; agg["js"] += j

print("== POOLED (4 models) ==")
print(row("axon baseline", summarize(agg["base"])))
print(row("axon retry-until-valid", summarize(agg["retry"])))
print(row("json_schema (incumbent)", summarize(agg["js"])))
