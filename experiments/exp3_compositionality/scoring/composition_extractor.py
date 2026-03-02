"""
Composition-structure extractor for AXON outputs.

Walks the AXON AST to detect composition operators (-> & | <-) and verify
that structural relationships between elements are correctly expressed.

Also provides text-based extraction for non-AXON structured formats and
a fallback for unparseable AXON outputs.
"""

from __future__ import annotations

import json
import os
import re
import sys
from typing import Optional

# Add src/ and experiments/ to path
PROJECT_ROOT = os.path.join(os.path.dirname(__file__), "..", "..", "..")
sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "experiments"))

# Reuse Exp 1 extractors for element scoring
from exp1_token_efficiency.scoring.extractors import (
    extract_axon as extract_axon_elements,
    extract_json_fc as extract_json_fc_elements,
    extract_fipa_acl as extract_fipa_acl_elements,
    _strip_fences,
    _present,
    _absent,
    _check_content_fact,
)


# ── AXON AST-based composition scoring ───────────────────────────────

def extract_axon_composition(output: str, cs_elements: list[dict],
                             task_id: str) -> dict[str, dict]:
    """Score composition-structure elements by walking the AXON AST.

    Args:
        output: Raw AXON output string
        cs_elements: List of composition_structure items from element_annotations
        task_id: Task identifier for context

    Returns:
        Dict of {element_id: {"verdict": "PRESENT"|"ABSENT", "evidence": str}}
    """
    cleaned = _strip_fences(output)
    results = {}

    try:
        from axon_parser import parse as axon_parse
        messages = axon_parse(cleaned)
    except Exception as e:
        for elem in cs_elements:
            results[elem["id"]] = _absent(f"AXON parse failed: {e}")
        return results

    if not messages:
        for elem in cs_elements:
            results[elem["id"]] = _absent("No messages parsed")
        return results

    # Collect all operator nodes from all message content trees
    all_ops = []
    max_depth = 0
    for msg in messages:
        if hasattr(msg, "content") and msg.content:
            ops = _collect_operators(msg.content)
            all_ops.extend(ops)
            depth = _measure_nesting_depth(msg.content)
            max_depth = max(max_depth, depth)

    # Also check raw text for operator presence as fallback
    text_lower = cleaned.lower()

    for elem in cs_elements:
        eid = elem["id"]
        cs_type = elem.get("type", "")

        if cs_type == "sequence":
            result = _check_sequence(all_ops, elem, text_lower, cleaned)
        elif cs_type == "parallel":
            result = _check_parallel(all_ops, elem, text_lower, cleaned)
        elif cs_type == "alternative":
            result = _check_alternative(all_ops, elem, text_lower, cleaned)
        elif cs_type == "causation":
            result = _check_causation(all_ops, elem, text_lower, cleaned)
        elif cs_type == "negation":
            result = _check_negation(all_ops, elem, text_lower, cleaned)
        elif cs_type == "nesting":
            result = _check_nesting(all_ops, max_depth, elem, text_lower, cleaned)
        else:
            result = _absent(f"Unknown composition type: {cs_type}")

        results[eid] = result

    return results


def _collect_operators(node, depth: int = 0) -> list[dict]:
    """Recursively collect all operator nodes from an AST tree.

    Returns list of dicts with:
        op: str — the operator
        left_text: str — string representation of left operand
        right_text: str — string representation of right operand
        depth: int — nesting depth
    """
    ops = []
    node_type = type(node).__name__

    if node_type == "BinaryExpr":
        op = node.op
        left_text = _node_to_text(node.left)
        right_text = _node_to_text(node.right)
        ops.append({
            "op": op,
            "left_text": left_text,
            "right_text": right_text,
            "depth": depth,
        })
        # Recurse into children
        ops.extend(_collect_operators(node.left, depth + 1))
        ops.extend(_collect_operators(node.right, depth + 1))

    elif node_type == "CallExpr":
        # Unary operators are CallExpr with func in {"~", "!", "neg"}
        if node.func in ("~", "!", "neg"):
            arg_text = _node_to_text(node.args[0]) if node.args else ""
            ops.append({
                "op": node.func,
                "left_text": arg_text,
                "right_text": "",
                "depth": depth,
            })
        # Recurse into args
        for arg in node.args:
            ops.extend(_collect_operators(arg, depth + 1))

    elif node_type == "ListExpr":
        for elem in node.elements:
            ops.extend(_collect_operators(elem, depth))

    elif node_type == "RecordExpr":
        for val in node.fields.values():
            ops.extend(_collect_operators(val, depth))

    elif node_type == "NamedArg":
        ops.extend(_collect_operators(node.value, depth))

    return ops


