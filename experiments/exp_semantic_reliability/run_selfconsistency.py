#!/usr/bin/env python3
"""Wild experiment 1 — self-consistency ensemble (a semantic repetition code).

Mechanism (coding theory, repetition/majority code): emit the SAME structured
message K times at temperature, then take a per-field MAJORITY VOTE. If the
model's value errors are uncorrelated across samples, consensus corrects them and
strict-deterministic fidelity rises past the 0.89 single-shot ceiling.

Reuses the in-context pilot's per-task json_schema (response_format) so SHAPE is
fixed and only VALUE errors remain — exactly the residual semantic bottleneck.

Usage: python run_selfconsistency.py --model qwen3-30b-instruct --k 5
"""
from __future__ import annotations
import argparse, json, os, sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
PILOT = os.path.join(HERE, "..", "exp_incontext_dsl")
M5 = os.path.join(HERE, "..", "exp_m5_falsification")
sys.path.insert(0, PILOT); sys.path.insert(0, M5)
from run_structured import schema_for, SYS  # reuse the constrained emitter
import scoring_lib as S
from m5_client import chat


def _hashable(v):
    return tuple(v) if isinstance(v, list) else v


def vote(samples, field):
    """Per-field majority vote across K extracted dicts."""
    vals = [_hashable(s.get(field)) for s in samples if isinstance(s, dict)]
    vals = [v for v in vals if v is not None]
    if not vals:
        return None
    top, _ = Counter(vals).most_common(1)[0]
    return list(top) if isinstance(top, tuple) else top


def emit_once(model, task, temp):
    msgs = [{"role": "system", "content": SYS},
            {"role": "user", "content": f"Intent:\n{task['nl_intent']}\n\nEmit the JSON object."}]
    r = chat(model, msgs, max_tokens=600, temperature=temp, response_format=schema_for(task))
    if not r["ok"]:
        return None
    try:
        o = json.loads(r["content"])
        return o if isinstance(o, dict) else None
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="qwen3-30b-instruct")
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument("--temp", type=float, default=0.7)
    args = ap.parse_args()
    tasks = json.load(open(os.path.join(M5, "tasks.json")))["tasks"]

    single, ensemble = [], []
    for t in tasks:
        samples = [emit_once(args.model, t, args.temp) for _ in range(args.k)]
        samples = [s for s in samples if s is not None]
        if not samples:
            continue
        # single-shot = first sample; ensemble = per-field majority vote
        s1 = {f: samples[0].get(f) for f in t["fields"]}
        cons = {f: vote(samples, f) for f in t["fields"]}
        f1 = S.score_task(s1, t)[0]
        fc = S.score_task(cons, t)[0]
        single.append(f1); ensemble.append(fc)
        print(f"{t['id']} single={f1:.2f} ensemble(k={len(samples)})={fc:.2f} "
              f"{'UP' if fc > f1 + 0.01 else ('DOWN' if fc < f1 - 0.01 else '=')}", flush=True)
    import statistics as st
    print(f"\n[{args.model}] k={args.k} temp={args.temp}  "
          f"single-shot fidelity={st.mean(single):.3f}  ensemble-vote fidelity={st.mean(ensemble):.3f}  "
          f"delta={st.mean(ensemble)-st.mean(single):+.3f}")


if __name__ == "__main__":
    main()
