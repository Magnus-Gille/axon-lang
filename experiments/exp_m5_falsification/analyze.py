#!/usr/bin/env python3
"""Score + aggregate the falsification campaign.

Joins encode (validity/tokens/latency) with decode (recovered fields), computes
round-trip fidelity per cell against ground truth, and reports the metric that
actually matters for agent-to-agent messaging:

    effective_tokens = mean_tokens / mean_fidelity   (expected wire-tokens per
                                                       fully-correct message)

Falsification logic: AXON "earns its place" in a slice only if it lands on the
fidelity-vs-tokens Pareto frontier AND is not dominated by an existing incumbent
(json / json_schema / struct_english / fipa_acl). Runs fine on partial data for
interim reports.

Usage: python analyze.py [--enc results/encode.jsonl] [--dec results/decode.jsonl]
"""
from __future__ import annotations

import argparse
import json
import os
import statistics as st
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from scoring_lib import score_task

INCUMBENTS = ["json", "json_schema", "struct_english", "fipa_acl"]
COND_ORDER = ["axon", "json", "json_schema", "struct_english", "fipa_acl"]


def load_jsonl(path):
    rows = []
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                try:
                    rows.append(json.loads(line))
                except Exception:
                    pass
    return rows


def mean(xs):
    xs = [x for x in xs if x is not None]
    return st.mean(xs) if xs else 0.0


def sd(xs):
    xs = [x for x in xs if x is not None]
    return st.pstdev(xs) if len(xs) > 1 else 0.0


def build_cells(enc, dec, tasks):
    dec_by_key = {d["key"]: d for d in dec}
    cells = []
    for e in enc:
        task = tasks[e["task_id"]]
        d = dec_by_key.get(e["key"])
        recovered = d.get("recovered") if d else None
        if not e.get("ok"):
            fidelity = 0.0
        else:
            fidelity, _ = score_task(recovered, task)
        # A cell is "decoded" only if the encode succeeded AND Agent B returned a
        # dict of recovered fields. The headline (all-attempt) metric imputes
        # fidelity=0 for non-decoded cells; the decoded-only sensitivity table
        # below restricts to just these rows.
        decoded = bool(e.get("ok")) and (d is not None) and isinstance(recovered, dict)
        cells.append({
            "model": e["model"],
            "condition": e["condition"],
            "task_id": e["task_id"],
            "level": e["level"],
            "run": e["run"],
            "ok": bool(e.get("ok")),
            "valid": bool(e.get("valid")),
            "decoded": decoded,
            "fidelity": fidelity,
            "ntok": e.get("neutral_tokens"),
            "ctok": e.get("completion_tokens"),
            "latency": e.get("latency_s"),
        })
    return cells


def agg(cells, keyfn):
    groups = defaultdict(list)
    for c in cells:
        groups[keyfn(c)].append(c)
    rows = {}
    for k, cs in groups.items():
        fid = [c["fidelity"] for c in cs]
        dec_cs = [c for c in cs if c.get("decoded")]
        rows[k] = {
            "n": len(cs),                      # attempts (all-attempt denominator)
            "valid_pct": 100 * mean([c["valid"] for c in cs]),
            "ok_pct": 100 * mean([c["ok"] for c in cs]),
            "fidelity": mean(fid),             # all-attempt: non-decoded imputed 0
            "fidelity_sd": sd(fid),
            "ntok": mean([c["ntok"] for c in cs]),          # attempt-mean wire tokens
            "ctok": mean([c["ctok"] for c in cs]),
            "latency": mean([c["latency"] for c in cs]),
            # decoded-only sensitivity: restrict to rows Agent B actually decoded
            "decoded_n": len(dec_cs),
            "decoded_fidelity": mean([c["fidelity"] for c in dec_cs]),
            "emitted_ntok": mean([c["ntok"] for c in dec_cs]),  # emitted-mean wire tokens
        }
        f = rows[k]["fidelity"]
        rows[k]["eff_tokens"] = (rows[k]["ntok"] / f) if f > 0 else float("inf")
    return rows


