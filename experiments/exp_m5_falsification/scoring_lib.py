#!/usr/bin/env python3
"""Field-level fidelity scoring for the falsification campaign.

A task carries a ground-truth field tuple. The decoder (Agent B) recovers a flat
JSON object keyed by the same field names. We score each field in [0,1] by its
declared `kind`, and the task fidelity is the mean over fields. Designed to be
generous to surface form (key/case/unit/synonym variation) but strict about
*semantics* (wrong value, dropped step, flipped boolean → 0).

Run `python scoring_lib.py --selftest` to exercise the matchers (red/green).
"""
from __future__ import annotations

import re
import sys


def _norm(x) -> str:
    if x is None:
        return ""
    s = str(x).strip().lower()
    s = s.lstrip("@").strip("\"'`")
    s = re.sub(r"\s+", " ", s)
    return s.strip()


# AXON / FIPA performative abbreviations <-> words. Treating QRY ≡ query is
# correct decoding of the format, so it is fair (not gaming) to credit it.
_ABBREV = {
    "qry": "query", "rpl": "reply", "inf": "inform", "req": "request",
    "cmd": "command", "pro": "propose", "acc": "accept", "rej": "reject",
    "ctr": "counter", "del": "delegate", "err": "error", "ack": "acknowledge",
    "sub": "subscribe", "pub": "publish", "nak": "reject", "dny": "deny",
    "cfm": "confirm", "cfp": "request",
}


def _expand(s) -> set[str]:
    s = _norm(s)
    out = {s, s.replace("-", "_"), s.replace("_", ""), s.replace("_", " ")}
    if s in _ABBREV:
        out.add(_ABBREV[s])
    for k, v in _ABBREV.items():
        if v == s:
            out.add(k)
    return {x for x in out if x}


def _tokens(s: str) -> set[str]:
    return {t for t in re.split(r"[^a-z0-9]+", _norm(s)) if t}


def _contain(a: str, b: str) -> bool:
    a, b = _norm(a), _norm(b)
    if len(a) >= 3 and a in b:
        return True
    if len(b) >= 3 and b in a:
        return True
    return False


def _first_num(x):
    if isinstance(x, (int, float)):
        return float(x)
    if isinstance(x, dict):
        for k in ("value", "val", "amount", "n"):
            if k in x:
                return _first_num(x[k])
    m = re.search(r"-?\d+(?:\.\d+)?", str(x).replace(",", ""))
    return float(m.group()) if m else None


def _to_bool(x):
    if isinstance(x, bool):
        return x
    s = _norm(x)
    if s in ("true", "t", "yes", "y", "1"):
        return True
    if s in ("false", "f", "no", "n", "0"):
        return False
    return None


def _as_list(x):
    if isinstance(x, list):
        return x
    if x is None:
        return []
    s = str(x)
    # split on arrows, commas, semicolons, ' and '
    parts = re.split(r"->|=>|,|;|\band\b|\bthen\b|\|", s)
    return [p for p in (p.strip() for p in parts) if p]


def _item_match(a, b) -> bool:
    if _norm(a) == _norm(b):
        return True
    if _contain(a, b):
        return True
    ta, tb = _tokens(a), _tokens(b)
    if ta and tb and len(ta & tb) / len(ta | tb) >= 0.5:
        return True
    return False


def _lcs(gt: list, rec: list) -> int:
    n, m = len(gt), len(rec)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n - 1, -1, -1):
        for j in range(m - 1, -1, -1):
            if _item_match(gt[i], rec[j]):
                dp[i][j] = 1 + dp[i + 1][j + 1]
            else:
                dp[i][j] = max(dp[i + 1][j], dp[i][j + 1])
    return dp[0][0]


