"""
Exp 2: Parse Accuracy Under Noise — Statistical Analysis

Analyzes structural preservation rates across conditions and perturbation types.

Usage:
    python3 experiments/exp2_parse_accuracy/analysis/analyze.py --all
    python3 experiments/exp2_parse_accuracy/analysis/analyze.py --results <file.json>
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from dataclasses import dataclass

import numpy as np

EXP2_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = EXP2_DIR / "results"

CONDITIONS_PREREG = [
    "free_english", "structured_english", "instruction_matched_english",
    "json_fc", "fipa_acl", "axon",
]
CONDITIONS_ALL = CONDITIONS_PREREG + ["aisp"]

PERTURBATION_TYPES = ["char_deletion", "token_swap", "truncation"]
COMPLEXITY_MAP = {"L1": 1, "L2": 2, "L3": 3}


@dataclass
class Record:
    task_id: str
    condition: str
    model: str
    run_number: int
    perturbation_type: str
    complexity_level: int
    preserved: bool
    original_length: int
    perturbed_length: int


def load_results(path: Path) -> list[Record]:
    """Load perturbation results into analysis records."""
    with open(path) as f:
        data = json.load(f)

    records = []
    for r in data["results"]:
        records.append(Record(
            task_id=r["task_id"],
            condition=r["condition"],
            model=r["model"],
            run_number=r["run_number"],
            perturbation_type=r["perturbation_type"],
            complexity_level=r.get("complexity_level", 0),
            preserved=r["preserved"],
            original_length=r.get("original_length", 0),
            perturbed_length=r.get("perturbed_length", 0),
        ))
    return records


def descriptive_stats(records: list[Record]):
    """Print descriptive statistics."""
    print("\n" + "=" * 80)
    print("DESCRIPTIVE STATISTICS — Structural Preservation Rate")
    print("=" * 80)

    # Per-condition × perturbation type
    print(f"\n{'Condition':<28}", end="")
    for pt in PERTURBATION_TYPES:
        print(f" {pt:>14}", end="")
    print(f" {'Overall':>9}")
    print("-" * (28 + 15 * len(PERTURBATION_TYPES) + 10))

    for cond in CONDITIONS_ALL:
        cr = [r for r in records if r.condition == cond]
        if not cr:
            continue
        line = f"  {cond:<26}"
        for pt in PERTURBATION_TYPES:
            pr = [r for r in cr if r.perturbation_type == pt]
            if pr:
                rate = sum(1 for r in pr if r.preserved) / len(pr)
                line += f" {rate:>13.1%}"
            else:
                line += f" {'N/A':>14}"
        overall = sum(1 for r in cr if r.preserved) / len(cr) if cr else 0
        marker = " *" if cond == "aisp" else ""
        line += f" {overall:>8.1%}{marker}"
        print(line)

    # Per-model
    print(f"\n{'Model':<28}", end="")
    for pt in PERTURBATION_TYPES:
        print(f" {pt:>14}", end="")
    print(f" {'Overall':>9}")
    print("-" * (28 + 15 * len(PERTURBATION_TYPES) + 10))

    for model in sorted(set(r.model for r in records)):
        mr = [r for r in records if r.model == model]
        line = f"  {model:<26}"
        for pt in PERTURBATION_TYPES:
            pr = [r for r in mr if r.perturbation_type == pt]
            if pr:
                rate = sum(1 for r in pr if r.preserved) / len(pr)
                line += f" {rate:>13.1%}"
            else:
                line += f" {'N/A':>14}"
        overall = sum(1 for r in mr if r.preserved) / len(mr) if mr else 0
        line += f" {overall:>8.1%}"
        print(line)

    # Per-complexity × perturbation type
    print(f"\n{'Complexity':<28}", end="")
    for pt in PERTURBATION_TYPES:
        print(f" {pt:>14}", end="")
    print()
    print("-" * (28 + 15 * len(PERTURBATION_TYPES)))

    for level_name, level_num in COMPLEXITY_MAP.items():
        lr = [r for r in records if r.complexity_level == level_num]
        if not lr:
            continue
        line = f"  {level_name:<26}"
        for pt in PERTURBATION_TYPES:
            pr = [r for r in lr if r.perturbation_type == pt]
            if pr:
                rate = sum(1 for r in pr if r.preserved) / len(pr)
                line += f" {rate:>13.1%}"
            else:
                line += f" {'N/A':>14}"
        print(line)


def pairwise_comparisons(records: list[Record]):
    """AXON vs each condition pairwise comparisons on preservation rate."""
    from scipy import stats as sp_stats

    print("\n" + "=" * 80)
    print("PAIRWISE COMPARISONS — AXON vs each condition (overall preservation)")
    print("=" * 80)

    axon_records = [r for r in records if r.condition == "axon"]
    axon_rate = sum(1 for r in axon_records if r.preserved) / len(axon_records) if axon_records else 0

    comparisons = []
    other_conditions = [c for c in CONDITIONS_PREREG if c != "axon"]

    for cond in other_conditions:
        other_records = [r for r in records if r.condition == cond]
        if not other_records:
            continue
        other_rate = sum(1 for r in other_records if r.preserved) / len(other_records)

        # Fisher's exact test (2x2: preserved/not × condition)
        a_pres = sum(1 for r in axon_records if r.preserved)
        a_fail = len(axon_records) - a_pres
        o_pres = sum(1 for r in other_records if r.preserved)
        o_fail = len(other_records) - o_pres

        _, p_val = sp_stats.fisher_exact([[a_pres, a_fail], [o_pres, o_fail]])

        # Effect size (difference in proportions)
        diff = axon_rate - other_rate

        comparisons.append({
            "condition": cond,
            "axon_rate": axon_rate,
            "other_rate": other_rate,
            "diff": diff,
            "p_uncorrected": p_val,
        })

    # Holm-Bonferroni
    comparisons.sort(key=lambda c: c["p_uncorrected"])
    k = len(comparisons)
    for i, comp in enumerate(comparisons):
        comp["p_corrected"] = min(comp["p_uncorrected"] * (k - i), 1.0)
        comp["significant"] = comp["p_corrected"] < 0.05

    print(f"\n  {'Comparison':<35} {'AXON':>7} {'Other':>7} {'Diff':>7} "
          f"{'p(raw)':>8} {'p(Holm)':>8} {'Sig':>5}")
    print("  " + "-" * 80)
    for comp in comparisons:
        sig = "*" if comp["significant"] else ""
        print(f"  AXON vs {comp['condition']:<24} {comp['axon_rate']:>6.1%} "
              f"{comp['other_rate']:>6.1%} {comp['diff']:>+6.1%} "
              f"{comp['p_uncorrected']:>8.4f} {comp['p_corrected']:>8.4f} {sig:>5}")

    # AISP (exploratory)
    aisp_records = [r for r in records if r.condition == "aisp"]
    if aisp_records:
        aisp_rate = sum(1 for r in aisp_records if r.preserved) / len(aisp_records)
        a_pres = sum(1 for r in axon_records if r.preserved)
        a_fail = len(axon_records) - a_pres
        o_pres = sum(1 for r in aisp_records if r.preserved)
        o_fail = len(aisp_records) - o_pres
        _, p_val = sp_stats.fisher_exact([[a_pres, a_fail], [o_pres, o_fail]])
        diff = axon_rate - aisp_rate
        print(f"\n  AXON vs aisp (exploratory)       {axon_rate:>6.1%} "
              f"{aisp_rate:>6.1%} {diff:>+6.1%} {p_val:>8.4f}")


def interaction_analysis(records: list[Record]):
    """Condition × perturbation type interaction analysis."""
    print("\n" + "=" * 80)
    print("INTERACTION: Condition × Perturbation Type")
    print("=" * 80)

    # Per-condition × perturbation preservation rates
    print(f"\n{'Condition × PertType':<42} {'N':>5} {'Preserved':>10} {'Rate':>7}")
    print("-" * 68)
    for cond in CONDITIONS_ALL:
        for pt in PERTURBATION_TYPES:
            cr = [r for r in records
                  if r.condition == cond and r.perturbation_type == pt]
            if not cr:
                continue
            n = len(cr)
            pres = sum(1 for r in cr if r.preserved)
            rate = pres / n
            print(f"  {cond} × {pt:<18} {n:>5} {pres:>10} {rate:>6.1%}")

    # Chi-square test for independence (condition × perturbation)
    try:
        from scipy import stats as sp_stats

        # Build contingency table: conditions × perturbation types
        prereg_records = [r for r in records if r.condition in CONDITIONS_PREREG]
        if prereg_records:
            observed = []
            for cond in CONDITIONS_PREREG:
                row = []
                for pt in PERTURBATION_TYPES:
                    cr = [r for r in prereg_records
                          if r.condition == cond and r.perturbation_type == pt]
                    row.append(sum(1 for r in cr if r.preserved))
                observed.append(row)

            chi2, p_val, dof, expected = sp_stats.chi2_contingency(observed)
            print(f"\n  Chi-square test (condition × perturbation independence):")
            print(f"    chi2 = {chi2:.2f}, dof = {dof}, p = {p_val:.4f}")
    except ImportError:
        pass


def mixed_effects_analysis(records: list[Record]):
    """GLMM: preservation ~ condition + perturbation_type + complexity + (1|task) + (1|model)"""
    try:
        import pandas as pd
        import statsmodels.formula.api as smf
    except ImportError:
        print("\n  statsmodels/pandas not installed. Skipping GLMM.")
        return

    print("\n" + "=" * 80)
    print("MIXED-EFFECTS MODEL — preservation rate")
    print("=" * 80)

    prereg = [r for r in records if r.condition in CONDITIONS_PREREG]
    if not prereg:
        return

    df = pd.DataFrame([{
        "preserved": int(r.preserved),
        "condition": r.condition,
        "perturbation_type": r.perturbation_type,
        "complexity": f"L{r.complexity_level}",
        "task": r.task_id,
        "model": r.model,
    } for r in prereg])

    df["condition"] = pd.Categorical(df["condition"], categories=CONDITIONS_PREREG)

    formula = ("preserved ~ C(condition, Treatment(reference='axon')) "
               "+ C(perturbation_type) + C(complexity)")
    print(f"\n  Formula: {formula}")
    print(f"  N = {len(df)}")

    try:
        model = smf.mixedlm(
            formula, df, groups=df["model"],
            re_formula="1", vc_formula={"task": "0 + C(task)"}
        )
        result = model.fit(reml=True)
        print(f"\n{result.summary()}")
    except Exception as e:
        print(f"\n  GLMM failed: {e}")
        print("  Falling back to fixed-effects model...")
        try:
            result = smf.ols(formula + " + C(model)", df).fit()
            print(f"\n{result.summary()}")
        except Exception as e2:
            print(f"\n  Fixed-effects also failed: {e2}")


def bootstrap_ci(records: list[Record], n_boot: int = 10000, seed: int = 42):
    """Bootstrap CIs for preservation rate differences (AXON vs each)."""
    rng = np.random.default_rng(seed)

    print("\n" + "=" * 80)
    print(f"BOOTSTRAP CIs (n={n_boot}) — AXON vs each condition (preservation rate diff)")
    print("=" * 80)

    axon = np.array([int(r.preserved) for r in records if r.condition == "axon"])
    if len(axon) == 0:
        return

    print(f"\n  {'Comparison':<35} {'Diff':>7} {'95% CI':>20}")
    print("  " + "-" * 65)

    for cond in [c for c in CONDITIONS_PREREG if c != "axon"]:
        other = np.array([int(r.preserved) for r in records if r.condition == cond])
        if len(other) == 0:
            continue

        boot_diffs = []
        for _ in range(n_boot):
            a_boot = rng.choice(axon, size=len(axon), replace=True)
            o_boot = rng.choice(other, size=len(other), replace=True)
            boot_diffs.append(float(np.mean(a_boot) - np.mean(o_boot)))

        diffs = np.array(boot_diffs)
        ci_lo = np.percentile(diffs, 2.5)
        ci_hi = np.percentile(diffs, 97.5)
        obs_diff = float(np.mean(axon) - np.mean(other))
        print(f"  AXON vs {cond:<24} {obs_diff:>+6.1%} [{ci_lo:>+8.3f}, {ci_hi:>+8.3f}]")


def write_results_summary(records: list[Record], output_path: Path):
    """Write RESULTS.md."""
    lines = [
        "# Experiment 2: Parse Accuracy Under Noise — Results",
        "",
        f"**Generated**: {__import__('datetime').datetime.now().isoformat()}",
        f"**Total records**: {len(records)}",
        "",
        "## Summary — Structural Preservation Rate",
        "",
        "| Condition | Char Deletion | Token Swap | Truncation | Overall |",
        "|-----------|---------------|------------|------------|---------|",
    ]

    for cond in CONDITIONS_ALL:
        cr = [r for r in records if r.condition == cond]
        if not cr:
            continue
        rates = {}
        for pt in PERTURBATION_TYPES:
            pr = [r for r in cr if r.perturbation_type == pt]
            if pr:
                rates[pt] = sum(1 for r in pr if r.preserved) / len(pr)
        overall = sum(1 for r in cr if r.preserved) / len(cr)
        marker = " (exploratory)" if cond == "aisp" else ""
        lines.append(
            f"| {cond}{marker} | {rates.get('char_deletion', 0):.1%} | "
            f"{rates.get('token_swap', 0):.1%} | "
            f"{rates.get('truncation', 0):.1%} | {overall:.1%} |"
        )

    lines.extend(["", "Higher = more structurally resilient to noise.", ""])

    with open(output_path, "w") as f:
        f.write("\n".join(lines))
    print(f"\n  Results written to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Exp 2: Parse Accuracy — Analysis"
    )
    parser.add_argument("--results", type=Path, help="Single results file")
    parser.add_argument("--all", action="store_true",
                        help="Load all results from default dir")
    parser.add_argument("--write-results", action="store_true",
                        help="Write RESULTS.md")
    args = parser.parse_args()

    if args.all:
        files = sorted(RESULTS_DIR.glob("exp2_*.json"))
    elif args.results:
        files = [args.results]
    else:
        parser.print_help()
        return

    if not files:
        print("No result files found.")
        return

    all_records = []
    for f in files:
        print(f"Loading: {f}")
        records = load_results(f)
        all_records.extend(records)

    print(f"\nTotal records: {len(all_records)}")
    print(f"Conditions: {sorted(set(r.condition for r in all_records))}")
    print(f"Models: {sorted(set(r.model for r in all_records))}")

    descriptive_stats(all_records)

    try:
        pairwise_comparisons(all_records)
    except ImportError:
        print("\n  scipy not installed. Skipping pairwise.")

    interaction_analysis(all_records)
    mixed_effects_analysis(all_records)

    try:
        bootstrap_ci(all_records)
    except Exception as e:
        print(f"\n  Bootstrap failed: {e}")

    if args.write_results:
        write_results_summary(all_records, EXP2_DIR / "RESULTS.md")


if __name__ == "__main__":
    main()
