"""
AXON Validator — 3-Level Conformance Checker
Separate from the parser. Validates AXON messages against the spec's
compliance tiers and semantic rules.

Usage:
    python3 src/axon_validator.py --tier 1 examples/basic.axon
    python3 src/axon_validator.py --tier 2 examples/basic.axon
    python3 src/axon_validator.py --tier 3 examples/basic.axon
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from axon_parser import (
    parse,
    LexerError,
    ParseError,
    Message,
    MetaBlock,
    NumberLiteral,
    StringLiteral,
    BooleanLiteral,
    NullLiteral,
    Reference,
    Tag,
    Variable,
    Identifier,
    ListExpr,
    RecordExpr,
    RangeExpr,
    CallExpr,
    NamedArg,
    BinaryExpr,
    PathExpr,
    ASTNode,
)


# ── Diagnostic types ─────────────────────────────────────────────────

class Severity(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class CheckKind(Enum):
    DETERMINISTIC = "deterministic"
    CONTEXT_REQUIRED = "context-required"
    SPEC_AMBIGUOUS = "spec-ambiguous"


@dataclass
class Diagnostic:
    severity: Severity
    message: str
    level: int  # validation level that produced this (1, 2, or 3)
    kind: CheckKind = CheckKind.DETERMINISTIC
    message_index: Optional[int] = None

    def __str__(self):
        prefix = f"L{self.level}"
        msg_ref = f" [msg {self.message_index}]" if self.message_index is not None else ""
        return f"[{prefix}:{self.severity.value}]{msg_ref} {self.message}"


@dataclass
class ValidationResult:
    valid: bool
    tier_checked: int
    diagnostics: list[Diagnostic] = field(default_factory=list)

    @property
    def errors(self) -> list[Diagnostic]:
        return [d for d in self.diagnostics if d.severity == Severity.ERROR]

    @property
    def warnings(self) -> list[Diagnostic]:
        return [d for d in self.diagnostics if d.severity == Severity.WARNING]

    def __str__(self):
        status = "PASS" if self.valid else "FAIL"
        lines = [f"Tier {self.tier_checked}: {status}"]
        for d in self.diagnostics:
            lines.append(f"  {d}")
        return "\n".join(lines)


# ── Tier field requirements ──────────────────────────────────────────

TIER_REQUIRED_FIELDS = {
    1: {"id", "%%"},
    2: {"id", "%%", "re", "ts", "ctx"},
    3: {"id", "%%", "re", "ts", "ctx", "sig", "authz", "tenant", "err_ns"},
}

# Valid type expectations for core metadata fields
META_TYPE_CHECKS = {
    "id": (StringLiteral, "string"),
    "%%": (NumberLiteral, "number"),
    "re": (StringLiteral, "string"),
    "ts": (NumberLiteral, "number"),
    "ctx": (StringLiteral, "string"),
    "ttl": (NumberLiteral, "number"),
    "sig": (StringLiteral, "string"),
    "authz": (StringLiteral, "string"),
    "tenant": (StringLiteral, "string"),
    "err_ns": (StringLiteral, "string"),
}

SUPPORTED_VERSIONS = {1}

# Performative transition rules
TRUTH_APT_RESPONSES = {"CFM", "DNY"}
PROPOSAL_RESPONSES = {"ACC", "REJ"}
TRUTH_APT_SOURCES = {"INF", "QRY", "RPL"}
PROPOSAL_SOURCES = {"PRO", "CTR"}

# Unit categories for cross-comparison checking
UNIT_CATEGORIES = {
    "time": {"ms", "s", "min", "h", "d"},
    "size": {"B", "KB", "MB", "GB"},
    "currency": {"usd", "eur"},
    "ratio": {"%"},
    "token": {"tok"},
}


def _unit_category(unit: str) -> Optional[str]:
    for cat, units in UNIT_CATEGORIES.items():
        if unit in units:
            return cat
    return None


# ── Validator ────────────────────────────────────────────────────────

class Validator:
    def __init__(self, source: str, tier: int = 1):
        if tier not in (1, 2, 3):
            raise ValueError(f"Tier must be 1, 2, or 3, got {tier}")
        self.source = source
        self.tier = tier
        self.diagnostics: list[Diagnostic] = []
        self.messages: list[Message] = []
        self.known_ids: set[str] = set()

    def validate(self) -> ValidationResult:
        # Level 1: syntactic
        if not self._check_level1():
            return ValidationResult(
                valid=False,
                tier_checked=self.tier,
                diagnostics=self.diagnostics,
            )

        # Level 2: tier compliance (gating)
        if self.tier >= 1:
            self._check_level2()

        # Level 3: semantic diagnostics (non-gating)
        self._check_level3()

        has_errors = any(d.severity == Severity.ERROR for d in self.diagnostics)
        return ValidationResult(
            valid=not has_errors,
            tier_checked=self.tier,
            diagnostics=self.diagnostics,
        )

    # ── Level 1: Syntactic ───────────────────────────────────────────

    def _check_level1(self) -> bool:
        try:
            self.messages = parse(self.source)
            return True
        except (LexerError, ParseError) as e:
            self.diagnostics.append(Diagnostic(
                severity=Severity.ERROR,
                message=f"Parse error: {e}",
                level=1,
            ))
            return False

    # ── Level 2: Tier compliance ─────────────────────────────────────

    def _check_level2(self):
        for i, msg in enumerate(self.messages):
            self._check_message_tier(msg, i)

    def _check_message_tier(self, msg: Message, idx: int):
        meta = msg.meta
        if meta is None:
            if self.tier >= 1:
                self.diagnostics.append(Diagnostic(
                    severity=Severity.ERROR,
                    message=f"Missing metadata block (Tier {self.tier} requires at least: {', '.join(sorted(TIER_REQUIRED_FIELDS[self.tier]))})",
                    level=2,
                    message_index=idx,
                ))
            return

        fields = meta.fields

        # Collect known IDs for response-link validation
        if "id" in fields and isinstance(fields["id"], StringLiteral):
            self.known_ids.add(fields["id"].value)

        # Required field presence
        required = TIER_REQUIRED_FIELDS.get(self.tier, set())
        for fld in sorted(required):
            if fld not in fields:
                self.diagnostics.append(Diagnostic(
                    severity=Severity.ERROR,
                    message=f"Missing required field '{fld}' for Tier {self.tier}",
                    level=2,
                    message_index=idx,
                ))

        # Field type validation
        for key, node in fields.items():
            if key in META_TYPE_CHECKS:
                expected_type, type_name = META_TYPE_CHECKS[key]
                if not isinstance(node, expected_type):
                    self.diagnostics.append(Diagnostic(
                        severity=Severity.ERROR,
                        message=f"Field '{key}' must be {type_name}, got {type(node).__name__}",
                        level=2,
                        message_index=idx,
                    ))

        # Priority range check
        if "^" in fields:
            node = fields["^"]
            if isinstance(node, NumberLiteral):
                if not (0 <= node.value <= 5) or node.value != int(node.value):
                    self.diagnostics.append(Diagnostic(
                        severity=Severity.ERROR,
                        message=f"Priority '^' must be integer 0-5, got {node.value}",
                        level=2,
                        message_index=idx,
                    ))
            else:
                self.diagnostics.append(Diagnostic(
                    severity=Severity.ERROR,
                    message=f"Priority '^' must be a number, got {type(node).__name__}",
                    level=2,
                    message_index=idx,
                ))

        # Protocol version check
        if "%%" in fields:
            node = fields["%%"]
            if isinstance(node, NumberLiteral):
                if int(node.value) not in SUPPORTED_VERSIONS:
                    self.diagnostics.append(Diagnostic(
                        severity=Severity.ERROR,
                        message=f"Unsupported protocol version: {int(node.value)} (supported: {sorted(SUPPORTED_VERSIONS)})",
                        level=2,
                        message_index=idx,
                    ))

    # ── Level 3: Semantic diagnostics (non-gating) ───────────────────

    def _check_level3(self):
        # Collect all known IDs first (for re-link validation)
        for msg in self.messages:
            if msg.meta and "id" in msg.meta.fields:
                node = msg.meta.fields["id"]
                if isinstance(node, StringLiteral):
                    self.known_ids.add(node.value)

        for i, msg in enumerate(self.messages):
            self._check_performative_transitions(msg, i)
            self._check_unit_compatibility(msg.content, i)
            self._check_response_links(msg, i)

    def _check_performative_transitions(self, msg: Message, idx: int):
        perf = msg.performative
        if msg.meta is None or "re" not in msg.meta.fields:
            return  # can't check transitions without reply-to context

        if perf in TRUTH_APT_RESPONSES:
            self.diagnostics.append(Diagnostic(
                severity=Severity.INFO,
                message=f"{perf} should respond to truth-apt performatives (INF, QRY, RPL)",
                level=3,
                kind=CheckKind.DETERMINISTIC,
                message_index=idx,
            ))

        if perf in PROPOSAL_RESPONSES:
            self.diagnostics.append(Diagnostic(
                severity=Severity.INFO,
                message=f"{perf} should respond to proposals (PRO, CTR)",
                level=3,
                kind=CheckKind.DETERMINISTIC,
                message_index=idx,
            ))

    def _check_unit_compatibility(self, node: ASTNode, idx: int):
        if isinstance(node, BinaryExpr):
            if node.op in ("<", ">", "<=", ">=", "!=", "="):
                left_unit = self._extract_unit(node.left)
                right_unit = self._extract_unit(node.right)
                if left_unit and right_unit:
                    left_cat = _unit_category(left_unit)
                    right_cat = _unit_category(right_unit)
                    if left_cat and right_cat and left_cat != right_cat:
                        self.diagnostics.append(Diagnostic(
                            severity=Severity.WARNING,
                            message=f"Comparing incompatible units: {left_unit} ({left_cat}) vs {right_unit} ({right_cat})",
                            level=3,
                            kind=CheckKind.DETERMINISTIC,
                            message_index=idx,
                        ))
            self._check_unit_compatibility(node.left, idx)
            self._check_unit_compatibility(node.right, idx)
        elif isinstance(node, CallExpr):
            for arg in node.args:
                self._check_unit_compatibility(arg, idx)
        elif isinstance(node, RecordExpr):
            for val in node.fields.values():
                self._check_unit_compatibility(val, idx)
        elif isinstance(node, ListExpr):
            for el in node.elements:
                self._check_unit_compatibility(el, idx)
        elif isinstance(node, RangeExpr):
            self._check_unit_compatibility(node.start, idx)
            self._check_unit_compatibility(node.end, idx)
        elif isinstance(node, NamedArg):
            self._check_unit_compatibility(node.value, idx)
        elif isinstance(node, Tag) and node.body:
            self._check_unit_compatibility(node.body, idx)
        elif isinstance(node, Message):
            self._check_unit_compatibility(node.content, idx)

    def _extract_unit(self, node: ASTNode) -> Optional[str]:
        if isinstance(node, NumberLiteral) and node.unit:
            return node.unit
        return None

    def _check_response_links(self, msg: Message, idx: int):
        if msg.meta is None or "re" not in msg.meta.fields:
            return
        re_node = msg.meta.fields["re"]
        if not isinstance(re_node, StringLiteral):
            return
        re_id = re_node.value
        if re_id not in self.known_ids:
            self.diagnostics.append(Diagnostic(
                severity=Severity.WARNING,
                message=f"Reply-to id '{re_id}' not found in this document's messages",
                level=3,
                kind=CheckKind.CONTEXT_REQUIRED,
                message_index=idx,
            ))


# ── Public API ───────────────────────────────────────────────────────

def validate(source: str, tier: int = 1) -> ValidationResult:
    v = Validator(source, tier)
    return v.validate()


# ── CLI ──────────────────────────────────────────────────────────────

def main():
    import sys

    if len(sys.argv) < 2:
        print("AXON Validator v0.1")
        print("Usage: python3 axon_validator.py [--tier N] <file.axon>")
        print("       python3 axon_validator.py --tier 2 examples/basic.axon")
        print()
        print("Tiers: 1=Core Valid, 2=Interop Compliant, 3=Production Certified")
        sys.exit(0)

    tier = 1
    args = sys.argv[1:]

    if "--tier" in args:
        idx = args.index("--tier")
        tier = int(args[idx + 1])
        args = args[:idx] + args[idx + 2:]

    if not args:
        print("Error: No input file specified")
        sys.exit(1)

    filename = args[0]
    if filename == "-":
        source = sys.stdin.read()
    else:
        with open(filename) as f:
            source = f.read()

    result = validate(source, tier)
    print(result)
    sys.exit(0 if result.valid else 1)


if __name__ == "__main__":
    main()
