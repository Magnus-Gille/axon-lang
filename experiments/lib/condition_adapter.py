"""
Condition-specific validation dispatch for Exp 0.

Each experimental condition has a different notion of "valid output".
This module routes validation to the appropriate checker.
"""

from __future__ import annotations

import json
import sys
import os
from typing import Optional

# Add src/ to path for AXON imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))


# ── Condition definitions ────────────────────────────────────────────

CONDITIONS = [
    "free_english",
    "structured_english",
    "instruction_matched_english",
    "json_fc",
    "fipa_acl",
    "axon",
]


def validate_output(condition: str, output: str) -> dict:
    """
    Validate an LLM output for a given condition.

    Returns:
        {
            "valid": bool,
            "errors": list[str],
            "condition": str,
        }
    """
    validators = {
        "free_english": _validate_english,
        "structured_english": _validate_english,
        "instruction_matched_english": _validate_english,
        "json_fc": _validate_json_fc,
        "fipa_acl": _validate_fipa_acl,
        "axon": _validate_axon,
    }

    if condition not in validators:
        return {"valid": False, "errors": [f"Unknown condition: {condition}"], "condition": condition}

    return validators[condition](output)


def _validate_english(output: str) -> dict:
    """English conditions: pass-through (any non-empty output is valid)."""
    errors = []
    if not output.strip():
        errors.append("Empty output")
    return {"valid": len(errors) == 0, "errors": errors, "condition": "english"}


def _validate_json_fc(output: str) -> dict:
    """JSON function calling: must be valid JSON."""
    errors = []
    try:
        parsed = json.loads(output)
        if not isinstance(parsed, (dict, list)):
            errors.append("Top-level JSON must be object or array")
    except json.JSONDecodeError as e:
        errors.append(f"Invalid JSON: {e}")
    return {"valid": len(errors) == 0, "errors": errors, "condition": "json_fc"}


def _validate_fipa_acl(output: str) -> dict:
    """FIPA-ACL: basic structural check for performative presence."""
    errors = []
    output_stripped = output.strip()
    if not output_stripped:
        errors.append("Empty output")
    else:
        fipa_performatives = {
            "inform", "query-if", "query-ref", "request", "agree",
            "refuse", "propose", "accept-proposal", "reject-proposal",
            "cfp", "subscribe", "cancel", "not-understood", "failure",
        }
        lower = output_stripped.lower()
        has_perf = any(f"({p}" in lower or f"{p}\n" in lower for p in fipa_performatives)
        if not has_perf:
            errors.append("No recognized FIPA-ACL performative found")
    return {"valid": len(errors) == 0, "errors": errors, "condition": "fipa_acl"}


def _validate_axon(output: str) -> dict:
    """AXON: must parse successfully via the AXON parser."""
    errors = []
    try:
        from axon_parser import parse
        messages = parse(output)
        if len(messages) == 0:
            errors.append("No messages parsed")
    except Exception as e:
        errors.append(f"AXON parse error: {e}")
    return {"valid": len(errors) == 0, "errors": errors, "condition": "axon"}
