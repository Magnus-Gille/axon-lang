"""
Exp 5: Cross-Model Generalization — Analysis

Extracts cross-model consistency metrics from existing Exp 1 and Exp 3 data.
No new data collection needed — this analysis reuses scored results.

Metrics:
- Per-condition cross-model SD (lower = more consistent across models)
- Levene's test for equality of variances (AXON vs each condition)
- Coefficient of Variation (CV) for normalized comparison

Usage:
    python3 experiments/exp5_cross_model/analyze.py --all
    python3 experiments/exp5_cross_model/analyze.py --exp1-dir results/ --exp3-dir results/
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from dataclasses import dataclass

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
EXP1_RESULTS_DIR = PROJECT_ROOT / "experiments" / "exp1_token_efficiency" / "results"
EXP3_RESULTS_DIR = PROJECT_ROOT / "experiments" / "exp3_compositionality" / "results"
EXP5_DIR = Path(__file__).resolve().parent

CONDITIONS_PREREG = [
    "free_english", "structured_english", "instruction_matched_english",
    "json_fc", "fipa_acl", "axon",
]
CONDITIONS_ALL = CONDITIONS_PREREG + ["aisp"]

MODELS = ["codex", "claude-haiku", "claude-sonnet"]


def load_exp1_records(results_dir: Path) -> list[dict]:
    """Load Exp 1 scored results into flat records."""
    records = []
    for path in sorted(results_dir.glob("exp1_scored_*.json")):
        with open(path) as f:
            data = json.load(f)
        for r in data["results"]:
            if r.get("tokens_per_unit") is not None:
                records.append({
                    "task_id": r["task_id"],
                    "condition": r["condition"],
                    "model": r["model"],
                    "run_number": r["run_number"],
                    "tokens_per_unit": r["tokens_per_unit"],
                    "valid": r["valid"],
                })
    return records


def load_exp3_records(results_dir: Path) -> list[dict]:
    """Load Exp 3 scored results into flat records."""
    records = []
    for path in sorted(results_dir.glob("*_scored*.json")):
        with open(path) as f:
            data = json.load(f)
        for r in data["results"]:
            scores = r.get("scores", {})
            records.append({
                "task_id": r["task_id"],
                "condition": r["condition"],
                "model": r["model"],
                "run_number": r["run_number"],
                "composition_rate": scores.get("composition_rate", 0.0),
                "element_rate": scores.get("element_rate", 0.0),
                "valid": r.get("valid", False),
            })
    return records


def model_means(records: list[dict], metric: str) -> dict[str, dict[str, float]]:
    """Compute per-model means for each condition.

    Returns: {condition: {model: mean_value}}
    """
    # Group by (condition, model)
    grouped = {}
    for r in records:
        key = (r["condition"], r["model"])
        grouped.setdefault(key, []).append(r[metric])

    result = {}
    for (cond, model), vals in grouped.items():
        result.setdefault(cond, {})[model] = float(np.mean(vals))
    return result


def cross_model_variance(records: list[dict], metric: str,
                         label: str, conditions: list[str]):
    """Compute cross-model SD and CV for each condition."""
    from scipy import stats as sp_stats

    means = model_means(records, metric)

    print(f"\n{'=' * 80}")
    print(f"CROSS-MODEL CONSISTENCY — {label}")
    print(f"{'=' * 80}")

    # Per-model means table
    present_models = sorted(set(r["model"] for r in records))
    header = f"{'Condition':<28}"
    for m in present_models:
        header += f" {m:>14}"
    header += f" {'SD':>8} {'CV':>8}"
    print(f"\n{header}")
    print("-" * (28 + 15 * len(present_models) + 18))

    condition_sds = {}
    for cond in conditions:
        if cond not in means:
            continue
        model_vals = [means[cond].get(m, float("nan")) for m in present_models]
        valid_vals = [v for v in model_vals if not np.isnan(v)]
        if len(valid_vals) < 2:
            continue

        sd = float(np.std(valid_vals, ddof=1))
        mean_val = float(np.mean(valid_vals))
        cv = sd / mean_val if mean_val > 0 else float("inf")
        condition_sds[cond] = {"sd": sd, "cv": cv, "model_vals": valid_vals}

        row = f"  {cond:<26}"
        for m in present_models:
            v = means[cond].get(m, float("nan"))
            row += f" {v:>14.3f}"
        marker = " *" if cond == "aisp" else ""
        row += f" {sd:>8.3f} {cv:>8.3f}{marker}"
        print(row)

    # Levene's test: AXON vs each condition
    if "axon" not in condition_sds:
        print("\n  No AXON data for Levene's test.")
        return condition_sds

    print(f"\n{'LEVENE TEST — AXON vs each condition':=^80}")
    print(f"  H0: Equal cross-model variance. Rejection means significantly different variance.")
    print(f"\n  {'Comparison':<35} {'AXON SD':>8} {'Other SD':>9} "
          f"{'F':>8} {'p':>8} {'Sig':>5}")
    print("  " + "-" * 75)

    axon_vals_all = _per_model_run_values(records, "axon", metric)

    for cond in conditions:
        if cond == "axon" or cond not in condition_sds:
            continue
        other_vals_all = _per_model_run_values(records, cond, metric)
        if len(other_vals_all) < 2:
            continue

        try:
            stat, p_val = sp_stats.levene(axon_vals_all, other_vals_all, center="median")
            sig = "*" if p_val < 0.05 else ""
            print(f"  AXON vs {cond:<24} "
                  f"{condition_sds['axon']['sd']:>8.3f} "
                  f"{condition_sds[cond]['sd']:>9.3f} "
                  f"{stat:>8.2f} {p_val:>8.4f} {sig:>5}")
        except Exception as e:
            print(f"  AXON vs {cond:<24} Levene test failed: {e}")

    return condition_sds


def _per_model_run_values(records: list[dict], condition: str,
                          metric: str) -> list[float]:
    """Get per-model mean values for a condition (for Levene's test).

    Groups by model, returns the model-level means as the test input.
    This tests whether the spread of model-level means differs between conditions.
    """
    by_model = {}
    for r in records:
        if r["condition"] == condition:
            by_model.setdefault(r["model"], []).append(r[metric])
    return [float(np.mean(vals)) for vals in by_model.values()]


def failure_rate_analysis(records: list[dict], conditions: list[str]):
    """Cross-model failure rate consistency."""
    print(f"\n{'=' * 80}")
    print("CROSS-MODEL FAILURE RATE CONSISTENCY")
    print("=" * 80)

    present_models = sorted(set(r["model"] for r in records))
    header = f"{'Condition':<28}"
    for m in present_models:
        header += f" {m:>14}"
    header += f" {'SD':>8}"
    print(f"\n{header}")
    print("-" * (28 + 15 * len(present_models) + 10))

    for cond in conditions:
        model_rates = []
        row = f"  {cond:<26}"
        for m in present_models:
            cr = [r for r in records if r["condition"] == cond and r["model"] == m]
            if cr:
                fail_rate = sum(1 for r in cr if not r["valid"]) / len(cr)
                model_rates.append(fail_rate)
                row += f" {fail_rate:>13.1%}"
            else:
                row += f" {'N/A':>14}"
        sd = float(np.std(model_rates, ddof=1)) if len(model_rates) > 1 else 0
        row += f" {sd:>8.3f}"
        print(row)


def write_results_summary(exp1_sds: dict, exp3_sds: dict, output_path: Path):
    """Write RESULTS.md summary."""
    lines = [
        "# Experiment 5: Cross-Model Generalization — Results",
        "",
        f"**Generated**: {__import__('datetime').datetime.now().isoformat()}",
        "",
        "## Summary",
        "",
        "Cross-model consistency analysis using Exp 1 (token efficiency) and",
        "Exp 3 (compositionality) scored data. No new data collection.",
        "",
        "### Token Efficiency (Exp 1) — Cross-Model SD",
        "",
        "| Condition | SD (tok/unit) | CV |",
        "|-----------|---------------|-----|",
    ]
    for cond in CONDITIONS_ALL:
        if cond in exp1_sds:
            s = exp1_sds[cond]
            marker = " (exploratory)" if cond == "aisp" else ""
            lines.append(f"| {cond}{marker} | {s['sd']:.3f} | {s['cv']:.3f} |")

    lines.extend([
        "",
        "### Compositionality (Exp 3) — Cross-Model SD",
        "",
        "| Condition | SD (comp rate) | CV |",
        "|-----------|----------------|-----|",
    ])
    for cond in CONDITIONS_ALL:
        if cond in exp3_sds:
            s = exp3_sds[cond]
            marker = " (exploratory)" if cond == "aisp" else ""
            lines.append(f"| {cond}{marker} | {s['sd']:.3f} | {s['cv']:.3f} |")

    lines.extend(["", "Lower SD = more consistent across models.", ""])

    with open(output_path, "w") as f:
        f.write("\n".join(lines))
    print(f"\n  Results written to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Exp 5: Cross-Model Generalization Analysis"
    )
    parser.add_argument("--exp1-dir", type=Path, help="Exp 1 results directory")
    parser.add_argument("--exp3-dir", type=Path, help="Exp 3 results directory")
    parser.add_argument("--all", action="store_true",
                        help="Use default result directories")
    parser.add_argument("--write-results", action="store_true",
                        help="Write RESULTS.md")
    args = parser.parse_args()

    if args.all:
        exp1_dir = EXP1_RESULTS_DIR
        exp3_dir = EXP3_RESULTS_DIR
    elif args.exp1_dir and args.exp3_dir:
        exp1_dir = args.exp1_dir
        exp3_dir = args.exp3_dir
    else:
        parser.print_help()
        return

    # Load data
    exp1_records = load_exp1_records(exp1_dir)
    exp3_records = load_exp3_records(exp3_dir)
    print(f"Loaded {len(exp1_records)} Exp 1 records, {len(exp3_records)} Exp 3 records")

    # Detect conditions
    conditions = CONDITIONS_ALL if any(
        r["condition"] == "aisp" for r in exp1_records + exp3_records
    ) else CONDITIONS_PREREG

    # Exp 1: tok/unit cross-model consistency
    exp1_sds = cross_model_variance(
        exp1_records, "tokens_per_unit",
        "Token Efficiency (tok/unit, Exp 1)", conditions
    )

    # Exp 3: composition rate cross-model consistency
    exp3_sds = cross_model_variance(
        exp3_records, "composition_rate",
        "Composition Rate (Exp 3)", conditions
    )

    # Failure rate consistency
    failure_rate_analysis(exp3_records, conditions)

    if args.write_results:
        write_results_summary(exp1_sds, exp3_sds, EXP5_DIR / "RESULTS.md")


if __name__ == "__main__":
    main()
