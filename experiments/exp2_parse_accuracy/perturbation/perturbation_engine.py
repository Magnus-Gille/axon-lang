"""
Perturbation engine for Exp 2: Parse Accuracy Under Noise.

Applies deterministic perturbations to agent communication messages.
All perturbations are seeded for reproducibility.

Usage:
    from perturbation_engine import apply_perturbation, PERTURBATION_TYPES

    perturbed = apply_perturbation(text, "char_deletion", seed=12345)
"""

from __future__ import annotations

import hashlib
import random
import sys
import os
from pathlib import Path

# Add experiments/ to path for lib imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "experiments"))

PERTURBATION_TYPES = ["char_deletion", "token_swap", "truncation"]


def compute_seed(task_id: str, condition: str, model: str,
                 run_number: int, perturbation_type: str) -> int:
    """Deterministic seed from cell identity."""
    key = f"{task_id}_{condition}_{model}_{run_number}_{perturbation_type}"
    return int(hashlib.sha256(key.encode()).hexdigest()[:8], 16)


def apply_perturbation(text: str, perturbation_type: str, seed: int) -> str:
    """Apply a single perturbation to text.

    Args:
        text: Original message text
        perturbation_type: One of PERTURBATION_TYPES
        seed: Random seed for reproducibility

    Returns:
        Perturbed text
    """
    if perturbation_type == "char_deletion":
        return apply_character_deletion(text, rate=0.05, seed=seed)
    elif perturbation_type == "token_swap":
        return apply_token_swap(text, seed=seed)
    elif perturbation_type == "truncation":
        return apply_truncation(text, ratio=0.75, seed=seed)
    else:
        raise ValueError(f"Unknown perturbation type: {perturbation_type}")


def apply_character_deletion(text: str, rate: float = 0.05, seed: int = 0) -> str:
    """Remove characters at random positions.

    Args:
        text: Input text
        rate: Fraction of characters to remove (default 5%)
        seed: Random seed

    Returns:
        Text with characters removed
    """
    if not text:
        return text

    rng = random.Random(seed)
    chars = list(text)
    n_delete = max(1, int(len(chars) * rate))

    # Select positions to delete
    if n_delete >= len(chars):
        return ""
    positions = sorted(rng.sample(range(len(chars)), n_delete), reverse=True)
    for pos in positions:
        chars.pop(pos)

    return "".join(chars)


def apply_token_swap(text: str, seed: int = 0) -> str:
    """Swap two adjacent tokens.

    Uses tiktoken cl100k_base tokenization. Selects a random position
    and swaps tokens at position i and i+1.

    Args:
        text: Input text
        seed: Random seed

    Returns:
        Text with one adjacent token pair swapped
    """
    try:
        from lib.token_counter import _get_encoding
        enc = _get_encoding("cl100k_base")
    except ImportError:
        # Fallback: word-level swap
        return _word_swap_fallback(text, seed)

    tokens = enc.encode(text)
    if len(tokens) < 2:
        return text

    rng = random.Random(seed)
    pos = rng.randint(0, len(tokens) - 2)
    tokens[pos], tokens[pos + 1] = tokens[pos + 1], tokens[pos]

    return enc.decode(tokens)


def _word_swap_fallback(text: str, seed: int) -> str:
    """Fallback word-level swap when tiktoken is unavailable."""
    words = text.split()
    if len(words) < 2:
        return text
    rng = random.Random(seed)
    pos = rng.randint(0, len(words) - 2)
    words[pos], words[pos + 1] = words[pos + 1], words[pos]
    return " ".join(words)


def apply_truncation(text: str, ratio: float = 0.75, seed: int = 0) -> str:
    """Keep the first `ratio` fraction of characters.

    Args:
        text: Input text
        ratio: Fraction to keep (default 75%)
        seed: Random seed (unused for truncation, included for API consistency)

    Returns:
        Truncated text
    """
    if not text:
        return text
    keep = max(1, int(len(text) * ratio))
    return text[:keep]


# ── Self-test ─────────────────────────────────────────────────────────

def _self_test():
    """Verify determinism and basic behavior."""
    test_text = 'REQ(@a > @b): download("data") -> clean() -> upload("warehouse")'

    print("Perturbation Engine — Self-Test")
    print("=" * 60)
    print(f"Original ({len(test_text)} chars): {test_text}")

    for ptype in PERTURBATION_TYPES:
        seed = compute_seed("L1-01", "axon", "codex", 1, ptype)
        result1 = apply_perturbation(test_text, ptype, seed)
        result2 = apply_perturbation(test_text, ptype, seed)

        assert result1 == result2, f"Non-deterministic: {ptype}"
        assert result1 != test_text or ptype == "truncation" and len(test_text) * 0.75 >= len(test_text), \
            f"No change applied: {ptype}"

        print(f"\n{ptype} (seed={seed}):")
        print(f"  Result ({len(result1)} chars): {result1}")
        print(f"  Deterministic: PASS")

    # Test with different seeds produce different results
    seed_a = compute_seed("L1-01", "axon", "codex", 1, "char_deletion")
    seed_b = compute_seed("L1-01", "axon", "codex", 2, "char_deletion")
    result_a = apply_perturbation(test_text, "char_deletion", seed_a)
    result_b = apply_perturbation(test_text, "char_deletion", seed_b)
    assert result_a != result_b, "Different seeds should produce different results"
    print(f"\nDifferent seeds → different results: PASS")

    print("\nAll tests passed.")


if __name__ == "__main__":
    _self_test()
