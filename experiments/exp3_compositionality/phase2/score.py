"""
Exp 3 Phase 2: Decomposition Scoring

Scores round-trip decomposition quality by comparing extracted steps/relationships
against element annotations (ground truth).

Metrics:
  - step_recall: proportion of expected elements found in decomposition steps
  - relationship_accuracy: proportion of relationships correctly typed
  - overall_decomp_score: harmonic mean of step_recall and relationship_accuracy

Usage:
    python3 experiments/exp3_compositionality/phase2/score.py results/phase2_decomposition_*.json
    python3 experiments/exp3_compositionality/phase2/score.py --dry-run results/phase2_decomposition_*.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
ANNOTATIONS_FILE = PROJECT_ROOT / "experiments" / "exp3_compositionality" / "tasks" / "element_annotations.json"


def load_annotations() -> dict:
    with open(ANNOTATIONS_FILE) as f:
        return json.load(f)


def score_decomposition(result: dict, annotations: dict) -> dict:
    """Score a single decomposition result against annotations.

    Returns dict with step_recall, relationship_accuracy, decomp_score.
    """
    task_id = result["task_id"]
    parsed = result.get("decomp_parsed")

    if not parsed:
        return {
            "parseable": False,
            "step_recall": 0.0,
            "relationship_accuracy": 0.0,
            "decomp_score": 0.0,
            "steps_found": 0,
            "steps_expected": 0,
            "rels_correct": 0,
            "rels_total": 0,
        }

    # Get annotation for this task
    task_ann = annotations.get(task_id, {})
    expected_elements = task_ann.get("elements", [])
    expected_cs = task_ann.get("composition_structure", [])

    # Count extracted steps
    steps = parsed.get("steps", [])
    rels = parsed.get("relationships", [])

    # Step recall: how many expected elements have a matching step?
    # Match by checking if element description appears in any step action
    matched = 0
    for elem in expected_elements:
        elem_lower = elem.get("key", "").lower().replace("_", " ")
        for step in steps:
            action_lower = step.get("action", "").lower()
            if elem_lower in action_lower or any(
                word in action_lower
                for word in elem_lower.split()
                if len(word) > 3
            ):
                matched += 1
                break

    step_recall = matched / len(expected_elements) if expected_elements else 1.0

    # Relationship accuracy: proportion of extracted relationships with valid types
    valid_types = {"SEQUENCE", "PARALLEL", "ALTERNATIVE", "CAUSAL", "NESTED"}
    rels_correct = sum(
        1 for r in rels if r.get("type", "").upper() in valid_types
    )
    relationship_accuracy = rels_correct / len(rels) if rels else 0.0

    # Also check if the number of relationships is reasonable vs expected
    expected_rels = len(expected_cs)
    rel_count_ratio = min(len(rels), expected_rels) / max(expected_rels, 1)

    # Decomp score: harmonic mean of step recall and relationship accuracy
    if step_recall + relationship_accuracy > 0:
        decomp_score = (
            2 * step_recall * relationship_accuracy
            / (step_recall + relationship_accuracy)
        )
    else:
        decomp_score = 0.0

    return {
        "parseable": True,
        "step_recall": round(step_recall, 3),
        "relationship_accuracy": round(relationship_accuracy, 3),
        "decomp_score": round(decomp_score, 3),
        "steps_found": len(steps),
        "steps_expected": len(expected_elements),
        "rels_correct": rels_correct,
        "rels_total": len(rels),
        "rels_expected": expected_rels,
        "rel_count_ratio": round(rel_count_ratio, 3),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Exp 3 Phase 2: Decomposition Scorer"
    )
    parser.add_argument("files", nargs="*", help="Phase 2 result JSON files")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not args.files:
        parser.print_help()
        return

    annotations = load_annotations()

    for filepath in args.files:
        print(f"\nScoring: {filepath}")
        with open(filepath) as f:
            data = json.load(f)

        results = data["results"]
        if args.dry_run:
            parseable = sum(1 for r in results if r.get("decomp_parsed"))
            print(f"  {len(results)} results, {parseable} parseable")
            by_cond = {}
            for r in results:
                c = r["condition"]
                by_cond[c] = by_cond.get(c, 0) + 1
            for c in sorted(by_cond):
                print(f"    {c}: {by_cond[c]}")
            continue

        # Score each result
        scored = []
        for r in results:
            scores = score_decomposition(r, annotations)
            r["decomp_scores"] = scores
            scored.append(r)

        # Summary by condition
        print(f"\n{'Condition':<30} {'Parse%':>7} {'StepRec':>8} {'RelAcc':>7} {'Decomp':>7} {'N':>4}")
        print("-" * 70)

        by_condition = {}
        for r in scored:
            c = r["condition"]
            if c not in by_condition:
                by_condition[c] = []
            by_condition[c].append(r["decomp_scores"])

        overall_scores = []
        for c in sorted(by_condition):
            entries = by_condition[c]
            n = len(entries)
            parseable = sum(1 for e in entries if e["parseable"])
            parse_pct = parseable / n if n else 0
            avg_recall = sum(e["step_recall"] for e in entries) / n
            avg_rel_acc = sum(e["relationship_accuracy"] for e in entries) / n
            avg_decomp = sum(e["decomp_score"] for e in entries) / n
            print(f"{c:<30} {parse_pct:>6.0%} {avg_recall:>8.1%} {avg_rel_acc:>7.1%} {avg_decomp:>7.1%} {n:>4}")
            overall_scores.extend(entries)

        n_total = len(overall_scores)
        parseable_total = sum(1 for e in overall_scores if e["parseable"])
        print("-" * 70)
        print(f"{'OVERALL':<30} {parseable_total/n_total:>6.0%} "
              f"{sum(e['step_recall'] for e in overall_scores)/n_total:>8.1%} "
              f"{sum(e['relationship_accuracy'] for e in overall_scores)/n_total:>7.1%} "
              f"{sum(e['decomp_score'] for e in overall_scores)/n_total:>7.1%} "
              f"{n_total:>4}")

        # Summary by original model → decomp model
        print(f"\n{'Pair':<30} {'Parse%':>7} {'Decomp':>7} {'N':>4}")
        print("-" * 50)
        by_pair = {}
        for r in scored:
            pair = f"{r['original_model']}→{r['decomp_model']}"
            if pair not in by_pair:
                by_pair[pair] = []
            by_pair[pair].append(r["decomp_scores"])
        for pair in sorted(by_pair):
            entries = by_pair[pair]
            n = len(entries)
            parseable = sum(1 for e in entries if e["parseable"])
            avg_decomp = sum(e["decomp_score"] for e in entries) / n
            print(f"{pair:<30} {parseable/n:>6.0%} {avg_decomp:>7.1%} {n:>4}")

        # Summary by complexity level
        print(f"\n{'Complexity':<30} {'Parse%':>7} {'Decomp':>7} {'N':>4}")
        print("-" * 50)
        by_complexity = {}
        for r in scored:
            lvl = r.get("complexity_level", 0)
            if lvl not in by_complexity:
                by_complexity[lvl] = []
            by_complexity[lvl].append(r["decomp_scores"])
        for lvl in sorted(by_complexity):
            entries = by_complexity[lvl]
            n = len(entries)
            parseable = sum(1 for e in entries if e["parseable"])
            avg_decomp = sum(e["decomp_score"] for e in entries) / n
            print(f"Level {lvl:<25} {parseable/n:>6.0%} {avg_decomp:>7.1%} {n:>4}")

        # Save scored results
        out_path = filepath.replace(".json", "_scored.json")
        data["results"] = scored
        data["scoring"] = {
            "total": n_total,
            "parseable": parseable_total,
            "mean_step_recall": round(sum(e["step_recall"] for e in overall_scores) / n_total, 3),
            "mean_relationship_accuracy": round(sum(e["relationship_accuracy"] for e in overall_scores) / n_total, 3),
            "mean_decomp_score": round(sum(e["decomp_score"] for e in overall_scores) / n_total, 3),
        }
        with open(out_path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"\nScored: {out_path}")


if __name__ == "__main__":
    main()
