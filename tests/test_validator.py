"""
Tests for the AXON validator.
Covers all 3 validation levels across tiers 1-3.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from axon_validator import validate, Severity, CheckKind


# ── Level 1: Syntactic ───────────────────────────────────────────────

class TestLevel1Syntactic:
    def test_valid_message_with_metadata(self):
        result = validate('[id:"m1", %%:1] INF(@a>@b): "hello"')
        assert result.valid

    def test_valid_syntax_no_metadata_fails_tier1(self):
        """Syntactically valid but fails tier 1 compliance (missing metadata)."""
        result = validate('INF(@a>@b): "hello"')
        assert not result.valid
        assert any("Missing metadata block" in d.message for d in result.errors)

    def test_invalid_syntax(self):
        result = validate('NOT_A_PERF(@a>@b): x')
        assert not result.valid
        assert any("Parse error" in d.message for d in result.errors)

    def test_empty_input(self):
        result = validate('')
        assert result.valid


# ── Level 2: Tier 1 compliance ───────────────────────────────────────

class TestTier1Compliance:
    def test_valid_tier1(self):
        result = validate('[id:"m1", %%:1] INF(@a>@b): "data"', tier=1)
        assert result.valid

    def test_missing_metadata_tier1(self):
        result = validate('INF(@a>@b): "data"', tier=1)
        assert not result.valid
        assert any("Missing metadata block" in d.message for d in result.errors)

    def test_missing_id_tier1(self):
        result = validate('[%%:1] INF(@a>@b): "data"', tier=1)
        assert not result.valid
        assert any("Missing required field 'id'" in d.message for d in result.errors)

    def test_missing_percent_tier1(self):
        result = validate('[id:"m1"] INF(@a>@b): "data"', tier=1)
        assert not result.valid
        assert any("Missing required field '%%'" in d.message for d in result.errors)

    def test_wrong_type_id(self):
        result = validate('[id:42, %%:1] INF(@a>@b): "data"', tier=1)
        assert not result.valid
        assert any("'id' must be string" in d.message for d in result.errors)

    def test_wrong_type_percent(self):
        result = validate('[id:"m1", %%:"one"] INF(@a>@b): "data"', tier=1)
        assert not result.valid
        assert any("'%%' must be number" in d.message for d in result.errors)

    def test_unsupported_version(self):
        result = validate('[id:"m1", %%:99] INF(@a>@b): "data"', tier=1)
        assert not result.valid
        assert any("Unsupported protocol version" in d.message for d in result.errors)


# ── Level 2: Tier 2 compliance ───────────────────────────────────────

class TestTier2Compliance:
    def test_valid_tier2(self):
        result = validate(
            '[id:"m1", %%:1, re:"m0", ts:1707600000, ctx:"conv-1"] INF(@a>@b): "data"',
            tier=2,
        )
        assert result.valid

    def test_missing_re_tier2(self):
        result = validate(
            '[id:"m1", %%:1, ts:1707600000, ctx:"conv-1"] INF(@a>@b): "data"',
            tier=2,
        )
        assert not result.valid
        assert any("Missing required field 're'" in d.message for d in result.errors)

    def test_missing_ts_tier2(self):
        result = validate(
            '[id:"m1", %%:1, re:"m0", ctx:"conv-1"] INF(@a>@b): "data"',
            tier=2,
        )
        assert not result.valid
        assert any("Missing required field 'ts'" in d.message for d in result.errors)

    def test_missing_ctx_tier2(self):
        result = validate(
            '[id:"m1", %%:1, re:"m0", ts:1707600000] INF(@a>@b): "data"',
            tier=2,
        )
        assert not result.valid
        assert any("Missing required field 'ctx'" in d.message for d in result.errors)


# ── Level 2: Tier 3 compliance ───────────────────────────────────────

class TestTier3Compliance:
    TIER3_FULL = (
        '[id:"m1", %%:1, re:"m0", ts:1707600000, ctx:"c1", '
        'sig:"ed25519:abc", authz:"role:admin", tenant:"acme", err_ns:"acme.x"] '
        'INF(@a>@b): "data"'
    )

    def test_valid_tier3(self):
        result = validate(self.TIER3_FULL, tier=3)
        assert result.valid

    def test_missing_sig_tier3(self):
        src = (
            '[id:"m1", %%:1, re:"m0", ts:1707600000, ctx:"c1", '
            'authz:"role:admin", tenant:"acme", err_ns:"acme.x"] '
            'INF(@a>@b): "data"'
        )
        result = validate(src, tier=3)
        assert not result.valid
        assert any("Missing required field 'sig'" in d.message for d in result.errors)

    def test_missing_tenant_tier3(self):
        src = (
            '[id:"m1", %%:1, re:"m0", ts:1707600000, ctx:"c1", '
            'sig:"ed25519:abc", authz:"role:admin", err_ns:"acme.x"] '
            'INF(@a>@b): "data"'
        )
        result = validate(src, tier=3)
        assert not result.valid
        assert any("Missing required field 'tenant'" in d.message for d in result.errors)


# ── Level 2: Priority range ─────────────────────────────────────────

class TestPriorityRange:
    def test_valid_priority(self):
        result = validate('[id:"m1", %%:1, ^:3] INF(@a>@b): "data"', tier=1)
        assert result.valid

    def test_priority_too_high(self):
        result = validate('[id:"m1", %%:1, ^:6] INF(@a>@b): "data"', tier=1)
        assert not result.valid
        assert any("Priority" in d.message for d in result.errors)

    def test_priority_zero(self):
        result = validate('[id:"m1", %%:1, ^:0] INF(@a>@b): "data"', tier=1)
        assert result.valid

    def test_priority_five(self):
        result = validate('[id:"m1", %%:1, ^:5] INF(@a>@b): "data"', tier=1)
        assert result.valid


# ── Level 3: Semantic diagnostics ────────────────────────────────────

class TestLevel3Semantics:
    def test_unit_category_mismatch(self):
        result = validate('[id:"m1", %%:1] INF(@a>@b): 10ms > 5usd', tier=1)
        warnings = [d for d in result.warnings if "incompatible units" in d.message]
        assert len(warnings) == 1
        assert "time" in warnings[0].message
        assert "currency" in warnings[0].message

    def test_same_unit_category_ok(self):
        result = validate('[id:"m1", %%:1] INF(@a>@b): 10ms > 5s', tier=1)
        warnings = [d for d in result.warnings if "incompatible units" in d.message]
        assert len(warnings) == 0

    def test_response_link_unknown_id(self):
        result = validate(
            '[id:"m1", %%:1, re:"nonexistent", ts:1707600000, ctx:"c1"] RPL(@b>@a): "data"',
            tier=2,
        )
        warnings = [d for d in result.warnings if "not found" in d.message]
        assert len(warnings) == 1

    def test_response_link_known_id(self):
        src = (
            '[id:"m1", %%:1] QRY(@a>@b): status(@x)\n'
            '[id:"m2", %%:1, re:"m1", ts:1707600000, ctx:"c1"] RPL(@b>@a): "ok"'
        )
        result = validate(src, tier=2)
        warnings = [d for d in result.warnings if "not found" in d.message]
        assert len(warnings) == 0


# ── Multi-message documents ──────────────────────────────────────────

class TestMultiMessage:
    def test_mixed_valid_invalid(self):
        src = (
            '[id:"m1", %%:1] INF(@a>@b): "ok"\n'
            'QRY(@a>@b): status(@x)\n'  # missing metadata
        )
        result = validate(src, tier=1)
        assert not result.valid

    def test_all_valid(self):
        src = (
            '[id:"m1", %%:1] INF(@a>@b): "ok"\n'
            '[id:"m2", %%:1] QRY(@a>@b): status(@x)\n'
        )
        result = validate(src, tier=1)
        assert result.valid


# ── Example files through validator ──────────────────────────────────

class TestExampleFiles:
    EXAMPLE_DIR = os.path.join(os.path.dirname(__file__), "..", "examples")

    def _read(self, filename):
        with open(os.path.join(self.EXAMPLE_DIR, filename)) as f:
            return f.read()

    def test_basic_tier1_syntax(self):
        """Basic examples should at least parse (Level 1)."""
        source = self._read("basic.axon")
        result = validate(source, tier=1)
        # Some messages lack metadata, so tier compliance may fail,
        # but syntax should be fine
        assert not any(d.level == 1 for d in result.errors)