def _measure_nesting_depth(node, current_depth: int = 0) -> int:
    """Measure the maximum nesting depth of composition operators."""
    node_type = type(node).__name__
    max_depth = current_depth

    if node_type == "BinaryExpr" and node.op in ("->", "&", "|", "<-"):
        max_depth = max(max_depth, current_depth + 1)
        max_depth = max(max_depth, _measure_nesting_depth(node.left, current_depth + 1))
        max_depth = max(max_depth, _measure_nesting_depth(node.right, current_depth + 1))

    elif node_type == "CallExpr":
        if node.func in ("~", "!", "neg"):
            max_depth = max(max_depth, current_depth + 1)
        for arg in node.args:
            max_depth = max(max_depth, _measure_nesting_depth(arg, current_depth))

    elif node_type == "ListExpr":
        for elem in node.elements:
            max_depth = max(max_depth, _measure_nesting_depth(elem, current_depth))

    elif node_type == "RecordExpr":
        for val in node.fields.values():
            max_depth = max(max_depth, _measure_nesting_depth(val, current_depth))

    elif node_type == "NamedArg":
        max_depth = max(max_depth, _measure_nesting_depth(node.value, current_depth))

    return max_depth


def _node_to_text(node) -> str:
    """Convert an AST node to a searchable text representation."""
    node_type = type(node).__name__

    if node_type == "BinaryExpr":
        left = _node_to_text(node.left)
        right = _node_to_text(node.right)
        return f"({left} {node.op} {right})"

    elif node_type == "CallExpr":
        args = ", ".join(_node_to_text(a) for a in node.args)
        if node.func in ("~", "!", "neg"):
            return f"{node.func}({args})"
        return f"{node.func}({args})"

    elif node_type == "Reference":
        return f"@{node.name}"

    elif node_type == "Variable":
        return f"${node.name}"

    elif node_type == "Identifier":
        return node.name

    elif node_type == "Tag":
        body = _node_to_text(node.body) if node.body else ""
        return f"#{node.name}({body})" if body else f"#{node.name}"

    elif node_type == "StringLiteral":
        return node.value

    elif node_type == "NumberLiteral":
        unit = node.unit or ""
        return f"{node.value}{unit}"

    elif node_type == "BooleanLiteral":
        return str(node.value).lower()

    elif node_type == "NullLiteral":
        return "null"

    elif node_type == "ListExpr":
        items = ", ".join(_node_to_text(e) for e in node.elements)
        return f"[{items}]"

    elif node_type == "RecordExpr":
        pairs = ", ".join(f"{k}: {_node_to_text(v)}" for k, v in node.fields.items())
        return f"{{{pairs}}}"

    elif node_type == "NamedArg":
        return f"{node.name}: {_node_to_text(node.value)}"

    elif node_type == "PathExpr":
        return ".".join(node.parts)

    elif node_type == "RangeExpr":
        return f"{_node_to_text(node.start)}..{_node_to_text(node.end)}"

    elif node_type == "Message":
        content = _node_to_text(node.content) if node.content else ""
        return content

    return str(node)


def _check_sequence(ops: list[dict], elem: dict, text_lower: str,
                    text_raw: str) -> dict:
    """Check for sequence operator (->)."""
    arrow_ops = [o for o in ops if o["op"] == "->"]
    if arrow_ops:
        # Check if operand names appear in the operator's subtree text
        operands = elem.get("operands", [])
        for op in arrow_ops:
            combined = f"{op['left_text']} {op['right_text']}".lower()
            if _operands_match(operands, combined, text_lower):
                return _present(
                    f"Sequence (->): {op['left_text'][:40]} -> {op['right_text'][:40]}"
                )
        # Found -> operator but operands don't match specifically
        return _present(
            f"Sequence operator found ({len(arrow_ops)} instances): "
            f"{arrow_ops[0]['left_text'][:30]} -> {arrow_ops[0]['right_text'][:30]}"
        )
    return _absent("No sequence operator (->) found in AST")


