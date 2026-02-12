"""
Conformance test suite for the AXON parser.

Tests valid corpus files parse successfully and invalid inputs
produce appropriate errors. This is the Week 0 exit gate.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from axon_parser import parse, LexerError, ParseError

CONFORMANCE_DIR = os.path.dirname(__file__)


# ── Valid corpus: every .axon file in this directory must parse ────────

VALID_FILES = [
    "valid_tier1.axon",
    "valid_tier2.axon",
    "valid_tier3.axon",
    "valid_performatives.axon",
    "valid_operators.axon",
]


@pytest.mark.parametrize("filename", VALID_FILES)
def test_valid_corpus(filename):
    path = os.path.join(CONFORMANCE_DIR, filename)
    with open(path) as f:
        source = f.read()
    messages = parse(source)
    assert len(messages) > 0, f"{filename} should produce at least one message"


# ── Invalid inputs: must raise LexerError or ParseError ──────────────

class TestInvalidDigitFirstIdentifier:
    def test_digit_first_tag(self):
        with pytest.raises(LexerError, match="Identifier must start with a letter"):
            parse('INF(@a>@b): #123tag')

    def test_digit_first_ref(self):
        with pytest.raises(LexerError, match="Identifier must start with a letter"):
            parse('INF(@a>@b): @123agent')

    def test_digit_first_var(self):
        with pytest.raises(LexerError, match="Identifier must start with a letter"):
            parse('INF(@a>@b): $123var')


class TestUnclosedComment:
    def test_unclosed_simple(self):
        with pytest.raises(LexerError, match="Unterminated comment"):
            parse('(* this is never closed')

    def test_unclosed_nested(self):
        with pytest.raises(LexerError, match="Unterminated comment"):
            parse('(* outer (* inner *) still open')

    def test_closed_comment_is_fine(self):
        msgs = parse('(* closed *) INF(@a>@b): x')
        assert len(msgs) == 1


class TestDuplicateMetadataKeys:
    def test_duplicate_id(self):
        with pytest.raises(ParseError, match="Duplicate metadata key 'id'"):
            parse('[id:"m1", id:"m2"] INF(@a>@b): x')

    def test_duplicate_percent(self):
        with pytest.raises(ParseError, match="Duplicate metadata key"):
            parse('[%%:1, %%:2] INF(@a>@b): x')

    def test_duplicate_caret(self):
        with pytest.raises(ParseError, match="Duplicate metadata key"):
            parse('[^:1, ^:2] INF(@a>@b): x')

    def test_unique_keys_ok(self):
        msgs = parse('[id:"m1", %%:1, ^:3] INF(@a>@b): x')
        assert len(msgs) == 1


class TestMissingRequiredStructure:
    def test_missing_routing(self):
        with pytest.raises(ParseError):
            parse('INF: x')

    def test_missing_content(self):
        with pytest.raises(ParseError):
            parse('INF(@a>@b):')

    def test_missing_performative(self):
        with pytest.raises(ParseError):
            parse('(@a>@b): x')

    def test_empty_input(self):
        msgs = parse('')
        assert len(msgs) == 0

    def test_only_whitespace(self):
        msgs = parse('   \n\n  ')
        assert len(msgs) == 0


class TestMiscInvalid:
    def test_unterminated_string(self):
        with pytest.raises(LexerError, match="Unterminated string"):
            parse('INF(@a>@b): "never closed')

    def test_unexpected_character(self):
        with pytest.raises(LexerError, match="Unexpected character"):
            parse('INF(@a>@b): `backtick')


# ── Regression: existing examples must still parse ───────────────────

EXAMPLE_DIR = os.path.join(CONFORMANCE_DIR, "..", "..", "examples")

EXAMPLE_FILES = ["basic.axon", "advanced.axon", "real_world_scenarios.axon"]


@pytest.mark.parametrize("filename", EXAMPLE_FILES)
def test_example_files(filename):
    path = os.path.join(EXAMPLE_DIR, filename)
    with open(path) as f:
        source = f.read()
    messages = parse(source)
    assert len(messages) > 0
