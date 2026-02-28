#!/usr/bin/env python3
"""
Benchmark B: Parsing & Validation Rigor

Feeds 20 malformed inputs to both AXON's parser and AISP's validator,
measuring detection rate, error specificity, and error location precision.

Usage:
    python3 experiments/exp_aisp_comparison/benchmark_b_runner.py
    python3 experiments/exp_aisp_comparison/benchmark_b_runner.py --verbose
"""

from __future__ import annotations

import json
import sys
import os
from pathlib import Path

# Add project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "experiments" / "lib"))

from condition_adapter import validate_output


def load_test_cases() -> list[dict]:
    """Load the 20 malformed test cases."""
    tc_path = Path(__file__).parent / "benchmark_b_test_cases.json"
    with open(tc_path) as f:
        data = json.load(f)
    return data["test_cases"]


def score_error_specificity(result: dict) -> int:
    """Score error specificity: 0=no error, 1=generic, 2=specific with detail."""
    if result["valid"]:
        return 0  # No error reported (accepted)
    errors = result.get("errors", [])
    if not errors:
        return 0
    error_text = " ".join(errors).lower()
    # Specific errors mention what's wrong (type, key, delimiter, etc.)
    specific_markers = [
        "parse error", "unclosed", "unexpected", "invalid", "missing",
        "duplicate", "unknown", "expected", "not a valid", "type", "bracket",
        "string", "number", "reference", "performative", "empty",
    ]
    if any(m in error_text for m in specific_markers):
        return 2
    return 1


def score_error_location(result: dict) -> int:
    """Score error location: 0=none, 1=approximate, 2=precise (line+col)."""
    if result["valid"]:
        return 0
    errors = result.get("errors", [])
    error_text = " ".join(errors)
    # Look for line/column indicators
    if "line" in error_text.lower() and "col" in error_text.lower():
        return 2
    if "line" in error_text.lower() or "position" in error_text.lower():
        return 1
    # AXON parser often includes position in error messages
    if "at " in error_text and any(c.isdigit() for c in error_text):
        return 1
    return 0


