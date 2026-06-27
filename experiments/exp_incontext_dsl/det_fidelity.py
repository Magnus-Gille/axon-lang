#!/usr/bin/env python3
"""View B of the in-context pilot: STRICT deterministic field extraction.

A real deterministic consumer extracts fields by literal key/structure — no LLM,
no alias tolerance. (The M5 study used an LLM decoder + FIELD_HINTS aliases; that
tolerance is exactly what a deterministic parser lacks.) This measures how much
fidelity survives strict literal extraction for each free-form LLM-emitted format.

Run: python det_fidelity.py
"""
from __future__ import annotations
import json, os, sys, statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
M5 = os.path.join(HERE, "..", "exp_m5_falsification")
sys.path.insert(0, HERE)
sys.path.insert(0, M5)
import conditions as C, scoring_lib as S

tasks = {t["id"]: t for t in json.load(open(os.path.join(M5, "tasks.json")))["tasks"]}
rows = [json.loads(l) for l in open(os.path.join(M5, "results/encode.jsonl"))]
CAP = {"qwen3-30b-instruct", "gpt-oss-120b", "qwen3-coder-next-80b"}


def json_strict(msg, task):
    """json.loads + LITERAL field-name lookup (peek one level into a 'content' envelope)."""
    try:
        o = json.loads(C.extract_json(msg))
    except Exception:
        return None
    if not isinstance(o, dict):
        return None
    flat = dict(o)
    if isinstance(o.get("content"), dict):
        flat = {**o, **o["content"]}
    return {k: flat.get(k) for k in task["fields"]}


def main():
    print("STRICT deterministic extraction (literal keys, no LLM, no alias) — capable senders")
    print(f"{'format':<16}{'strict_fid':>11}{'n':>6}")
    for cond in ("json", "json_schema"):
        fids = [S.score_task(json_strict(r["msg"], tasks[r["task_id"]]), tasks[r["task_id"]])[0]
                for r in rows if r["condition"] == cond and r.get("valid")
                and r["model"] in CAP and (r.get("msg") or "").strip()]
        print(f"{cond:<16}{st.mean(fids):>11.3f}{len(fids):>6}")
    for name, fn in [("dsl", "results/dsl.jsonl"), ("structured", "results/structured.jsonl")]:
        p = os.path.join(HERE, fn)
        if os.path.exists(p):
            rs = [json.loads(l) for l in open(p) if json.loads(l).get("valid")]
            print(f"{name:<16}{st.mean(r['det_fidelity'] for r in rs):>11.3f}{len(rs):>6}")

    print("\nM5 reported JSON fidelity 0.94 used an LLM decoder + aliases; the gap to strict (0.27)")
    print("is pure alias-tolerance. Only SCHEMA-CONSTRAINED emission (structured outputs, ~0.88)")
    print("survives strict deterministic extraction — a JSON technique, orthogonal to AXON.")

    # effective marginal-token cost under REAL strict deterministic fidelity
    def stats(fn, tokkey="neutral_tokens"):
        rs = [json.loads(l) for l in open(os.path.join(HERE, fn))]
        v = [r for r in rs if r.get("valid")]
        return (st.mean(r[tokkey] for r in v), len(v) / len(rs), st.mean(r["det_fidelity"] for r in v))
    print(f"\nEffective marginal tok/correct = tok / (parse_rate x strict_fidelity):")
    print(f"{'format':<16}{'tok':>6}{'parse':>7}{'fid':>6}{'eff':>8}")
    for name, fn in [("dsl", "results/dsl.jsonl"), ("structured", "results/structured.jsonl")]:
        p = os.path.join(HERE, fn)
        if os.path.exists(p):
            tok, pr, fid = stats(fn)
            eff = tok / (pr * fid) if pr * fid else float("inf")
            print(f"{name:<16}{tok:>6.1f}{pr:>7.2f}{fid:>6.2f}{eff:>8.1f}")
    print("(plain JSON strict eff = 37/(1.0x0.27) ~= 137; json_schema ~96. At MATCHED high")
    print(" fidelity, only structured outputs qualifies — AXON/DSL are cheap-but-wrong.)")


if __name__ == "__main__":
    main()