def score_field(spec: dict, recovered) -> float:
    kind = spec["kind"]
    val = spec.get("value")
    alts = spec.get("alts", [])
    if recovered is None or (isinstance(recovered, str) and not recovered.strip()):
        return 0.0

    if kind == "enum":
        cand_exp: set[str] = set()
        for c in [val, *alts]:
            cand_exp |= _expand(c)
        rec_exp = _expand(recovered) | _tokens(recovered)
        if cand_exp & rec_exp:
            return 1.0
        r = _norm(recovered)
        if any(_contain(r, c) for c in cand_exp if len(c) >= 3):
            return 1.0
        return 0.0

    if kind == "ref":
        r = _norm(recovered)
        g = _norm(val)
        return 1.0 if (r == g or _contain(r, g)) else 0.0

    if kind == "text":
        r, g = _norm(recovered), _norm(val)
        if r == g or _contain(r, g):
            return 1.0
        tr, tg = _tokens(r), _tokens(g)
        if not tg:
            return 0.0
        j = len(tr & tg) / len(tr | tg) if (tr | tg) else 0.0
        return 1.0 if j >= 0.5 else round(j, 3)

    if kind == "num":
        rn = _first_num(recovered)
        if rn is None:
            return 0.0
        g = float(val)
        if abs(g) < 1e-9:
            return 1.0 if abs(rn) < 1e-9 else 0.0
        rel = abs(rn - g) / abs(g)
        if rel <= 0.02 or abs(rn - g) <= 0.5:
            return 1.0
        return 0.0

    if kind == "bool":
        rb = _to_bool(recovered)
        return 1.0 if rb is not None and rb == bool(val) else 0.0

    if kind == "list_ordered":
        gt = list(val)
        rec = _as_list(recovered)
        if not gt:
            return 1.0
        return round(_lcs(gt, rec) / len(gt), 3)

    if kind == "list_set":
        gt = list(val)
        rec = _as_list(recovered)
        if not gt:
            return 1.0
        matched = sum(1 for g in gt if any(_item_match(g, r) for r in rec))
        union = len(gt) + max(0, len(rec) - matched)
        return round(matched / union, 3) if union else 0.0

    raise ValueError(f"unknown field kind: {kind}")


def score_task(recovered: dict, task: dict) -> tuple[float, dict]:
    """Return (fidelity in [0,1], per-field score dict)."""
    fields = task["fields"]
    recovered = recovered or {}
    # tolerate decoder key variation: build a normalized lookup
    norm_rec = {_norm(k): v for k, v in recovered.items()} if isinstance(recovered, dict) else {}
    per = {}
    for fname, spec in fields.items():
        if isinstance(recovered, dict) and fname in recovered:
            rv = recovered[fname]
        else:
            rv = norm_rec.get(_norm(fname))
        per[fname] = score_field(spec, rv)
    fidelity = sum(per.values()) / len(per) if per else 0.0
    return round(fidelity, 4), per


# ── self-test (red/green) ───────────────────────────────────────────────────

def _selftest():
    T = {
        "fields": {
            "speech_act": {"kind": "enum", "value": "request", "alts": ["command", "req"]},
            "target": {"kind": "ref", "value": "pipeline"},
            "uptime": {"kind": "num", "value": 99.7, "unit": "%"},
            "retry": {"kind": "bool", "value": False},
            "url": {"kind": "text", "value": "https://api.example.com/data"},
            "steps": {"kind": "list_ordered", "value": ["fetch", "parse", "store"]},
            "actions": {"kind": "list_set", "value": ["analyze", "summarize", "validate"]},
        }
    }
    # perfect recovery
    perfect = {
        "speech_act": "request", "target": "@pipeline", "uptime": 99.7, "retry": False,
        "url": "https://api.example.com/data", "steps": ["fetch", "parse", "store"],
        "actions": ["validate", "analyze", "summarize"],
    }
    f, per = score_task(perfect, T)
    assert f == 1.0, (f, per)

    # synonyms / surface variation still perfect-ish
    syn = {
        "speech_act": "CMD", "target": "pipeline", "uptime": "99.7%", "retry": "no",
        "url": "https://api.example.com/data", "steps": "fetch -> parse -> store",
        "actions": ["Analyze", "Validate", "Summarize"],
    }
    f2, per2 = score_task(syn, T)
    assert f2 == 1.0, (f2, per2)

    # semantic errors must drop score
    bad = {
        "speech_act": "inform", "target": "@db", "uptime": 50, "retry": True,
        "url": "https://other.com", "steps": ["store", "fetch"], "actions": ["analyze"],
    }
    f3, per3 = score_task(bad, T)
    assert per3["speech_act"] == 0.0, per3
    assert per3["retry"] == 0.0, per3
    assert per3["uptime"] == 0.0, per3
    assert per3["steps"] < 1.0, per3            # wrong order / missing item
    assert per3["actions"] < 0.5, per3          # only 1 of 3, no credit for missing
    assert f3 < 0.4, (f3, per3)

    # missing everything → 0
    f4, _ = score_task({}, T)
    assert f4 == 0.0, f4

    # partial order credit: 2 of 3 in order
    part = dict(perfect)
    part["steps"] = ["fetch", "store"]          # dropped 'parse' but order ok -> 2/3
    _, perp = score_task(part, T)
    assert abs(perp["steps"] - 2 / 3) < 0.01, perp["steps"]

    print("scoring_lib selftest: ALL PASS")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        _selftest()
    else:
        print("usage: python scoring_lib.py --selftest")
