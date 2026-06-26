#!/usr/bin/env python3
"""Deterministic, meaning-preserving normalizer for common AXON emission errors.

Tests whether AXON's "capability floor" is largely a SPEC-STRICTNESS gap: a small
set of safe surface-syntax repairs that a lenient parser/preprocessor could apply,
recovering messages the strict reference grammar rejects WITHOUT changing meaning.

Three repairs (safe — only applied to messages the strict grammar already rejects,
so over-firing can never break a valid message, only fail to help an invalid one):
  R1 multi-receiver routing:  (@X>@a, @b, @c)  -> (@X>[@a,@b,@c])
  R2 bare clock-time literal:  02:00           -> "02:00"  (string, not a record `:`)
  R3 bare labelled record:     alert{level:3}  -> #alert{level:3}  (tag a record)

repair(msg) -> (repaired_text, [rules_fired]).  `python axon_repair.py --selftest`.
"""
from __future__ import annotations
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "src"))


def parses(msg: str) -> bool:
    try:
        import axon_parser as ap
        ap.Parser(ap.Lexer(msg).tokenize()).parse()
        return True
    except Exception:
        return False


def repair(msg: str):
    fired = []
    # R1: collapse a comma-separated receiver list in the routing envelope into [...]
    new = re.sub(
        r">\s*(@[\w-]+(?:\s*,\s*@[\w-]+)+)\s*\)",
        lambda mo: ">[" + re.sub(r"\s*,\s*", ",", mo.group(1)) + "])",
        msg,
    )
    if new != msg:
        fired.append("R1_routing_list")
        msg = new
    # R2: quote bare clock-times so `:` isn't read as a record separator
    new = re.sub(r'(?<!")\b(\d{1,2}:\d{2})\b(?!")', r'"\1"', msg)
    if new != msg:
        fired.append("R2_quote_time")
        msg = new
    # R3: a bare identifier immediately followed by a record becomes a tag
    new = re.sub(r"(?<![#\w@$])([a-zA-Z][\w-]*)\{", r"#\1{", msg)
    if new != msg:
        fired.append("R3_tag_record")
        msg = new
    return msg, fired


def _selftest():
    cases = [
        ("PUB(@p>@w1, @w2, @w3): x()", "R1_routing_list"),
        ("INF(@a>@b): t(02:00..04:00)", "R2_quote_time"),
        ("INF(@m>@admin): alert{level:3}", "R3_tag_record"),
    ]
    for src, rule in cases:
        assert not parses(src), f"precondition: {src} should be invalid"
        fixed, fired = repair(src)
        assert rule in fired, (src, fired)
        assert parses(fixed), f"repair did not make it parse: {src} -> {fixed}"
    # a valid message must be left untouched (idempotence on good input)
    good = "QRY(@a>@b): status(@svc)"
    assert repair(good) == (good, [])
    print("axon_repair selftest: ALL PASS")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        _selftest()
    else:
        print("usage: python axon_repair.py --selftest")