def run_benchmark(verbose: bool = False) -> dict:
    """Run Benchmark B and return results."""
    test_cases = load_test_cases()
    results = {
        "axon": {"detected": 0, "total": 0, "specificity_sum": 0, "location_sum": 0, "details": []},
        "aisp": {"detected": 0, "total": 0, "specificity_sum": 0, "location_sum": 0, "details": []},
    }

    print("=" * 80)
    print("BENCHMARK B: Parsing & Validation Rigor")
    print("=" * 80)
    print(f"\n  Testing {len(test_cases)} malformed inputs against AXON parser and AISP validator\n")

    for tc in test_cases:
        tc_id = tc["id"]
        category = tc["category"]
        desc = tc["description"]

        if verbose:
            print(f"\n--- {tc_id}: {desc} ({category}) ---")

        # Test AXON
        axon_input = tc["axon_input"]
        axon_result = validate_output("axon", axon_input)
        axon_rejected = not axon_result["valid"]
        axon_spec = score_error_specificity(axon_result)
        axon_loc = score_error_location(axon_result)

        results["axon"]["total"] += 1
        if axon_rejected:
            results["axon"]["detected"] += 1
        results["axon"]["specificity_sum"] += axon_spec
        results["axon"]["location_sum"] += axon_loc
        results["axon"]["details"].append({
            "id": tc_id, "category": category, "description": desc,
            "rejected": axon_rejected, "errors": axon_result.get("errors", []),
            "specificity": axon_spec, "location": axon_loc,
            "expected": tc["expected_axon"],
        })

        # Test AISP
        aisp_input = tc["aisp_input"]
        aisp_result = validate_output("aisp", aisp_input)
        aisp_rejected = not aisp_result["valid"]
        aisp_spec = score_error_specificity(aisp_result)
        aisp_loc = score_error_location(aisp_result)

        results["aisp"]["total"] += 1
        if aisp_rejected:
            results["aisp"]["detected"] += 1
        results["aisp"]["specificity_sum"] += aisp_spec
        results["aisp"]["location_sum"] += aisp_loc
        results["aisp"]["details"].append({
            "id": tc_id, "category": category, "description": desc,
            "rejected": aisp_rejected, "errors": aisp_result.get("errors", []),
            "specificity": aisp_spec, "location": aisp_loc,
            "expected": tc["expected_aisp"],
        })

        if verbose:
            axon_status = "REJECT" if axon_rejected else "ACCEPT"
            aisp_status = "REJECT" if aisp_rejected else "ACCEPT"
            print(f"  AXON: {axon_status} (spec={axon_spec}, loc={axon_loc}) "
                  f"{''.join(axon_result.get('errors', [])[:1])}")
            print(f"  AISP: {aisp_status} (spec={aisp_spec}, loc={aisp_loc}) "
                  f"{''.join(aisp_result.get('errors', [])[:1])}")

    # Summary
    print("\n" + "=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)

    for tool in ["axon", "aisp"]:
        r = results[tool]
        n = r["total"]
        det = r["detected"]
        det_rate = det / n if n > 0 else 0
        mean_spec = r["specificity_sum"] / n if n > 0 else 0
        mean_loc = r["location_sum"] / n if n > 0 else 0
        accepted = n - det

        print(f"\n  {tool.upper()}:")
        print(f"    Detection rate:       {det}/{n} ({det_rate:.0%})")
        print(f"    Accepted (should reject): {accepted}/{n}")
        print(f"    Mean error specificity:   {mean_spec:.2f}/2.00")
        print(f"    Mean error location:      {mean_loc:.2f}/2.00")

    # By category
    print("\n  Detection by category:")
    print(f"  {'Category':<25} {'AXON':>10} {'AISP':>10}")
    print("  " + "-" * 47)
    categories = ["missing_structure", "type_mismatch", "syntax_error", "semantic_violation", "edge_case"]
    for cat in categories:
        axon_cat = [d for d in results["axon"]["details"] if d["category"] == cat]
        aisp_cat = [d for d in results["aisp"]["details"] if d["category"] == cat]
        axon_det = sum(1 for d in axon_cat if d["rejected"])
        aisp_det = sum(1 for d in aisp_cat if d["rejected"])
        axon_total = len(axon_cat)
        aisp_total = len(aisp_cat)
        print(f"  {cat:<25} {axon_det}/{axon_total:>6} {aisp_det}/{aisp_total:>6}")

    # Prediction verification
    print("\n  Prediction verification:")
    axon_rate = results["axon"]["detected"] / results["axon"]["total"]
    aisp_accept_rate = 1 - (results["aisp"]["detected"] / results["aisp"]["total"])
    axon_mean_spec = results["axon"]["specificity_sum"] / results["axon"]["total"]
    aisp_mean_spec = results["aisp"]["specificity_sum"] / results["aisp"]["total"]

    predictions = [
        (f"AXON rejects ≥90%", axon_rate >= 0.90, f"{axon_rate:.0%}"),
        (f"AISP accepts ≥80%", aisp_accept_rate >= 0.80, f"{aisp_accept_rate:.0%} accepted"),
        (f"AXON specificity ≥1.5", axon_mean_spec >= 1.5, f"{axon_mean_spec:.2f}"),
        (f"AISP specificity ≤0.5", aisp_mean_spec <= 0.5, f"{aisp_mean_spec:.2f}"),
    ]
    for desc, passed, value in predictions:
        status = "PASS" if passed else "FAIL"
        print(f"    [{status}] {desc}: {value}")

    return results


def save_results(results: dict):
    """Save detailed results to JSON."""
    out_path = Path(__file__).parent / "benchmark_b_results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n  Results saved to {out_path}")


def main():
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    results = run_benchmark(verbose=verbose)
    save_results(results)


if __name__ == "__main__":
    main()
