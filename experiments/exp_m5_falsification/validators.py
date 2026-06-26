#!/usr/bin/env python3
"""Per-condition SURFACE validity checks for the falsification campaign.

"Surface validity" = does the emitted message parse / conform to its format's
structural contract, *before* any field extraction. The check is deliberately
**format-specific**, and the conditions are NOT equally strict by nature — so we
make each as strict as its format admits and report the metric as
`surface_valid%` (never just "valid%"), with the per-condition semantics spelled
out so the comparison isn't read as apples-to-apples:

  axon           : parses under the reference AXON grammar (src/axon_parser.py)
  json           : parses as a JSON value (json.loads)
  json_schema    : parses AND conforms to the envelope contract — speech_act in
                   the allowed set, and sender / receiver / content all present
  fipa_acl       : balanced parens AND a known performative head AND the
                   :sender / :receiver / :content slots present
  struct_english : N/A — free prose has no parser; "valid by construction".
                   surface_valid() returns None for it; it is reported as "n/a"
                   and excluded from the cross-condition validity comparison.

A previous version checked json_schema with a bare ``json.loads`` and fipa_acl
with paren-balance only, which made "64% (axon) vs 97-100%" an apples-to-oranges
comparison (a strict format-specific validator for AXON vs. very soft checks for
the rest). Re-validating the committed corpus with these stricter checks gives
*identical* percentages (the envelope/slot contracts were already satisfied by
every parse-OK message), so the gap is robust — but the metric is now honestly
strict on every condition.

Run ``python validators.py --selftest`` for red/green coverage.
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "src"))

# Allowed vocabularies, kept in lockstep with the encoder prompts in conditions.py.
JSON_SCHEMA_ACTS = {
    "query", "inform", "request", "command", "propose", "accept",
    "reject", "counter", "delegate", "error", "subscribe",
}
FIPA_PERFORMATIVES = [
    "query-ref", "inform", "request", "cfp", "propose", "accept-proposal",
    "reject-proposal", "agree", "failure", "subscribe",
]


def _extract_json(msg: str) -> str:
    """Pull the first balanced JSON object out of a reply (mirrors conditions.extract_json)."""
    import conditions as C  # local import: avoids a hard dep when only AXON is checked
    return C.extract_json(msg)


def axon_valid(msg: str) -> bool:
    try:
        import axon_parser as ap

        msgs = ap.Parser(ap.Lexer(msg).tokenize()).parse()
        return len(msgs) >= 1
    except Exception:
        return False


def json_valid(msg: str) -> bool:
    try:
        json.loads(_extract_json(msg))
        return True
    except Exception:
        return False


def json_schema_valid(msg: str) -> bool:
    """Parse AND conform to the envelope contract."""
    try:
        obj = json.loads(_extract_json(msg))
    except Exception:
        return False
    if not isinstance(obj, dict):
        return False
    act = str(obj.get("speech_act", "")).strip().lower()
    return (
        act in JSON_SCHEMA_ACTS
        and "sender" in obj
        and "receiver" in obj
        and "content" in obj
    )


def fipa_valid(msg: str) -> bool:
    """Balanced parens AND a known performative head AND :sender/:receiver/:content slots."""
    s = (msg or "").strip()
    if not (s.startswith("(") and s.count("(") == s.count(")") and s.count("(") >= 1):
        return False
    head = s[1:].lstrip()
    if not any(head.startswith(p) for p in FIPA_PERFORMATIVES):
        return False
    return ":sender" in s and ":receiver" in s and ":content" in s


def surface_valid(condition: str, msg: str, ok: bool = True):
    """Surface validity for a condition's message.

    Returns True/False, or None for struct_english (N/A — no parser). A non-ok
    encode (model error / empty) is False for any parseable condition.
    """
    if condition == "struct_english":
        return None  # N/A: prose has no structural contract
    if not ok or not msg or not msg.strip():
        return False
    if condition == "axon":
        return axon_valid(msg)
    if condition == "json":
        return json_valid(msg)
    if condition == "json_schema":
        return json_schema_valid(msg)
    if condition == "fipa_acl":
        return fipa_valid(msg)
    return False


# ── self-test (red/green) ───────────────────────────────────────────────────

def _selftest():
    # AXON
    assert axon_valid("QRY(@a>@b): status(@service-x)")
    assert not axon_valid("CPU_exceeded_95%")  # units in identifier — real failure mode

    # plain JSON — any well-formed object/value parses
    assert json_valid('{"act":"query","to":"@b"}')
    assert not json_valid("{not json}")

    # json_schema — envelope contract is enforced, not just json.loads
    good = '{"speech_act":"query","sender":"@a","receiver":"@b","content":{"subject":"status"}}'
    assert json_schema_valid(good)
    assert json_valid(good)  # also valid as bare json
    # well-formed JSON but NOT the envelope -> json passes, json_schema FAILS
    flat = '{"act":"query","to":"@b","subject":"status"}'
    assert json_valid(flat)
    assert not json_schema_valid(flat), "flat JSON must fail the envelope contract"
    # unknown speech act -> fail
    assert not json_schema_valid('{"speech_act":"frobnicate","sender":"@a","receiver":"@b","content":{}}')
    # missing content -> fail
    assert not json_schema_valid('{"speech_act":"query","sender":"@a","receiver":"@b"}')

    # FIPA — performative + slots, not just balanced parens
    fok = '(query-ref :sender @a :receiver @b :content "(status @service-x)" :ontology agents)'
    assert fipa_valid(fok)
    # balanced parens but no slots / no performative -> FAILS (old check would pass)
    assert not fipa_valid("(status @service-x)"), "bare balanced parens must fail strict FIPA"
    assert not fipa_valid('(query-ref :sender @a :content "(x)")'), "missing :receiver must fail"

    # struct_english -> N/A
    assert surface_valid("struct_english", "I query agent B for status.") is None

    # dispatcher + non-ok / empty
    assert surface_valid("axon", "QRY(@a>@b): status(@s)") is True
    assert surface_valid("json_schema", flat) is False
    assert surface_valid("json", "", ok=True) is False
    assert surface_valid("axon", "QRY(@a>@b): status(@s)", ok=False) is False

    print("validators selftest: ALL PASS")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        _selftest()
    else:
        print("usage: python validators.py --selftest")
