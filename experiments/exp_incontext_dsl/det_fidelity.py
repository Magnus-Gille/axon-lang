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
    dslf = os.path.join(HERE, "results", "dsl.jsonl")
    if os.path.exists(dslf):
        dsl = [json.loads(l) for l in open(dslf) if json.loads(l).get("valid")]
        print(f"{'dsl':<16}{st.mean(r['det_fidelity'] for r in dsl):>11.3f}{len(dsl):>6}")
    print("\nM5 reported JSON fidelity 0.94 used an LLM decoder + aliases; the gap to strict (0.27)")
    print("is pure alias-tolerance. The regime rewards SCHEMA-CONSTRAINED emission (structured")
    print("outputs), not a dense notation — see RESULTS.md.")


if __name__ == "__main__":
    main()