def pareto(rows_by_cond):
    """Conditions not dominated on (fidelity higher, ntok lower)."""
    items = [(c, r["fidelity"], r["ntok"]) for c, r in rows_by_cond.items()]
    front = []
    for c, f, t in items:
        dominated = any((f2 >= f and t2 <= t and (f2 > f or t2 < t)) for c2, f2, t2 in items if c2 != c)
        if not dominated:
            front.append(c)
    return front


def _cond_of(k):
    return k[0] if isinstance(k, (tuple, list)) else k


def fmt_table(rows, order=None, label="key"):
    keys = order or sorted(rows)
    # 'surf_val%' = SURFACE validity, condition-specific (AXON: reference parser;
    # json_schema: envelope contract; fipa: performative+slots; json: json.loads).
    # struct_english has no parser -> 'n/a' (valid by construction), excluded from
    # the validity comparison.
    out = [f"{label:<22} {'n':>4} {'surf_val%':>9} {'fidelity':>9} {'±sd':>6} {'ntok':>6} {'ctok':>7} {'lat_s':>6} {'eff_tok':>8}"]
    for k in keys:
        if k not in rows:
            continue
        r = rows[k]
        eff = f"{r['eff_tokens']:.1f}" if r["eff_tokens"] != float("inf") else "inf"
        val = "n/a" if _cond_of(k) == "struct_english" else f"{r['valid_pct']:.0f}%"
        out.append(
            f"{str(k):<22} {r['n']:>4} {val:>9} {r['fidelity']:>9.3f} "
            f"{r['fidelity_sd']:>6.3f} {r['ntok']:>6.1f} {str(round(r['ctok'],1) if r['ctok'] else '-'):>7} "
            f"{r['latency']:>6.1f} {eff:>8}"
        )
    return "\n".join(out)


