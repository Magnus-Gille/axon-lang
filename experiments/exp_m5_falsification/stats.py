#!/usr/bin/env python3
"""Statistical rigor for the main result (REALM paper firming).

- Per-condition mean fidelity with 95% bootstrap CIs.
- The capability-floor correlation: Spearman(model capability rank, metric) for
  AXON vs JSON — AXON should track capability steeply, JSON should be flat.
- Paired AXON vs json_schema per (model, task): mean diff + sign test.

Stdlib only (deterministic bootstrap via a fixed LCG so results are reproducible
without Math.random-style nondeterminism).
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
dec = {json.loads(l)["key"]: json.loads(l) for l in open(os.path.join(HERE, "results/decode.jsonl"))}

CONDS = ["axon", "json", "json_schema", "struct_english", "fipa_acl"]
# rough capability ranking (small/weak -> large/strong)
CAP = {"qwen35-a3b": 1, "gemma4": 2, "qwen3-30b-instruct": 3, "gpt-oss-120b": 4, "qwen3-coder-next-80b": 5}


def fid(k):
    e = enc[k]
    if not e.get("ok"):
        return 0.0
    d = dec.get(k)
    return score_task(d.get("recovered") if d else None, tasks[e["task_id"]])[0]


def cells(cond=None, model=None):
    out = []
    for k, e in enc.items():
        if cond and e["condition"] != cond:
            continue
        if model and e["model"] != model:
            continue
        out.append(k)
    return out


# deterministic LCG bootstrap
class LCG:
    def __init__(self, seed=12345):
        self.s = seed

    def randint(self, n):
        self.s = (1103515245 * self.s + 12345) & 0x7FFFFFFF
        return self.s % n


def boot_ci(vals, B=2000):
    if not vals:
        return (0.0, 0.0, 0.0)
    rng = LCG()
    means = []
    n = len(vals)
    for _ in range(B):
        s = sum(vals[rng.randint(n)] for _ in range(n)) / n
        means.append(s)
    means.sort()
    return (st.mean(vals), means[int(0.025 * B)], means[int(0.975 * B)])


def _avg_ranks(v):
    """Fractional (average) ranks — tie-correct, unlike a plain argsort."""
    order = sorted(range(len(v)), key=lambda i: v[i])
    r = [0.0] * len(v)
    i = 0
    while i < len(v):
        j = i
        while j + 1 < len(v) and v[order[j + 1]] == v[order[i]]:
            j += 1
        rank = (i + j) / 2.0 + 1.0  # 1-based average rank for the tie block
        for k in range(i, j + 1):
            r[order[k]] = rank
        i = j + 1
    return r


def spearman(xs, ys):
    """Tie-aware Spearman rho. Returns None (undefined) for a constant vector —
    a degenerate case the old plain-argsort version reported as a spurious +1.00
    (e.g. JSON validity 100% across all 5 models)."""
    if len(xs) < 2 or len(set(xs)) < 2 or len(set(ys)) < 2:
        return None
    rx, ry = _avg_ranks(xs), _avg_ranks(ys)
    n = len(xs)
    mx = sum(rx) / n
    my = sum(ry) / n
    cov = sum((rx[i] - mx) * (ry[i] - my) for i in range(n))
    sx = sum((rx[i] - mx) ** 2 for i in range(n)) ** 0.5
    sy = sum((ry[i] - my) ** 2 for i in range(n)) ** 0.5
    return cov / (sx * sy) if sx and sy else None


def _fmt_rho(v):
    return "undef(const)" if v is None else f"{v:+.2f}"


print("## Per-condition fidelity, 95% bootstrap CI (all models)")
print(f"{'cond':<16}{'mean':>7}{'  95% CI':>18}{'n':>5}")
for c in CONDS:
    vals = [fid(k) for k in cells(cond=c)]
    m, lo, hi = boot_ci(vals)
    print(f"{c:<16}{m:>7.3f}   [{lo:.3f}, {hi:.3f}]{len(vals):>5}")

print("\n## Capability-floor correlation (Spearman rank vs metric, per model)")
models = sorted(CAP, key=lambda m: CAP[m])
caps = [CAP[m] for m in models]
for c in ["axon", "json", "json_schema"]:
    fids = [st.mean([fid(k) for k in cells(cond=c, model=m)] or [0]) for m in models]
    valids = [100 * st.mean([enc[k]["valid"] for k in cells(cond=c, model=m)] or [0]) for m in models]
    print(f"{c:<14} fidelity~capability rho={_fmt_rho(spearman(caps, fids))}   "
          f"validity~capability rho={_fmt_rho(spearman(caps, valids))}")
print("(AXON should show strong positive rho; JSON should be ~flat near 0)")
print("(n=5 over an ad-hoc capability ordering — read as exploratory monotone")
print(" evidence, not a settled effect; rho is undefined for a constant vector.)")

print("\n## Paired AXON vs json_schema (per model×task)")
diffs = []
for m in CAP:
    for t in tasks:
        ka = f"{m}|axon|{t}|0"
        kj = f"{m}|json_schema|{t}|0"
        if ka in enc and kj in enc:
            diffs.append(fid(ka) - fid(kj))
wins = sum(1 for d in diffs if d > 0.01)
losses = sum(1 for d in diffs if d < -0.01)
ties = len(diffs) - wins - losses
print(f"n={len(diffs)}  AXON wins={wins}  ties={ties}  losses={losses}  "
      f"mean diff={st.mean(diffs):+.3f}")
print("(negative mean diff = AXON worse than json_schema on raw all-cells fidelity)")
