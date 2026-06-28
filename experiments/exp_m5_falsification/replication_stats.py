#!/usr/bin/env python3
"""Run-aware replication stats for the firming campaign.

Unlike analyze.py (which pools all cells), this treats RUNS as repeated measures
and reports run-to-run variability — the thing that tells us whether a per-model
difference (e.g. the AXON validity-capability ladder) is signal or noise.

Per (model, condition) it computes, across the R runs present:
  - surface-validity %   : mean ± SD of the per-run valid-fraction
  - decoded-only fidelity: mean ± SD of the per-run mean fidelity
And a test-retest line per condition: per-cell fidelity correlation across the
first two runs (only for cells present in both).

Usage: python replication_stats.py
"""
from __future__ import annotations
import json, os, sys, statistics as st
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from scoring_lib import score_task

tasks = {t["id"]: t for t in json.load(open(os.path.join(HERE, "tasks.json")))["tasks"]}
enc = [json.loads(l) for l in open(os.path.join(HERE, "results/encode.jsonl"))]
dec = {d["key"]: d for d in (json.loads(l) for l in open(os.path.join(HERE, "results/decode.jsonl")))}

CONDS = ["axon", "json", "json_schema", "struct_english", "fipa_acl"]
CAP = ["qwen35-a3b", "gemma4", "qwen3-30b-instruct", "gpt-oss-120b", "qwen3-coder-next-80b"]


def fid(e):
    if not e.get("ok"):
        return 0.0
    d = dec.get(e["key"])
    return score_task(d.get("recovered") if d else None, tasks[e["task_id"]])[0]


def decoded(e):
    d = dec.get(e["key"])
    return bool(e.get("ok")) and d is not None and isinstance(d.get("recovered"), dict)


def ms(xs):
    xs = [x for x in xs if x is not None]
    if not xs:
        return float("nan"), float("nan"), 0
    return st.mean(xs), (st.pstdev(xs) if len(xs) > 1 else 0.0), len(xs)


# index cells by (model, cond, run)
cells = defaultdict(list)
for e in enc:
    cells[(e["model"], e["condition"], e["run"])].append(e)
runs_present = sorted({e["run"] for e in enc})
print(f"runs present in corpus: {runs_present}\n")

print("=" * 78)
print("AXON capability ladder — validity% and decoded-fidelity, mean±SD across runs")
print("=" * 78)
print(f"{'model':<24}{'#runs':>6}{'valid% (m±sd)':>18}{'dec_fid (m±sd)':>20}")
for m in CAP:
    runs = sorted({r for (mm, c, r) in cells if mm == m and c == "axon"})
    valpcts, figs = [], []
    for r in runs:
        cs = cells[(m, "axon", r)]
        if cs:
            valpcts.append(100 * st.mean([1 if e.get("valid") else 0 for e in cs]))
        dcs = [fid(e) for e in cs if decoded(e)]
        if dcs:
            figs.append(st.mean(dcs))
    vm, vs, _ = ms(valpcts)
    fm, fs, _ = ms(figs)
    print(f"{m:<24}{len(runs):>6}   {vm:>5.0f}% ± {vs:>4.0f}      {fm:>6.3f} ± {fs:.3f}")

print("\n" + "=" * 78)
print("Per-condition decoded-only fidelity — mean±SD across runs (all models pooled per run)")
print("=" * 78)
print(f"{'condition':<16}{'valid% (m±sd)':>18}{'dec_fid (m±sd)':>20}")
for c in CONDS:
    valpcts, figs = [], []
    for r in runs_present:
        cs = [e for e in enc if e["condition"] == c and e["run"] == r]
        if not cs:
            continue
        valpcts.append(100 * st.mean([1 if e.get("valid") else 0 for e in cs]))
        dcs = [fid(e) for e in cs if decoded(e)]
        if dcs:
            figs.append(st.mean(dcs))
    vm, vs, _ = ms(valpcts)
    fm, fs, _ = ms(figs)
    lbl = "n/a" if c == "struct_english" else f"{vm:>4.0f}% ± {vs:.0f}"
    print(f"{c:<16}{lbl:>18}      {fm:>6.3f} ± {fs:.3f}")

print("\n" + "=" * 78)
print("Test-retest: per-cell fidelity agreement, run0 vs run1 (cells decoded in both)")
print("=" * 78)
for c in CONDS:
    pairs = []
    for e0 in enc:
        if e0["condition"] != c or e0["run"] != 0:
            continue
        key1 = e0["key"].rsplit("|", 1)[0] + "|1"
        e1 = next((e for e in enc if e["key"] == key1), None)
        if e1 and decoded(e0) and decoded(e1):
            pairs.append((fid(e0), fid(e1)))
    if len(pairs) >= 3:
        xs = [a for a, _ in pairs]; ys = [b for _, b in pairs]
        mx, my = st.mean(xs), st.mean(ys)
        cov = sum((a - mx) * (b - my) for a, b in pairs)
        sx = sum((a - mx) ** 2 for a in xs) ** 0.5
        sy = sum((b - my) ** 2 for b in ys) ** 0.5
        r = cov / (sx * sy) if sx and sy else float("nan")
        mad = st.mean(abs(a - b) for a, b in pairs)
        print(f"  {c:<16} n={len(pairs):>3}  pearson_r={r:+.3f}  mean|Δfid|={mad:.3f}")
    else:
        print(f"  {c:<16} (insufficient paired cells)")
