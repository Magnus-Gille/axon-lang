#!/usr/bin/env python3
"""Hybrid frontier calibration of the machine scorer.

Samples cells and asks a FRONTIER model (via `claude -p`, no M5 involvement) two
questions per cell:
  enc_score  — how faithfully does Agent A's MESSAGE convey the intended fields?
               (isolates ENCODER quality, independent of the decoder)
  rec_score  — how faithfully does Agent B's RECOVERED tuple capture the intent?
               (this is what our machine scorer also measures)

We then correlate `rec_score` with the machine fidelity to validate the scorer,
and compare enc_score vs rec_score to see whether the encoder or the decoder is
the bottleneck. Bounded spend (default 48 cells).

Usage: python calibrate.py [--n 48] [--judge claude]
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from scoring_lib import score_task

COND_ORDER = ["axon", "json", "json_schema", "struct_english", "fipa_acl"]


def readable_truth(task):
    out = []
    for k, spec in task["fields"].items():
        out.append(f"{k} = {spec['value']}")
    return "; ".join(out)


def judge_prompt(msg, truth, recovered):
    return (
        "You are validating an agent-to-agent message pipeline. Be strict.\n\n"
        f"INTENDED INFORMATION (ground truth):\n{truth}\n\n"
        f"AGENT A's MESSAGE (the wire format):\n{msg}\n\n"
        f"AGENT B's RECOVERED FIELDS (after decoding):\n{json.dumps(recovered)}\n\n"
        "Answer with ONLY a JSON object, no prose:\n"
        '{"enc_score": <0.0-1.0: how completely/correctly A\'s MESSAGE conveys the '
        'intended information>, "rec_score": <0.0-1.0: how completely/correctly the '
        'RECOVERED fields match the intended information>}'
    )


def call_claude(prompt: str) -> str:
    try:
        p = subprocess.run(
            ["claude", "-p", prompt],
            capture_output=True, text=True, timeout=180,
            stdin=subprocess.DEVNULL,
        )
        return p.stdout.strip()
    except Exception as e:
        return f"__ERR__ {e}"


def parse_scores(text: str):
    s = text
    a = s.find("{")
    b = s.rfind("}")
    if a != -1 and b != -1:
        try:
            d = json.loads(s[a : b + 1])
            return float(d.get("enc_score")), float(d.get("rec_score"))
        except Exception:
            pass
    return None, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=48)
    ap.add_argument("--enc", default=os.path.join(HERE, "results", "encode.jsonl"))
    ap.add_argument("--dec", default=os.path.join(HERE, "results", "decode.jsonl"))
    ap.add_argument("--tasks-file", default=os.path.join(HERE, "tasks.json"))
    ap.add_argument("--out", default=os.path.join(HERE, "results", "calibration.jsonl"))
    args = ap.parse_args()

    tasks = {t["id"]: t for t in json.load(open(args.tasks_file))["tasks"]}
    enc = {json.loads(l)["key"]: json.loads(l) for l in open(args.enc)}
    dec = {json.loads(l)["key"]: json.loads(l) for l in open(args.dec)}

    # stratified sample: spread across conditions and levels, prefer decoded cells
    pool = defaultdict(list)
    for k, e in enc.items():
        if not e.get("ok"):
            continue
        if k not in dec:
            continue
        pool[e["condition"]].append(k)
    per = max(1, args.n // len(COND_ORDER))
    sample = []
    for c in COND_ORDER:
        ks = sorted(pool.get(c, []))
        # spread across the list deterministically
        if ks:
            step = max(1, len(ks) // per)
            sample.extend(ks[::step][:per])

    done = set()
    if os.path.exists(args.out):
        for l in open(args.out):
            try:
                done.add(json.loads(l)["key"])
            except Exception:
                pass

    out = open(args.out, "a")
    rows = []
    for i, k in enumerate(sample):
        if k in done:
            continue
        e = enc[k]
        d = dec[k]
        task = tasks[e["task_id"]]
        mach_fid, _ = score_task(d.get("recovered"), task)
        text = call_claude(judge_prompt(e["msg"], readable_truth(task), d.get("recovered")))
        enc_s, rec_s = parse_scores(text)
        rec = {
            "key": k, "condition": e["condition"], "task_id": e["task_id"],
            "level": e["level"], "model": e["model"],
            "machine_fidelity": mach_fid, "judge_enc": enc_s, "judge_rec": rec_s,
            "judge_raw": text[:300],
        }
        out.write(json.dumps(rec) + "\n")
        out.flush()
        rows.append(rec)
        print(f"[calib {i+1}/{len(sample)}] {e['condition']}/{e['task_id']} "
              f"mach={mach_fid:.2f} judge_rec={rec_s} judge_enc={enc_s}", flush=True)

    # quick agreement stats
    pairs = [(r["machine_fidelity"], r["judge_rec"]) for r in rows if r["judge_rec"] is not None]
    if len(pairs) >= 3:
        import statistics as st
        mae = st.mean(abs(a - b) for a, b in pairs)
        xs = [a for a, _ in pairs]; ys = [b for _, b in pairs]
        mx, my = st.mean(xs), st.mean(ys)
        cov = sum((a - mx) * (b - my) for a, b in pairs)
        sx = sum((a - mx) ** 2 for a in xs) ** 0.5
        sy = sum((b - my) ** 2 for b in ys) ** 0.5
        r = cov / (sx * sy) if sx and sy else float("nan")
        print(f"\nMACHINE vs JUDGE_REC: n={len(pairs)} MAE={mae:.3f} pearson_r={r:.3f}")


if __name__ == "__main__":
    main()
