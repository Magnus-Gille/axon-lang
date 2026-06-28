#!/usr/bin/env python3
"""VoI-gated ARQ — cheap reliability by verifying only the fields that matter.

The independent-verifier ARQ catches role-confusion at recall ~1.0, but verifying EVERY
field is wasteful. Kharkevich/Stratonovich (RU) value-of-information: a field's value is how
much getting it wrong changes the RECEIVER'S ACTION. Verify only high-VoI fields →
near-full protection on what matters, at a fraction of the verify cost.

Design (on the role-swap injection benchmark):
  1. VoI ranking: an independent model scores each field 1-5 by action-impact (Kharkevich).
  2. Inject role-swaps (known ground truth), tag each by the injected field's VoI tier.
  3. Compare verify-ALL vs VoI-GATED (verify only fields with VoI >= median):
       - recall on HIGH-VoI errors (the ones that change behaviour)
       - verify COST (fraction of fields sent to the verifier)
  Also: do errors concentrate in high-VoI fields? (if so, gating is doubly efficient.)

Verifier + VoI-ranker = claude -p (independent, capable). Usage: python run_voi.py
"""
from __future__ import annotations
import json, os, subprocess, sys, copy, statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
M5 = os.path.join(HERE, "..", "exp_m5_falsification")
sys.path.insert(0, M5)
import conditions as C
ENTITY_KINDS = {"ref", "text", "list_set", "list_ordered"}


def claude(prompt):
    try:
        r = subprocess.run(["claude", "-p", prompt], capture_output=True, text=True, timeout=120, stdin=subprocess.DEVNULL)
        return C.extract_json(r.stdout)
    except Exception:
        return ""


def gt(t):
    return {k: s.get("value") for k, s in t["fields"].items()}


def hints_of(t):
    return t.get("hints") or {k: C.FIELD_HINTS.get(k, "") for k in t["fields"]}


def voi_rank(t):
    h = hints_of(t)
    body = "\n".join(f"- {k}: {h.get(k,'')}" for k in t["fields"])
    p = (f"An agent receives this message and ACTS on it. Intent context:\n{t['nl_intent']}\n\nFields:\n{body}\n\n"
         "Rate each field 1-5 by VALUE OF INFORMATION = how much a WRONG value changes what the "
         "receiver DOES (5 = wrong value => wrong action/target/safety; 1 = cosmetic/rationale). "
         'Return ONLY JSON like {"speech_act": 5, "rationale": 1}.')
    try:
        a = json.loads(claude(p)); return {k: float(a.get(k, 3)) for k in t["fields"]}
    except Exception:
        return {k: 3.0 for k in t["fields"]}


def injections(t):
    base = gt(t); ents = [k for k in t["fields"] if t["fields"][k]["kind"] in ENTITY_KINDS]
    out = []
    for a in ents:
        for b in ents:
            if a != b and base[a] != base[b]:
                c = copy.deepcopy(base); c[a] = base[b]; out.append((c, a)); break
    return out


def verify_field(t, fields, k):
    h = hints_of(t)
    p = (f"Sender intent:\n{t['nl_intent']}\n\nField '{k}' = {json.dumps(fields.get(k))}\n"
         f"'{k}' should mean: {h.get(k,'')}\nIs this value correct? Return ONLY JSON {{\"correct\": true|false}}.")
    try:
        return json.loads(claude(p)).get("correct") is False  # True = flagged wrong
    except Exception:
        return False


def main():
    tasks = json.load(open(os.path.join(M5, "tasks.json")))["tasks"]
    # VoI per field
    voi = {t["id"]: voi_rank(t) for t in tasks}
    allv = [v for t in tasks for v in voi[t["id"]].values()]
    med = st.median(allv)
    print(f"VoI median={med:.1f}; high-VoI = VoI>={med}")

    # build injected cases
    cases = []
    for t in tasks:
        for cf, fld in injections(t):
            cases.append((t, cf, fld))
    hi_err = sum(1 for t, _, f in cases if voi[t["id"]][f] >= med)
    print(f"{len(cases)} injected errors; {hi_err} in HIGH-VoI fields ({100*hi_err/len(cases):.0f}%)\n")

    # verify-ALL vs VoI-GATED
    res = {"all": dict(hi_caught=0, lo_caught=0, calls=0), "voi": dict(hi_caught=0, lo_caught=0, calls=0)}
    tot_fields = sum(len(t["fields"]) for t, _, _ in cases)
    hi_errs = lo_errs = 0
    for t, fields, fld in cases:
        is_hi = voi[t["id"]][fld] >= med
        hi_errs += is_hi; lo_errs += (not is_hi)
        for mode in ("all", "voi"):
            for k in t["fields"]:
                if mode == "voi" and voi[t["id"]][k] < med:
                    continue
                res[mode]["calls"] += 1
                if k == fld and verify_field(t, fields, k):
                    res[mode]["hi_caught" if is_hi else "lo_caught"] += 1
    for mode in ("all", "voi"):
        d = res[mode]
        hi_rec = d["hi_caught"]/hi_errs if hi_errs else 0
        cost = d["calls"]/(tot_fields)  # verify calls per (case×field) — relative
        print(f"{mode:<5} high-VoI recall={hi_rec:.2f}  low-VoI caught={d['lo_caught']}/{lo_errs}  verify-calls={d['calls']} ({cost:.2f}x of verify-all-field-slots)")
    print("\n(VoI-gated should match verify-all on HIGH-VoI recall at far fewer calls — cheap reliability where it matters.)")


if __name__ == "__main__":
    main()
