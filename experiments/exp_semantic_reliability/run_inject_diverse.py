#!/usr/bin/env python3
"""Detection generality across ERROR TYPES (not just role-swaps).

The injection benchmark validated detection on clean role-swaps (recall 1.00). Real
messages fail in more ways. This injects DIVERSE known errors into ground-truth-correct
messages and measures the independent verifier's recall PER error type — testing whether
the mechanism is role-swap-specific or general.

Error types injected (one known error per case):
  role_swap     : entity field A gets entity field B's value (the characteristic confusion)
  ref_hallucin  : a ref field gets a fabricated @entity not in the intent
  enum_wrong    : an enum field gets a different (wrong) allowed value
  num_wrong     : a number field gets a clearly-wrong number
  bool_flip     : a boolean field is flipped
  list_drop     : an ordered/set list field loses an item

Detector: independent capable verifier (claude -p) + the shared thesaurus (the proven config).
Usage: python run_inject_diverse.py
"""
from __future__ import annotations
import json, os, subprocess, sys, copy, statistics as st
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
M5 = os.path.join(HERE, "..", "exp_m5_falsification")
sys.path.insert(0, M5)
import conditions as C

ENUMS = ["query", "inform", "request", "command", "propose", "accept", "reject", "counter", "delegate", "error", "subscribe"]


def gt(t):
    return {k: s.get("value") for k, s in t["fields"].items()}


def diverse_injections(t):
    base = gt(t)
    fields = t["fields"]
    ents = [k for k in fields if fields[k]["kind"] in ("ref", "text", "list_set", "list_ordered")]
    out = []  # (corrupted, field, error_type)
    for a in ents:  # role_swap
        for b in ents:
            if a != b and base[a] != base[b]:
                c = copy.deepcopy(base); c[a] = base[b]; out.append((c, a, "role_swap")); break
    for k, s in fields.items():
        c = copy.deepcopy(base); v = base[k]
        if s["kind"] == "ref":
            c[k] = "@ghost-node-xyz"; out.append((c, k, "ref_hallucin"))
        elif s["kind"] == "enum":
            alt = next((e for e in ENUMS if e != str(v).lower()), "inform"); c[k] = alt; out.append((c, k, "enum_wrong"))
        elif s["kind"] == "num":
            try:
                c[k] = float(v) * 3 + 17; out.append((c, k, "num_wrong"))
            except Exception:
                pass
        elif s["kind"] == "bool":
            c[k] = (not bool(v)); out.append((c, k, "bool_flip"))
        elif s["kind"] in ("list_ordered", "list_set") and isinstance(v, list) and len(v) > 1:
            c[k] = v[:-1]; out.append((c, k, "list_drop"))
    return out


def claude_flags(t, fields):
    body = "\n".join(f"- {k} = {json.dumps(fields.get(k))}" for k in t["fields"])
    thes = "\n".join(f"- {k}: {C.FIELD_HINTS.get(k,'')}" for k in t["fields"])
    p = (f"You are Agent B receiving a message. Sender intent:\n{t['nl_intent']}\n\nDecoded fields:\n{body}\n\n"
         f"Agreed meaning of each field:\n{thes}\n\nFor each field, is its value correct given the intent "
         '(catch wrong entities, swapped roles, wrong numbers, flipped booleans, dropped list items, '
         'hallucinated/absent values)? Return ONLY JSON like {"target": false, "retry": true}.')
    try:
        r = subprocess.run(["claude", "-p", p], capture_output=True, text=True, timeout=120, stdin=subprocess.DEVNULL)
        a = json.loads(C.extract_json(r.stdout))
        return {k for k in t["fields"] if a.get(k) is False}
    except Exception:
        return set()


def main():
    tasks = json.load(open(os.path.join(M5, "tasks.json")))["tasks"]
    by_type = defaultdict(lambda: dict(tp=0, fn=0))
    fp = tn = 0
    cases = []
    for t in tasks:
        cases.append((t, gt(t), None, "clean"))
        for cf, fld, et in diverse_injections(t):
            cases.append((t, cf, fld, et))
    n_err = sum(1 for *_, et in cases if et != "clean")
    print(f"{len(cases)} cases, {n_err} injected errors across types\n", flush=True)
    for i, (t, fields, fld, et) in enumerate(cases):
        flags = claude_flags(t, fields)
        for k in t["fields"]:
            flagged = k in flags
            if et != "clean" and k == fld:
                by_type[et]["tp" if flagged else "fn"] += 1
            elif k != fld:  # a field that is NOT the injected one → should be clean
                if flagged: fp += 1
                else: tn += 1
        if (i + 1) % 15 == 0:
            print(f"  {i+1}/{len(cases)}", flush=True)
    print(f"\n{'error type':<14}{'recall':>8}{'n':>5}")
    for et in ("role_swap", "ref_hallucin", "enum_wrong", "num_wrong", "bool_flip", "list_drop"):
        d = by_type[et]; n = d["tp"] + d["fn"]
        if n:
            print(f"{et:<14}{d['tp']/n:>8.2f}{n:>5}")
    allr = sum(by_type[e]["tp"] for e in by_type) / max(1, sum(by_type[e]["tp"] + by_type[e]["fn"] for e in by_type))
    print(f"{'OVERALL':<14}{allr:>8.2f}{n_err:>5}")
    print(f"false-positive rate on clean fields: {fp/(fp+tn):.3f} ({fp} of {fp+tn})")


if __name__ == "__main__":
    main()
