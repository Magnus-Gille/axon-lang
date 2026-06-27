#!/usr/bin/env python3
"""Wild experiment 3 — semantic round-trip DETECTION + ARQ patch.

The detector half of the problem (catch valid-but-wrong), built from the cross-lingual
synthesis's strongest convergence: two-phase semantic ARQ (Burnashev decision-feedback ×
Clark grounding × Chinese SemHARQ) + the listener>speaker asymmetry (mech 2).

Key subtlety: the noise source is the SENDER (the encoder errs), so a self-checksum is
consistent with its own error and detects nothing. Detection needs an INDEPENDENT view —
a fresh RECEIVER-framed pass judging the message against the sender-held intent.

We test the asymmetry directly: same model, two verifier framings —
  self    : "you GENERATED this; which fields are wrong?"   (generator self-critique)
  receiver: "you RECEIVED this; does each field match the intent?" (receiver-as-evaluator)
Then ARQ-patch the flagged fields and re-score.

Metric: detection recall/precision of actually-wrong fields; fidelity lift after patch.
Baseline = bare structured outputs (~0.89) so there are real systematic errors to catch.

Usage: python run_detect.py --model qwen3-30b-instruct
"""
from __future__ import annotations
import argparse, json, os, sys, statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
PILOT = os.path.join(HERE, "..", "exp_incontext_dsl"); M5 = os.path.join(HERE, "..", "exp_m5_falsification")
sys.path.insert(0, PILOT); sys.path.insert(0, M5)
from run_structured import schema_for, SYS
import conditions as C, scoring_lib as S
from m5_client import chat


def emit_bare(model, t):
    r = chat(model, [{"role": "system", "content": SYS},
                     {"role": "user", "content": f"Intent:\n{t['nl_intent']}\n\nEmit the JSON object."}],
             max_tokens=600, temperature=0.2, response_format=schema_for(t))
    try:
        o = json.loads(r["content"]); return o if isinstance(o, dict) else {}
    except Exception:
        return {}


def verify(model, t, fields, framing, thesaurus=False):
    if framing.startswith("receiver"):
        head = ("You are Agent B who RECEIVED this message from Agent A. The sender's intent was:\n"
                f"{t['nl_intent']}\nThe message decoded to these field values:")
    else:  # self
        head = ("You (Agent A) GENERATED this message for the intent below. Re-check your own work.\n"
                f"Intent:\n{t['nl_intent']}\nYour message field values:")
    body = "\n".join(f"- {k} = {json.dumps(fields.get(k))}" for k in t["fields"])
    if thesaurus:
        body += "\n\nThe agreed meaning of each field (the shared schema contract):\n" + \
                "\n".join(f"- {k}: {C.FIELD_HINTS.get(k,'')}" for k in t["fields"])
    example = "{" + ", ".join('"%s": true|false' % k for k in t["fields"]) + "}"
    ask = ("\n\nFor EACH field, judge whether its VALUE correctly captures the intent (watch for "
           "role confusion: recipient vs target/source, cause vs source). "
           "Return ONLY JSON mapping each field name to true (correct) or false (wrong), e.g. "
           + example)
    r = chat(model, [{"role": "user", "content": head + "\n" + body + ask}], max_tokens=300, temperature=0.0)
    try:
        a = json.loads(C.extract_json(r["content"]))
        return {k: (a.get(k) is False) for k in t["fields"]}  # True = flagged WRONG
    except Exception:
        return {k: False for k in t["fields"]}


def patch(model, t, fields, flagged):
    out = dict(fields)
    for k in t["fields"]:
        if not flagged.get(k):
            continue
        hint = C.FIELD_HINTS.get(k, "")
        r = chat(model, [{"role": "user", "content":
                 f"Intent:\n{t['nl_intent']}\n\nThe field '{k}' means: {hint}\n"
                 f"Give ONLY the correct value for '{k}' (a JSON value, no key, no prose)."}],
                 max_tokens=120, temperature=0.0)
        try:
            out[k] = json.loads(C.extract_json(r["content"]) or r["content"].strip())
        except Exception:
            out[k] = r["content"].strip()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="qwen3-30b-instruct")
    args = ap.parse_args()
    tasks = json.load(open(os.path.join(M5, "tasks.json")))["tasks"]
    m = args.model
    CONDS = [("self", False), ("receiver", False), ("receiver+thesaurus", True)]
    det = {name: dict(tp=0, fp=0, fn=0) for name, _ in CONDS}
    base_fid, patched_fid = [], []
    for t in tasks:
        fields = {f: emit_bare(m, t).get(f) for f in t["fields"]}
        # ground-truth per-field wrongness
        wrong = {k: S.score_field(t["fields"][k], fields.get(k)) < 1.0 for k in t["fields"]}
        base_fid.append(S.score_task(fields, t)[0])
        for name, thes in CONDS:
            fr = "receiver" if name.startswith("receiver") else "self"
            flagged = verify(m, t, fields, fr, thesaurus=thes)
            for k in t["fields"]:
                if flagged[k] and wrong[k]: det[name]["tp"] += 1
                elif flagged[k] and not wrong[k]: det[name]["fp"] += 1
                elif not flagged[k] and wrong[k]: det[name]["fn"] += 1
        # ARQ patch using the thesaurus-equipped receiver detector
        flagged = verify(m, t, fields, "receiver", thesaurus=True)
        patched_fid.append(S.score_task(patch(m, t, fields, flagged), t)[0])
    print(f"[{m}] baseline fidelity={st.mean(base_fid):.3f}  post-ARQ(thesaurus-detect+patch)={st.mean(patched_fid):.3f}  "
          f"delta={st.mean(patched_fid)-st.mean(base_fid):+.3f}\n")
    print(f"{'detector':<20}{'recall':>8}{'precision':>11}{'tp':>5}{'fp':>5}{'fn':>5}")
    for fr, _ in CONDS:
        d = det[fr]; rec = d["tp"]/(d["tp"]+d["fn"]) if d["tp"]+d["fn"] else 0
        prec = d["tp"]/(d["tp"]+d["fp"]) if d["tp"]+d["fp"] else 0
        print(f"{fr:<10}{rec:>8.2f}{prec:>11.2f}{d['tp']:>5}{d['fp']:>5}{d['fn']:>5}")
    print("\n(listener-speaker asymmetry predicts receiver-framing recall > self-framing)")


if __name__ == "__main__":
    main()
