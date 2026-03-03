"""
Exp 2: Parse Accuracy Under Noise — Runner

Loads valid Exp 1 outputs, applies deterministic perturbations, and validates
the perturbed outputs using the condition adapter.

No LLM calls needed — perturbation + validation are purely local.

Usage:
    python3 experiments/exp2_parse_accuracy/run.py --all
    python3 experiments/exp2_parse_accuracy/run.py --condition axon --perturbation char_deletion
    python3 experiments/exp2_parse_accuracy/run.py --dry-run
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime, timezone

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "experiments"))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from lib.condition_adapter import validate_output, CONDITIONS
from lib.token_counter import count_tokens_multi
from exp2_parse_accuracy.perturbation.perturbation_engine import (
    apply_perturbation,
    compute_seed,
    PERTURBATION_TYPES,
)

EXP1_RESULTS_DIR = PROJECT_ROOT / "experiments" / "exp1_token_efficiency" / "results"
EXP2_RESULTS_DIR = Path(__file__).parent / "results"

# Also include Exp 3 scored results for AISP condition
EXP3_RESULTS_DIR = PROJECT_ROOT / "experiments" / "exp3_compositionality" / "results"


def load_valid_outputs() -> list[dict]:
    """Load valid outputs from Exp 1 scored results.

    Returns flat list of {task_id, condition, model, run_number, output, token_counts}.
    """
    outputs = []

    # Load from Exp 1 (6 conditions)
    for path in sorted(EXP1_RESULTS_DIR.glob("exp1_scored_*.json")):
        with open(path) as f:
            data = json.load(f)
        for r in data["results"]:
            if r["valid"] and r.get("output"):
                outputs.append({
                    "task_id": r["task_id"],
                    "condition": r["condition"],
                    "model": r["model"],
                    "run_number": r["run_number"],
                    "output": r["output"],
                    "token_counts": r.get("token_counts", {}),
                })

    # Load AISP from Exp 3 scored results
    for path in sorted(EXP3_RESULTS_DIR.glob("*_scored*.json")):
        with open(path) as f:
            data = json.load(f)
        for r in data["results"]:
            if r["condition"] == "aisp" and r.get("valid", False) and r.get("output"):
                outputs.append({
                    "task_id": r["task_id"],
                    "condition": r["condition"],
                    "model": r["model"],
                    "run_number": r["run_number"],
                    "output": r["output"],
                    "token_counts": r.get("token_counts", {}),
                })

    return outputs


def run_perturbations(outputs: list[dict],
                      conditions_filter: list[str] | None = None,
                      perturbation_filter: list[str] | None = None) -> list[dict]:
    """Apply perturbations and validate.

    Returns list of result records.
    """
    results = []
    conditions = conditions_filter or CONDITIONS
    perturbations = perturbation_filter or PERTURBATION_TYPES

    for record in outputs:
        cond = record["condition"]
        if cond not in conditions:
            continue

        task_id = record["task_id"]
        model = record["model"]
        run_number = record["run_number"]
        original = record["output"]

        for ptype in perturbations:
            seed = compute_seed(task_id, cond, model, run_number, ptype)
            perturbed = apply_perturbation(original, ptype, seed)

            # Validate perturbed output
            validation = validate_output(cond, perturbed)

            # Token count on perturbed output
            try:
                perturbed_tokens = count_tokens_multi(perturbed)
            except Exception:
                perturbed_tokens = {}

            level_str = task_id.split("-")[0]
            complexity = {"L1": 1, "L2": 2, "L3": 3}.get(level_str, 0)

            results.append({
                "task_id": task_id,
                "condition": cond,
                "model": model,
                "run_number": run_number,
                "perturbation_type": ptype,
                "seed": seed,
                "original": original,
                "perturbed": perturbed,
                "original_length": len(original),
                "perturbed_length": len(perturbed),
                "preserved": validation["valid"],
                "validation_errors": validation.get("errors", []),
                "token_counts_original": record.get("token_counts", {}),
                "token_counts_perturbed": perturbed_tokens,
                "complexity_level": complexity,
            })

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Exp 2: Parse Accuracy Under Noise — Runner"
    )
    parser.add_argument("--all", action="store_true",
                        help="Run all conditions and perturbation types")
    parser.add_argument("--condition", action="append", dest="conditions",
                        help="Filter to specific condition(s)")
    parser.add_argument("--perturbation", action="append", dest="perturbations",
                        help="Filter to specific perturbation type(s)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show counts without running")
    args = parser.parse_args()

    if not args.all and not args.conditions:
        parser.print_help()
        return

    # Load source outputs
    outputs = load_valid_outputs()
    print(f"Loaded {len(outputs)} valid source outputs")

    # Count by condition
    by_cond = {}
    for o in outputs:
        by_cond[o["condition"]] = by_cond.get(o["condition"], 0) + 1
    for cond in sorted(by_cond):
        print(f"  {cond}: {by_cond[cond]}")

    if args.dry_run:
        n_cond = len(args.conditions or CONDITIONS)
        n_pert = len(args.perturbations or PERTURBATION_TYPES)
        total_cells = sum(by_cond.get(c, 0) for c in (args.conditions or CONDITIONS)) * n_pert
        print(f"\nWould generate {total_cells} perturbed outputs")
        print(f"  Conditions: {args.conditions or CONDITIONS}")
        print(f"  Perturbation types: {args.perturbations or PERTURBATION_TYPES}")
        return

    # Run perturbations
    results = run_perturbations(outputs, args.conditions, args.perturbations)
    print(f"\nGenerated {len(results)} perturbed outputs")

    # Summary
    print(f"\n{'Condition':<28} {'Char Del':>9} {'Tok Swap':>9} {'Truncate':>9} {'Overall':>9}")
    print("-" * 70)
    for cond in CONDITIONS:
        cr = [r for r in results if r["condition"] == cond]
        if not cr:
            continue
        rates = {}
        for ptype in PERTURBATION_TYPES:
            pr = [r for r in cr if r["perturbation_type"] == ptype]
            if pr:
                rate = sum(1 for r in pr if r["preserved"]) / len(pr)
                rates[ptype] = rate
        overall = sum(1 for r in cr if r["preserved"]) / len(cr) if cr else 0
        print(f"  {cond:<26} {rates.get('char_deletion', 0):>8.1%} "
              f"{rates.get('token_swap', 0):>8.1%} "
              f"{rates.get('truncation', 0):>8.1%} {overall:>8.1%}")

    # Save results
    EXP2_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    outfile = EXP2_RESULTS_DIR / f"exp2_perturbation_results_{timestamp}.json"

    data = {
        "experiment": "exp2_parse_accuracy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "exp1_scored + exp3_scored (AISP)",
        "total_results": len(results),
        "perturbation_types": PERTURBATION_TYPES,
        "conditions": sorted(set(r["condition"] for r in results)),
        "results": results,
    }

    with open(outfile, "w") as f:
        json.dump(data, f, indent=2)
    print(f"\nResults saved: {outfile}")


if __name__ == "__main__":
    main()