def _check_parallel(ops: list[dict], elem: dict, text_lower: str,
                    text_raw: str) -> dict:
    """Check for parallel operator (&)."""
    amp_ops = [o for o in ops if o["op"] == "&"]
    if amp_ops:
        operands = elem.get("operands", [])
        for op in amp_ops:
            combined = f"{op['left_text']} {op['right_text']}".lower()
            if _operands_match(operands, combined, text_lower):
                return _present(
                    f"Parallel (&): {op['left_text'][:40]} & {op['right_text'][:40]}"
                )
        return _present(
            f"Parallel operator found ({len(amp_ops)} instances): "
            f"{amp_ops[0]['left_text'][:30]} & {amp_ops[0]['right_text'][:30]}"
        )
    return _absent("No parallel operator (&) found in AST")


def _check_alternative(ops: list[dict], elem: dict, text_lower: str,
                       text_raw: str) -> dict:
    """Check for alternative operator (|)."""
    pipe_ops = [o for o in ops if o["op"] == "|"]
    if pipe_ops:
        operands = elem.get("operands", [])
        for op in pipe_ops:
            combined = f"{op['left_text']} {op['right_text']}".lower()
            if _operands_match(operands, combined, text_lower):
                return _present(
                    f"Alternative (|): {op['left_text'][:40]} | {op['right_text'][:40]}"
                )
        return _present(
            f"Alternative operator found ({len(pipe_ops)} instances): "
            f"{pipe_ops[0]['left_text'][:30]} | {pipe_ops[0]['right_text'][:30]}"
        )
    return _absent("No alternative operator (|) found in AST")


def _check_causation(ops: list[dict], elem: dict, text_lower: str,
                     text_raw: str) -> dict:
    """Check for causation operator (<-)."""
    causal_ops = [o for o in ops if o["op"] == "<-"]
    if causal_ops:
        operands = elem.get("operands", [])
        for op in causal_ops:
            combined = f"{op['left_text']} {op['right_text']}".lower()
            if _operands_match(operands, combined, text_lower):
                return _present(
                    f"Causation (<-): {op['left_text'][:40]} <- {op['right_text'][:40]}"
                )
        return _present(
            f"Causation operator found ({len(causal_ops)} instances): "
            f"{causal_ops[0]['left_text'][:30]} <- {causal_ops[0]['right_text'][:30]}"
        )
    return _absent("No causation operator (<-) found in AST")


def _check_negation(ops: list[dict], elem: dict, text_lower: str,
                    text_raw: str) -> dict:
    """Check for negation operator (! or ~)."""
    neg_ops = [o for o in ops if o["op"] in ("!", "neg", "~")]
    if neg_ops:
        return _present(
            f"Negation ({neg_ops[0]['op']}): {neg_ops[0]['left_text'][:50]}"
        )
    # Also check for exclude/not patterns in text
    if re.search(r"!\s*\w|~\s*\w|not\(|exclude\(", text_lower):
        return _present("Negation pattern found in text")
    return _absent("No negation operator (! or ~) found in AST")


def _check_nesting(ops: list[dict], max_depth: int, elem: dict,
                   text_lower: str, text_raw: str) -> dict:
    """Check for operator nesting (operators inside other operators)."""
    # Count how many distinct composition operator types are present
    comp_ops = {o["op"] for o in ops if o["op"] in ("->", "&", "|", "<-")}

    if max_depth >= 2 and len(comp_ops) >= 2:
        return _present(
            f"Nesting depth {max_depth} with operators: {', '.join(sorted(comp_ops))}"
        )
    elif max_depth >= 2:
        return _present(f"Nesting depth {max_depth}")
    elif len(comp_ops) >= 2:
        # Multiple operator types but shallow nesting
        nested = any(o["depth"] > 0 for o in ops if o["op"] in ("->", "&", "|", "<-"))
        if nested:
            return _present(
                f"Nested operators: {', '.join(sorted(comp_ops))}"
            )
        return _absent(
            f"Multiple operators ({', '.join(sorted(comp_ops))}) but no nesting detected"
        )
    return _absent(f"Insufficient nesting: depth={max_depth}, operator types={len(comp_ops)}")


