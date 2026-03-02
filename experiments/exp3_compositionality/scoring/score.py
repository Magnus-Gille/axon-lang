"""
Exp 3: Compositionality — Hybrid Scorer

Scores both standard elements (reusing Exp 1 extractors) and
composition-structure elements (new for Exp 3).

Usage:
    # Score a single results file
    python3 experiments/exp3_compositionality/scoring/score.py results/exp3_codex_*.json

    # Score with judge panel for English conditions
    python3 experiments/exp3_compositionality/scoring/score.py results/exp3_codex_*.json --judge

    # Test extractor on a known-good AXON output
    python3 experiments/exp3_compositionality/scoring/score.py --test

    # Cross-validate AXON machine scores against judge panel
    python3 experiments/exp3_compositionality/scoring/score.py --cross-validate results/exp3_*.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from datetime import datetime, timezone

# Add paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "experiments"))

from exp1_token_efficiency.scoring.extractors import (
    extract_axon as extract_axon_elements,
    extract_json_fc as extract_json_fc_elements,
    extract_fipa_acl as extract_fipa_acl_elements,
    MACHINE_SCORED_CONDITIONS,
    JUDGE_SCORED_CONDITIONS,
)

from exp3_compositionality.scoring.composition_extractor import (
    extract_axon_composition,
    extract_text_composition,
    measure_nesting_depth,
)


TASKS_FILE = Path(__file__).parent.parent / "tasks" / "element_annotations.json"
RESULTS_DIR = Path(__file__).parent.parent / "results"

# Conditions where composition-structure is machine-scored
COMPOSITION_MACHINE_CONDITIONS = {"axon"}
# Conditions where composition-structure needs judge scoring
COMPOSITION_JUDGE_CONDITIONS = {
    "free_english", "structured_english", "instruction_matched_english",
    "json_fc", "fipa_acl", "aisp",
}


def load_annotations() -> dict:
    """Load element annotations including composition-structure definitions."""
    with open(TASKS_FILE) as f:
        return json.load(f)


def get_task_annotations(annotations: dict, task_id: str) -> dict | None:
    """Get annotations for a specific task."""
    for task in annotations["tasks"]:
        if task["id"] == task_id:
            return task
    return None


def score_output(condition: str, output: str, task_id: str,
                 annotations: dict) -> dict:
    """Score a single output for both elements and composition-structure.

    Returns:
        {
            "elements": {element_id: {"verdict": str, "evidence": str}},
            "composition_structure": {cs_id: {"verdict": str, "evidence": str}},
            "nesting_depth": int,
            "element_rate": float,
            "composition_rate": float,
            "needs_judge": list[str],  # element IDs that need judge scoring
        }
    """
    task_ann = get_task_annotations(annotations, task_id)
    if not task_ann:
        return {
            "elements": {},
            "composition_structure": {},
            "nesting_depth": 0,
            "element_rate": 0.0,
            "composition_rate": 0.0,
            "needs_judge": [],
            "error": f"No annotations for task {task_id}",
        }

    elements = task_ann["elements"]["items"]
    cs_elements = task_ann["composition_structure"]["items"]
    needs_judge = []

    # ── Score standard elements ──────────────────────────────────────
    if condition in MACHINE_SCORED_CONDITIONS:
        if condition == "axon":
            elem_results = extract_axon_elements(output, elements, task_id)
        elif condition == "json_fc":
            elem_results = extract_json_fc_elements(output, elements, task_id)
        elif condition == "fipa_acl":
            elem_results = extract_fipa_acl_elements(output, elements, task_id)
        else:
            elem_results = {}
    else:
        # Judge-scored conditions — mark all elements as needing judge
        elem_results = {}
        for elem in elements:
            needs_judge.append(elem["id"])

    # ── Score composition-structure ──────────────────────────────────
    cs_results = {}
    if condition in COMPOSITION_MACHINE_CONDITIONS:
        cs_results = extract_axon_composition(output, cs_elements, task_id)
    else:
        # Try text-based extraction as pre-filter
        text_results = extract_text_composition(output, cs_elements, task_id)
        for elem in cs_elements:
            eid = elem["id"]
            if text_results.get(eid) is not None:
                cs_results[eid] = text_results[eid]
            else:
                needs_judge.append(eid)

    # ── Measure nesting depth ────────────────────────────────────────
    nesting_depth = 0
    if condition == "axon":
        nesting_depth = measure_nesting_depth(output)

    # ── Calculate rates ──────────────────────────────────────────────
    elem_total = len(elements)
    elem_present = sum(
        1 for r in elem_results.values()
        if r.get("verdict") == "PRESENT"
    )
    element_rate = elem_present / elem_total if elem_total > 0 else 0.0

    cs_total = len(cs_elements)
    cs_present = sum(
        1 for r in cs_results.values()
        if r.get("verdict") == "PRESENT"
    )
    composition_rate = cs_present / cs_total if cs_total > 0 else 0.0

    return {
        "elements": elem_results,
        "composition_structure": cs_results,
        "nesting_depth": nesting_depth,
        "element_rate": element_rate,
        "composition_rate": composition_rate,
        "element_total": elem_total,
        "element_present": elem_present,
        "cs_total": cs_total,
        "cs_present": cs_present,
        "needs_judge": needs_judge,
    }


def score_results_file(filepath: str, annotations: dict) -> dict:
    """Score all outputs in a results JSON file.

    Returns a scored results dict with per-output scores added.
    """
    with open(filepath) as f:
        data = json.load(f)

    scored_results = []
    total_needs_judge = 0

    for result in data["results"]:
        task_id = result["task_id"]
        condition = result["condition"]
        output = result["output"]

        scores = score_output(condition, output, task_id, annotations)
        result["scores"] = scores
        total_needs_judge += len(scores["needs_judge"])
        scored_results.append(result)

    data["results"] = scored_results
    data["scoring"] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_scored": len(scored_results),
        "total_needs_judge": total_needs_judge,
        "method": "machine (AXON AST) + text extraction (structured) + judge pending (English/AISP)",
    }

    return data


def print_scoring_summary(data: dict):
    """Print a summary of scoring results."""
    results = data["results"]

    print("\n" + "=" * 70)
    print("EXP 3 SCORING SUMMARY")
    print("=" * 70)

    # Per-condition composition rates
    conditions = sorted(set(r["condition"] for r in results))

    print(f"\n{'Condition':<28} {'Comp Rate':>10} {'Elem Rate':>10} {'N':>5} {'Judge':>6}")
    print("-" * 65)

    for c in conditions:
        c_results = [r for r in results if r["condition"] == c]
        scored = [r for r in c_results if "scores" in r]
        if not scored:
            continue

        comp_rates = [r["scores"]["composition_rate"] for r in scored]
        elem_rates = [r["scores"]["element_rate"] for r in scored]
        needs_judge = sum(len(r["scores"]["needs_judge"]) for r in scored)

        mean_comp = sum(comp_rates) / len(comp_rates) if comp_rates else 0
        mean_elem = sum(elem_rates) / len(elem_rates) if elem_rates else 0

        print(f"  {c:<26} {mean_comp:>9.1%} {mean_elem:>9.1%} {len(scored):>5} {needs_judge:>6}")

    # Per-level composition rates
    print(f"\n{'Level':<28} {'Comp Rate':>10} {'Elem Rate':>10} {'N':>5}")
    print("-" * 55)

    for level_prefix in ["L1", "L2", "L3"]:
        l_results = [
            r for r in results
            if r["task_id"].startswith(level_prefix) and "scores" in r
        ]
        if not l_results:
            continue

        comp_rates = [r["scores"]["composition_rate"] for r in l_results]
        elem_rates = [r["scores"]["element_rate"] for r in l_results]

        mean_comp = sum(comp_rates) / len(comp_rates) if comp_rates else 0
        mean_elem = sum(elem_rates) / len(elem_rates) if elem_rates else 0

        print(f"  {level_prefix:<26} {mean_comp:>9.1%} {mean_elem:>9.1%} {len(l_results):>5}")

    # Nesting depth stats for AXON
    axon_l23 = [
        r for r in results
        if r["condition"] == "axon"
        and r["task_id"].startswith(("L2", "L3"))
        and "scores" in r
    ]
    if axon_l23:
        depths = [r["scores"]["nesting_depth"] for r in axon_l23]
        print(f"\nAXON nesting depth (L2+L3): "
              f"mean={sum(depths)/len(depths):.1f}, "
              f"max={max(depths)}, "
              f"min={min(depths)}")


def run_test():
    """Test the composition extractor on a known-good AXON output."""
    print("=" * 60)
    print("Composition Extractor — Self-Test")
    print("=" * 60)

    annotations = load_annotations()

    # Test L1-01: Sequential pipeline
    test_output = 'REQ(@data_processor > @worker): download("data_lake") -> clean(remove_nulls=true) -> upload("warehouse")'
    print(f"\nTest L1-01 (sequence):")
    print(f"  Input: {test_output}")
    scores = score_output("axon", test_output, "L1-01", annotations)
    print(f"  Element rate: {scores['element_rate']:.0%} ({scores['element_present']}/{scores['element_total']})")
    print(f"  Composition rate: {scores['composition_rate']:.0%} ({scores['cs_present']}/{scores['cs_total']})")
    for cs_id, cs_result in scores["composition_structure"].items():
        print(f"    {cs_id}: {cs_result['verdict']} — {cs_result['evidence'][:60]}")

    # Test L1-02: Parallel execution
    test_output2 = 'REQ(@deployer > @cluster_mgr): check(cpu_usage) & check(memory_usage) & check(disk_space)'
    print(f"\nTest L1-02 (parallel):")
    print(f"  Input: {test_output2}")
    scores2 = score_output("axon", test_output2, "L1-02", annotations)
    print(f"  Element rate: {scores2['element_rate']:.0%} ({scores2['element_present']}/{scores2['element_total']})")
    print(f"  Composition rate: {scores2['composition_rate']:.0%} ({scores2['cs_present']}/{scores2['cs_total']})")
    for cs_id, cs_result in scores2["composition_structure"].items():
        print(f"    {cs_id}: {cs_result['verdict']} — {cs_result['evidence'][:60]}")

    # Test L2-01: Sequence + parallel nesting
    test_output3 = 'REQ(@orchestrator > @pipeline): validate(schema) -> (sentiment_analysis() & topic_classification()) -> merge(results)'
    print(f"\nTest L2-01 (sequence + parallel nesting):")
    print(f"  Input: {test_output3}")
    scores3 = score_output("axon", test_output3, "L2-01", annotations)
    print(f"  Element rate: {scores3['element_rate']:.0%} ({scores3['element_present']}/{scores3['element_total']})")
    print(f"  Composition rate: {scores3['composition_rate']:.0%} ({scores3['cs_present']}/{scores3['cs_total']})")
    print(f"  Nesting depth: {scores3['nesting_depth']}")
    for cs_id, cs_result in scores3["composition_structure"].items():
        print(f"    {cs_id}: {cs_result['verdict']} — {cs_result['evidence'][:60]}")

    # Test nesting depth
    print(f"\nNesting depth measurement:")
    for label, out in [
        ("flat sequence", 'REQ(@a>@b): x -> y -> z'),
        ("parallel in seq", 'REQ(@a>@b): x -> (y & z) -> w'),
        ("nested 3-deep", 'REQ(@a>@b): x -> (y & (z | w)) -> v'),
    ]:
        depth = measure_nesting_depth(out)
        print(f"  {label}: depth={depth}")

    print("\nSelf-test complete.")


def main():
    parser = argparse.ArgumentParser(description="Exp 3: Compositionality Scorer")
    parser.add_argument("files", nargs="*", help="Results JSON files to score")
    parser.add_argument("--test", action="store_true", help="Run self-test")
    parser.add_argument("--judge", action="store_true",
                        help="Enable judge scoring for English conditions (requires CLI tools)")
    parser.add_argument("--cross-validate", action="store_true",
                        help="Cross-validate AXON machine scores against judge panel")
    args = parser.parse_args()

    if args.test:
        run_test()
        return

    if not args.files:
        parser.print_help()
        return

    annotations = load_annotations()

    for filepath in args.files:
        print(f"\nScoring: {filepath}")
        scored_data = score_results_file(filepath, annotations)
        print_scoring_summary(scored_data)

        # Save scored results
        out_path = filepath.replace(".json", "_scored.json")
        with open(out_path, "w") as f:
            json.dump(scored_data, f, indent=2)
        print(f"\nScored results saved: {out_path}")


if __name__ == "__main__":
    main()