def fmt_decoded_table(rows, order=None, label="condition"):
    keys = order or sorted(rows)
    out = [f"{label:<22} {'dec_n':>6} {'dec_fidelity':>12} {'emit_ntok':>10}"]
    for k in keys:
        if k not in rows:
            continue
        r = rows[k]
        out.append(
            f"{str(k):<22} {r['decoded_n']:>6} {r['decoded_fidelity']:>12.3f} {r['emitted_ntok']:>10.1f}"
        )
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--enc", default=os.path.join(HERE, "results", "encode.jsonl"))
    ap.add_argument("--dec", default=os.path.join(HERE, "results", "decode.jsonl"))
    ap.add_argument("--tasks-file", default=os.path.join(HERE, "tasks.json"))
    ap.add_argument("--out", default=os.path.join(HERE, "results", "summary.md"))
    args = ap.parse_args()

    tasks = {t["id"]: t for t in json.load(open(args.tasks_file))["tasks"]}
    enc = load_jsonl(args.enc)
    dec = load_jsonl(args.dec)
    cells = build_cells(enc, dec, tasks)
    if not cells:
        print("no cells yet")
        return

    by_cond = agg(cells, lambda c: c["condition"])
    by_cl = agg(cells, lambda c: (c["condition"], c["level"]))
    by_cm = agg(cells, lambda c: (c["condition"], c["model"]))

    L = []
    L.append(f"# M5 Falsification — analysis ({len(cells)} cells, {len(enc)} encoded, {len(dec)} decoded)")
    models = sorted({c["model"] for c in cells})
    L.append(f"\nModels present: {models}")
    n_decoded = sum(1 for c in cells if c.get("decoded"))
    L.append("\n## By condition (overall) — ALL-ATTEMPT denominator")
    L.append(f"_{len(cells)} attempted cells; {n_decoded} decoded. Non-ok / empty / "
             "non-decoded encode attempts are counted as fidelity 0 here, and ntok is the "
             "attempt-mean (failed attempts carry 0 wire tokens). This is the headline metric._")
    L.append("```")
    L.append(fmt_table(by_cond, COND_ORDER, "condition"))
    L.append("```")

    # Denominator sensitivity: fidelity/tokens over DECODED messages only (the
    # rows Agent B actually recovered). AXON's emission failures are excluded, so
    # this isolates "how faithful is AXON *when it decodes*" from "how often does
    # AXON fail to emit a usable message".
    L.append("\n## Decoded-only sensitivity (fidelity & tokens over decoded messages only)")
    L.append("_Excludes failed/empty/non-decoded encodes instead of imputing 0. Read"
             " ALONGSIDE the all-attempt table: the gap between them is AXON's emission-"
             "reliability penalty, not a fidelity penalty._")
    L.append("```")
    L.append(fmt_decoded_table(by_cond, COND_ORDER, "condition"))
    L.append("```")

    L.append("\n## By condition × level\n```")
    for lvl in (1, 2, 3):
        rows = {c: by_cl[(c, lvl)] for c in COND_ORDER if (c, lvl) in by_cl}
        if rows:
            L.append(f"-- Level {lvl} --")
            L.append(fmt_table(rows, COND_ORDER, f"L{lvl} condition"))
    L.append("```")

    L.append("\n## By condition × model (size axis)\n```")
    for m in models:
        rows = {c: by_cm[(c, m)] for c in COND_ORDER if (c, m) in by_cm}
        if rows:
            L.append(f"-- {m} --")
            L.append(fmt_table(rows, COND_ORDER, "condition"))
    L.append("```")

    # Pareto + verdict
    front = pareto(by_cond)
    L.append("\n## Pareto frontier (fidelity↑ vs neutral-tokens↓)")
    L.append(f"Non-dominated conditions: **{front}**")
    L.append(f"AXON on frontier: **{'YES' if 'axon' in front else 'NO'}**")

    # AXON vs best incumbent, overall and per slice
    def verdict_slice(rows, label):
        if "axon" not in rows:
            return None
        ax = rows["axon"]
        incs = {c: rows[c] for c in INCUMBENTS if c in rows}
        if not incs:
            return None
        best_fid_c = max(incs, key=lambda c: incs[c]["fidelity"])
        best_fid = incs[best_fid_c]["fidelity"]
        # AXON earns place if: fidelity >= best incumbent (within 0.02) AND fewer tokens than that incumbent
        fid_ok = ax["fidelity"] >= best_fid - 0.02
        tok_win = ax["ntok"] < incs[best_fid_c]["ntok"]
        earns = fid_ok and tok_win
        return {
            "label": label, "axon_fid": ax["fidelity"], "axon_tok": ax["ntok"],
            "best_inc": best_fid_c, "best_inc_fid": best_fid, "best_inc_tok": incs[best_fid_c]["ntok"],
            "earns": earns,
        }

    L.append("\n## Falsification verdict — does AXON earn its place?")
    slices = [("OVERALL", by_cond)]
    for lvl in (1, 2, 3):
        rows = {c: by_cl[(c, lvl)] for c in COND_ORDER if (c, lvl) in by_cl}
        slices.append((f"Level {lvl}", rows))
    for m in models:
        rows = {c: by_cm[(c, m)] for c in COND_ORDER if (c, m) in by_cm}
        slices.append((f"model:{m}", rows))

    any_earns = False
    L.append("```")
    L.append(f"{'slice':<26} {'axon_fid':>8} {'axon_tok':>8} {'best_inc':>16} {'inc_fid':>8} {'inc_tok':>8} {'AXON_WINS':>9}")
    for label, rows in slices:
        v = verdict_slice(rows, label)
        if not v:
            continue
        any_earns = any_earns or v["earns"]
        L.append(
            f"{v['label']:<26} {v['axon_fid']:>8.3f} {v['axon_tok']:>8.1f} {v['best_inc']:>16} "
            f"{v['best_inc_fid']:>8.3f} {v['best_inc_tok']:>8.1f} {('YES' if v['earns'] else 'no'):>9}"
        )
    L.append("```")
    L.append(f"\n**AXON earns its place in at least one slice: {'YES' if any_earns else 'NO'}**")
    L.append("(earns = fidelity within 0.02 of best incumbent AND strictly fewer neutral tokens)")

    text = "\n".join(L)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as f:
        f.write(text + "\n")
    # also dump machine-readable
    with open(args.out.replace(".md", ".json"), "w") as f:
        json.dump({
            "by_condition": {k: v for k, v in by_cond.items()},
            "by_condition_level": {f"{c}|L{l}": v for (c, l), v in by_cl.items()},
            "by_condition_model": {f"{c}|{m}": v for (c, m), v in by_cm.items()},
            "pareto_front": front,
            "n_cells": len(cells),
        }, f, indent=2)
    print(text)


if __name__ == "__main__":
    main()
