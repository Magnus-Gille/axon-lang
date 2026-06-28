#!/usr/bin/env python3
"""In-context deterministic-parse pilot — effective marginal-token cost.

The one regime the cross-model debate (debate/axon-falsification-pivot-*) left
genuinely open for AXON: a message that is model-visible / token-billed (in a
prompt), parsed by a DETERMINISTIC consumer (no LLM tolerance — invalid input is
rejected outright, unlike the LLM decoder in the M5 study), with NO compression
layer (you can't gzip a prompt). There AXON's raw density is a real ~28% token
saving, but its ~33% invalid-emission rate becomes a HARD cost.

We compute the in-context cost under a reject-and-retry deterministic protocol,
granting AXON the BEST case ("parsed => correct", fidelity=1 once it parses):

    effective_marginal_tokens = mean_tokens / deterministic_parse_rate

(geometric retry: expected attempts to land one parseable message = 1/p). This
is generous to AXON — it ignores any deterministic field-extraction loss. If AXON
loses even here, the in-context regime is settled.

`deterministic_parse_rate` is exactly the M5 `valid` field: AXON via the reference
grammar, JSON via json.loads, json_schema via the envelope contract. AXON+repair
applies the deterministic normalizer (axon_repair) first.

Reuses the M5 corpus (no box). New competitive arms (custom DSL, structured
outputs) are scored by the same formula once collected (see PLAN.md).
"""
from __future__ import annotations
import json, os, sys, statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
M5 = os.path.join(HERE, "..", "exp_m5_falsification")
sys.path.insert(0, M5)
import axon_repair as R  # deterministic normalizer + parser check

ENC = os.path.join(M5, "results", "encode.jsonl")


def main():
    rows = [json.loads(l) for l in open(ENC)]
    # restrict to capable senders (the regime assumes both ends are capable);
    # use all models too for an "all-sender" row.
    CAPABLE = {"qwen3-30b-instruct", "gpt-oss-120b", "qwen3-coder-next-80b"}

    def stats_for(cond, models=None, repair=False):
        ms = [r for r in rows if r["condition"] == cond and r.get("ok")
              and (r.get("msg") or "").strip()
              and (models is None or r["model"] in models)]
        if not ms:
            return None
        n = len(ms)
        toks = st.mean(r["neutral_tokens"] for r in ms)
        if repair:
            # deterministic parse rate AFTER the free normalizer
            valid = sum(1 for r in ms if R.parses(r["msg"]) or R.parses(R.repair(r["msg"])[0]))
        else:
            valid = sum(1 for r in ms if r.get("valid"))
        p = valid / n
        eff = toks / p if p > 0 else float("inf")
        return dict(n=n, tok=toks, parse_rate=p, eff=eff)

    print("IN-CONTEXT DETERMINISTIC-CONSUMER COST (reject-retry; parsed=>correct, best case for AXON)")
    print("effective marginal tokens = mean_tokens / deterministic_parse_rate\n")
    for label, models in [("ALL senders", None), ("CAPABLE senders only", CAPABLE)]:
        print(f"== {label} ==")
        print(f"{'format':<22}{'n':>5}{'tok':>7}{'det_parse%':>11}{'eff_tok/correct':>16}")
        arms = [
            ("axon", "axon", False),
            ("axon+repair", "axon", True),
            ("json (compact)", "json", False),
            ("json_schema", "json_schema", False),
        ]
        res = {}
        for name, cond, rep in arms:
            s = stats_for(cond, models, rep)
            if s:
                res[name] = s
                print(f"{name:<22}{s['n']:>5}{s['tok']:>7.1f}{100*s['parse_rate']:>10.0f}%{s['eff']:>16.1f}")
        # verdict
        if "axon" in res and "json (compact)" in res:
            a, j = res["axon"]["eff"], res["json (compact)"]["eff"]
            ar = res.get("axon+repair", {}).get("eff")
            print(f"  -> raw AXON {'BEATS' if a < j else 'LOSES TO'} compact JSON "
                  f"({a:.1f} vs {j:.1f} eff-tok); AXON+repair {ar:.1f}" if ar else "")
        print()
    print("(Generous to AXON: grants parsed=>correct and independent geometric retries.")
    print(" A custom task-DSL arm and structured-outputs arm are scored by the same")
    print(" formula once collected — see PLAN.md.)")


if __name__ == "__main__":
    main()