def _operands_match(operand_names: list[str], combined_text: str,
                    full_text: str) -> bool:
    """Check if expected operand names can be found in the operator text.

    Uses fuzzy matching: converts operand names like 'step_download' to
    search terms like 'download'.
    """
    if not operand_names:
        return True

    for name in operand_names:
        # Extract search terms from operand name
        terms = name.replace("step_", "").replace("option_", "").replace(
            "check_", "").replace("scan_", "").replace("extract_", "").replace(
            "cause_", "").replace("effect_", "").replace("root_cause_", "")
        terms = terms.replace("_", " ").split()

        # At least one term should appear in the text
        found = any(t in combined_text or t in full_text for t in terms)
        if not found:
            return False
    return True


# ── Text-based composition scoring for non-AXON formats ─────────────

# Keywords that signal composition relationships
SEQUENCE_SIGNALS = [
    r"\bthen\b", r"\bafter\b", r"\bbefore\b", r"\bnext\b", r"\bfirst\b",
    r"\bsecond\b", r"\bthird\b", r"\bfinally\b", r"\bfollowed by\b",
    r"\bstep\s*\d", r"\bsequence\b", r"\bpipeline\b", r"\bin order\b",
    r"->",
]

PARALLEL_SIGNALS = [
    r"\bsimultaneously\b", r"\bin parallel\b", r"\bconcurrently\b",
    r"\bat the same time\b", r"\btogether\b", r"\bboth\b.*\band\b",
    r"&",
]

ALTERNATIVE_SIGNALS = [
    r"\beither\b.*\bor\b", r"\balternatively\b", r"\bif\b.*\belse\b",
    r"\bfallback\b", r"\botherwise\b", r"\bdepending on\b",
    r"\|",
]

CAUSATION_SIGNALS = [
    r"\bcaused by\b", r"\bdue to\b", r"\bbecause\b", r"\bresulting from\b",
    r"\broot cause\b", r"\bled to\b", r"\btriggered by\b",
    r"<-",
]

NEGATION_SIGNALS = [
    r"\bexclude\b", r"\bexcept\b", r"\bnot\b", r"\bexcluding\b",
    r"\bwithout\b", r"\bbut not\b",
]


def extract_text_composition(output: str, cs_elements: list[dict],
                             task_id: str) -> dict[str, dict]:
    """Score composition-structure elements using text pattern matching.

    Used for non-AXON structured formats (JSON FC, FIPA-ACL) where we can
    search for structural keywords but don't have a composition-aware AST.
    Returns None for elements that need judge scoring.
    """
    cleaned = _strip_fences(output)
    text_lower = cleaned.lower()
    results = {}

    for elem in cs_elements:
        eid = elem["id"]
        cs_type = elem.get("type", "")

        if cs_type == "sequence":
            signals = SEQUENCE_SIGNALS
        elif cs_type == "parallel":
            signals = PARALLEL_SIGNALS
        elif cs_type == "alternative":
            signals = ALTERNATIVE_SIGNALS
        elif cs_type == "causation":
            signals = CAUSATION_SIGNALS
        elif cs_type == "negation":
            signals = NEGATION_SIGNALS
        elif cs_type == "nesting":
            # Nesting requires judge assessment for non-AXON formats
            results[eid] = None  # Signal: needs judge
            continue
        else:
            results[eid] = None
            continue

        # Search for signal patterns
        found_signals = []
        for pattern in signals:
            match = re.search(pattern, text_lower)
            if match:
                found_signals.append(match.group(0))

        if found_signals:
            results[eid] = _present(f"Text signals: {', '.join(found_signals[:3])}")
        else:
            results[eid] = None  # Needs judge — no text signals found

    return results


# ── Nesting depth measurement ────────────────────────────────────────

def measure_nesting_depth(output: str) -> int:
    """Measure the composition nesting depth of an AXON output.

    Returns 0 if the output cannot be parsed or has no composition operators.
    """
    cleaned = _strip_fences(output)
    try:
        from axon_parser import parse as axon_parse
        messages = axon_parse(cleaned)
    except Exception:
        return 0

    max_depth = 0
    for msg in messages:
        if hasattr(msg, "content") and msg.content:
            depth = _measure_nesting_depth(msg.content)
            max_depth = max(max_depth, depth)
    return max_depth
