#!/usr/bin/env python3
"""Rigorous detection benchmark via CONTROLLED ERROR INJECTION.

Organic errors are too few (~7 over 14 tasks) to measure detection. Instead, start from
GROUND-TRUTH-correct messages and inject KNOWN role-confusion errors (the characteristic
LLM failure: an entity from one slot placed in another). Then measure how well each
detector flags the injected field (recall) without flagging clean fields (precision/FPR).
Ground truth is exact by construction → real statistical power.

Detectors (all claude -p, independent of any sender, + shared thesaurus):
  direct / roundtrip / adversarial  + union(≥1) / majority(≥2)

Injection model: for each task, for each entity-role field (ref/text/list), make a
corrupted copy where that field's value is SWAPPED with another entity-role field's value
(intra-message role swap) — exactly the organic confusion (recipient↔target, source↔root).

Usage: python run_inject.py
"""
from __future__ import annotations
import json, os, subprocess, sys, copy, statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
M5 = os.path.join(HERE, "..", "exp_m5_falsification")
sys.path.insert(0, M5)
import conditions as C

ENTITY_KINDS = {"ref", "text", "list_set", "list_ordered"}


def gt_fields(t):
    return {k: spec.get("value") for k, spec in t["fields"].items()}


def injections(t):
    """Yield (corrupted_fields, corrupted_field_name) — one intra-message role swap each."""
    base = gt_fields(t)
    ents = [k for k in t["fields"] if t["fields"][k]["kind"] in ENTITY_KINDS]
    out = []
    for i, a in enumerate(ents):
        for b in ents:
            if a == b or base[a] == base[b]:
                continue
            c = copy.deepcopy(base)
            c[a] = base[b]            # put b's value into slot a (role swap)
            out.append((c, a))
            break                      # one swap per field a
    return out


def claude(prompt):
    try:
        r = subprocess.run(["claude", "-p", prompt], capture_output=True, text=True, timeout=120, stdin=subprocess.DEVNULL)
        return C.extract_json(r.stdout)
    except Exception:
        return ""


def framing(t, fields, mode):
    body = "\n".join(f"- {k} = {json.dumps(fields.get(k))}" for k in t["fields"])
    thes = "\n".join(f"- {k}: {C.FIELD_HINTS.get(k,'')}" for k in t["fields"])
    base = f"Sender intent:\n{t['nl_intent']}\n\nDecoded fields:\n{body}\n\nAgreed meanings:\n{thes}\n\n"
    ask = {"direct": 'For each field, is its value correct? Return ONLY JSON like {"target": false}.',
           "roundtrip": 'Restate what each field asserts, then mark each correct/wrong vs the intent. ONLY JSON like {"target": false}.',
           "adversarial": 'Assume an entity was swapped into the wrong slot; name the wrong field(s). ONLY JSON like {"target": false}.'}[mode]
    try:
        a = json.loads(claude(base + ask))
        return {k for k in t["fields"] if a.get(k) is False}
    except Exception:
        return set()


def main():
    tasks = json.load(open(os.path.join(M5, "tasks.json")))["tasks"]
    cases = []  # (task, fields, injected_field_or_None)
    for t in tasks:
        cases.append((t, gt_fields(t), None))               # clean control
        for cf, fld in injections(t):
            cases.append((t, cf, fld))                       # one injected error
    n_inj = sum(1 for _, _, f in cases if f)
    print(f"benchmark: {len(cases)} cases ({n_inj} injected errors, {len(cases)-n_inj} clean controls)\n", flush=True)
    agg = {n: dict(tp=0, fp=0, fn=0, tn=0) for n in ("direct", "roundtrip", "adversarial", "union", "majority")}
    for i, (t, fields, inj) in enumerate(cases):
        fl = {m: framing(t, fields, m) for m in ("direct", "roundtrip", "adversarial")}
        cnt = {k: sum(k in fl[m] for m in fl) for k in t["fields"]}
        fl["union"] = {k for k in t["fields"] if cnt[k] >= 1}
        fl["majority"] = {k for k in t["fields"] if cnt[k] >= 2}
        for n in agg:
            for k in t["fields"]:
                flagged = k in fl[n]; is_err = (k == inj)
                if flagged and is_err: agg[n]["tp"] += 1
                elif flagged and not is_err: agg[n]["fp"] += 1
                elif not flagged and is_err: agg[n]["fn"] += 1
                else: agg[n]["tn"] += 1
        if (i + 1) % 10 == 0:
            print(f"  {i+1}/{len(cases)} cases", flush=True)
    print(f"\n{'detector':<12}{'recall':>8}{'prec':>7}{'FPR':>7}{'tp':>5}{'fp':>5}{'fn':>5}")
    for n in ("direct", "roundtrip", "adversarial", "union", "majority"):
        d = agg[n]
        rec = d["tp"]/(d["tp"]+d["fn"]) if d["tp"]+d["fn"] else 0
        prec = d["tp"]/(d["tp"]+d["fp"]) if d["tp"]+d["fp"] else 0
        fpr = d["fp"]/(d["fp"]+d["tn"]) if d["fp"]+d["tn"] else 0
        print(f"{n:<12}{rec:>8.2f}{prec:>7.2f}{fpr:>7.2f}{d['tp']:>5}{d['fp']:>5}{d['fn']:>5}")


if __name__ == "__main__":
    main()
