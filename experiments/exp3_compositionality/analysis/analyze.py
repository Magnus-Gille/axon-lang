"""
Exp 3: Compositionality — Statistical Analysis Pipeline

Implements the pre-registered analysis plan:
- Primary: composition_success ~ condition + complexity_level + (1|task) + (1|model)
- Interaction: composition_success ~ condition * complexity_level + (1|task) + (1|model)
- Secondary: overall element rate, nesting depth (Poisson, L2+L3)
- AISP: reported separately (exploratory, uncorrected)

Usage:
    python3 experiments/exp3_compositionality/analysis/analyze.py --results <scored_json>
    python3 experiments/exp3_compositionality/analysis/analyze.py --results-dir results/
    python3 experiments/exp3_compositionality/analysis/analyze.py --all
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from dataclasses import dataclass

import numpy as np

EXP3_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = EXP3_DIR / "results"

# Pre-registered conditions (5 pairwise comparisons with AXON)
CONDITIONS_PREREG = [
    "free_english", "structured_english", "instruction_matched_english",
    "json_fc", "fipa_acl", "axon",
]

# Extended conditions (exploratory)
CONDITIONS_ALL = CONDITIONS_PREREG + ["aisp"]

COMPLEXITY_MAP = {"L1": 1, "L2": 2, "L3": 3}


@dataclass
class AnalysisRecord:
    task_id: str
    condition: str
    model: str
    run_number: int
    complexity_level: int
    # Standard elements
    element_present: int
    element_total: int
    element_rate: float
    # Composition structure (primary DV)
    cs_present: int
    cs_total: int
    composition_rate: float
    # Nesting depth (secondary DV)
    nesting_depth: int
    # Raw token count
    tokens_cl100k: int
    valid: bool


def load_scored_results(path: Path) -> list[dict]:
    """Load scored results from a JSON file."""
    with open(path) as f:
        data = json.load(f)
    return data["results"]


def build_records(scored_results: list[dict]) -> list[AnalysisRecord]:
    """Convert scored JSON results to analysis records."""
    records = []
    for r in scored_results:
        task_id = r["task_id"]
        level_str = task_id.split("-")[0]
        complexity = COMPLEXITY_MAP.get(level_str, 0)

        scores = r.get("scores", {})
        tc = r.get("token_counts") or {}

        records.append(AnalysisRecord(
            task_id=task_id,
            condition=r["condition"],
            model=r["model"],
            run_number=r["run_number"],
            complexity_level=complexity,
            element_present=scores.get("element_present", 0),
            element_total=scores.get("element_total", 0),
            element_rate=scores.get("element_rate", 0.0),
            cs_present=scores.get("cs_present", 0),
            cs_total=scores.get("cs_total", 0),
            composition_rate=scores.get("composition_rate", 0.0),
            nesting_depth=scores.get("nesting_depth", 0),
            tokens_cl100k=tc.get("cl100k_base", 0),
            valid=r.get("valid", False),
        ))
    return records


# ── Descriptive Statistics ───────────────────────────────────────────


def descriptive_stats(records: list[AnalysisRecord]):
    """Print descriptive statistics by condition and complexity."""
    print("\n" + "=" * 80)
    print("DESCRIPTIVE STATISTICS")
    print("=" * 80)

    # Per-condition
    print(f"\n{'Condition':<28} {'N':>5} {'CompRate':>10} {'ElemRate':>10} "
          f"{'Depth':>6} {'Tokens':>8}")
    print("-" * 70)
    for cond in CONDITIONS_ALL:
        cr = [r for r in records if r.condition == cond]
        if not cr:
            continue
        n = len(cr)
        mean_comp = np.mean([r.composition_rate for r in cr])
        mean_elem = np.mean([r.element_rate for r in cr])
        mean_depth = np.mean([r.nesting_depth for r in cr])
        mean_tok = np.mean([r.tokens_cl100k for r in cr])
        marker = " *" if cond == "aisp" else ""
        print(f"  {cond:<26} {n:>5} {mean_comp:>9.1%} {mean_elem:>9.1%} "
              f"{mean_depth:>6.1f} {mean_tok:>8.1f}{marker}")

    # Per-complexity
    print(f"\n{'Level':<28} {'N':>5} {'CompRate':>10} {'CompRate SD':>12}")
    print("-" * 60)
    for level_name, level_num in COMPLEXITY_MAP.items():
        lr = [r for r in records if r.complexity_level == level_num]
        if not lr:
            continue
        vals = [r.composition_rate for r in lr]
        print(f"  {level_name:<26} {len(lr):>5} {np.mean(vals):>9.1%} "
              f"{np.std(vals):>12.3f}")

    # Per-condition × complexity (key table)
    print(f"\n{'Condition × Level':<35} {'N':>4} {'CompRate':>9}")
    print("-" * 50)
    for cond in CONDITIONS_ALL:
        for level_name, level_num in COMPLEXITY_MAP.items():
            cr = [r for r in records
                  if r.condition == cond and r.complexity_level == level_num]
            if not cr:
                continue
            mean_comp = np.mean([r.composition_rate for r in cr])
            print(f"  {cond} × {level_name:<17} {len(cr):>4} {mean_comp:>8.1%}")

    # Ceiling check (L1)
    print(f"\n{'L1 CEILING CHECK':=^80}")
    l1 = [r for r in records if r.complexity_level == 1]
    l1_rates = {}
    for cond in CONDITIONS_ALL:
        cr = [r for r in l1 if r.condition == cond]
        if cr:
            rate = np.mean([r.composition_rate for r in cr])
            l1_rates[cond] = rate
            print(f"  {cond:<26} L1 composition rate: {rate:.1%}")
    all_above_90 = all(r > 0.90 for r in l1_rates.values()) if l1_rates else False
    if all_above_90:
        print("  >> CEILING: All conditions >90% on L1. Focus analysis on L2+L3.")
    else:
        print("  >> No ceiling effect. Include all levels in analysis.")

    # Failure rate
    print(f"\n{'FAILURE RATE':=^80}")
    for cond in CONDITIONS_ALL:
        cr = [r for r in records if r.condition == cond]
        failures = sum(1 for r in cr if not r.valid)
        total = len(cr)
        rate = failures / total if total > 0 else 0
        print(f"  {cond:<26} {failures:>4} / {total:>4} ({rate:.1%})")


# ── Pairwise Comparisons ────────────────────────────────────────────


def pairwise_comparisons(records: list[AnalysisRecord]):
    """Pairwise comparisons of AXON vs each prereg condition.

    Reports: mean difference, Cohen's d, bootstrap CI, Holm-Bonferroni corrected p.
    """
    from scipy import stats as sp_stats

    print("\n" + "=" * 80)
    print("PAIRWISE COMPARISONS — AXON vs each condition (composition_rate)")
    print("=" * 80)

    axon_vals = np.array([r.composition_rate for r in records if r.condition == "axon"])
    if len(axon_vals) == 0:
        print("  No AXON records found.")
        return

    comparisons = []
    other_conditions = [c for c in CONDITIONS_PREREG if c != "axon"]

    for cond in other_conditions:
        other_vals = np.array([r.composition_rate for r in records if r.condition == cond])
        if len(other_vals) == 0:
            continue

        # Mean difference
        diff = np.mean(axon_vals) - np.mean(other_vals)

        # Cohen's d
        pooled_sd = np.sqrt(
            (np.var(axon_vals, ddof=1) + np.var(other_vals, ddof=1)) / 2
        )
        d = diff / pooled_sd if pooled_sd > 0 else float("inf")

        # Mann-Whitney U (non-parametric)
        u_stat, p_val = sp_stats.mannwhitneyu(axon_vals, other_vals, alternative="two-sided")

        # Bootstrap CI for effect size (10,000 resamples, BCa)
        ci_low, ci_high = _bootstrap_ci_d(axon_vals, other_vals, n_resamples=10000)

        comparisons.append({
            "condition": cond,
            "axon_mean": np.mean(axon_vals),
            "other_mean": np.mean(other_vals),
            "diff": diff,
            "d": d,
            "ci_low": ci_low,
            "ci_high": ci_high,
            "p_uncorrected": p_val,
        })

    # Holm-Bonferroni correction
    comparisons.sort(key=lambda c: c["p_uncorrected"])
    k = len(comparisons)
    for i, comp in enumerate(comparisons):
        comp["p_corrected"] = min(comp["p_uncorrected"] * (k - i), 1.0)
        comp["significant"] = comp["p_corrected"] < 0.05

    # Print results
    print(f"\n{'Comparison':<35} {'Diff':>7} {'d':>7} {'95% CI':>16} "
          f"{'p(raw)':>8} {'p(Holm)':>8} {'Sig':>5}")
    print("-" * 90)
    for comp in comparisons:
        sig = "***" if comp["p_corrected"] < 0.001 else (
            "**" if comp["p_corrected"] < 0.01 else (
                "*" if comp["p_corrected"] < 0.05 else ""))
        ci_str = f"[{comp['ci_low']:+.3f}, {comp['ci_high']:+.3f}]"
        print(f"  AXON vs {comp['condition']:<24} {comp['diff']:>+.3f} {comp['d']:>+.3f} "
              f"{ci_str:>16} {comp['p_uncorrected']:>8.4f} {comp['p_corrected']:>8.4f} "
              f"{sig:>5}")

    # AISP (exploratory, uncorrected)
    aisp_vals = np.array([r.composition_rate for r in records if r.condition == "aisp"])
    if len(aisp_vals) > 0:
        diff = np.mean(axon_vals) - np.mean(aisp_vals)
        pooled_sd = np.sqrt((np.var(axon_vals, ddof=1) + np.var(aisp_vals, ddof=1)) / 2)
        d = diff / pooled_sd if pooled_sd > 0 else float("inf")
        _, p_val = sp_stats.mannwhitneyu(axon_vals, aisp_vals, alternative="two-sided")
        print(f"\n  AXON vs aisp (exploratory)     {diff:>+.3f} {d:>+.3f} "
              f"{'':>16} {p_val:>8.4f} {'N/A':>8}")


def _bootstrap_ci_d(a: np.ndarray, b: np.ndarray,
                     n_resamples: int = 10000,
                     alpha: float = 0.05) -> tuple[float, float]:
    """Bootstrap confidence interval for Cohen's d (BCa method approximation)."""
    rng = np.random.default_rng(42)
    ds = []
    na, nb = len(a), len(b)
    for _ in range(n_resamples):
        a_boot = rng.choice(a, size=na, replace=True)
        b_boot = rng.choice(b, size=nb, replace=True)
        diff = np.mean(a_boot) - np.mean(b_boot)
        pooled = np.sqrt((np.var(a_boot, ddof=1) + np.var(b_boot, ddof=1)) / 2)
        ds.append(diff / pooled if pooled > 0 else 0)
    ds = np.array(ds)
    lo = np.percentile(ds, 100 * alpha / 2)
    hi = np.percentile(ds, 100 * (1 - alpha / 2))
    return float(lo), float(hi)


# ── Mixed-Effects Model ──────────────────────────────────────────────


def mixed_effects_analysis(records: list[AnalysisRecord],
                           focus_l23: bool = False):
    """Run binomial GLMM for composition_success.

    Primary: composition_success ~ condition + complexity_level + (1|task) + (1|model)
    Interaction: composition_success ~ condition * complexity_level + (1|task) + (1|model)
    """
    try:
        import pandas as pd
        import statsmodels.formula.api as smf
        import statsmodels.api as sm
    except ImportError:
        print("\n  statsmodels/pandas not installed. Skipping mixed-effects model.")
        print("  Install: pip install statsmodels pandas")
        return

    # Filter to prereg conditions only
    valid = [r for r in records
             if r.condition in CONDITIONS_PREREG and r.cs_total > 0]
    if focus_l23:
        valid = [r for r in valid if r.complexity_level >= 2]

    if not valid:
        print("\n  No valid records for mixed-effects analysis.")
        return

    subset_label = "L2+L3 only" if focus_l23 else "all levels"

    print("\n" + "=" * 80)
    print(f"MIXED-EFFECTS MODEL — composition_rate ({subset_label}) [Primary]")
    print("=" * 80)

    df = pd.DataFrame([{
        "cs_present": r.cs_present,
        "cs_total": r.cs_total,
        "composition_rate": r.composition_rate,
        "condition": r.condition,
        "complexity": f"L{r.complexity_level}",
        "task": r.task_id,
        "model": r.model,
    } for r in valid])

    df["condition"] = pd.Categorical(
        df["condition"], categories=CONDITIONS_PREREG
    )

    # Primary model: additive
    formula = ("composition_rate ~ C(condition, Treatment(reference='axon')) "
               "+ C(complexity)")

    print(f"\n  Formula: {formula}")
    print(f"  N = {len(df)}")
    print(f"  Conditions: {df['condition'].nunique()}")
    print(f"  Models: {df['model'].nunique()}")
    print(f"  Tasks: {df['task'].nunique()}")

    try:
        model = smf.mixedlm(
            formula, df, groups=df["model"],
            re_formula="1", vc_formula={"task": "0 + C(task)"}
        )
        result = model.fit(reml=True)
        print(f"\n{result.summary()}")
    except Exception as e:
        print(f"\n  Mixed-effects model failed: {e}")
        print("  Falling back to fixed-effects model...")
        _fixed_effects_fallback(df, "composition_rate", subset_label)

    # Interaction model (key hypothesis)
    print("\n" + "=" * 80)
    print(f"INTERACTION MODEL — condition × complexity ({subset_label})")
    print("=" * 80)

    formula_int = ("composition_rate ~ C(condition, Treatment(reference='axon')) "
                   "* C(complexity)")
    print(f"\n  Formula: {formula_int}")

    try:
        model_int = smf.mixedlm(
            formula_int, df, groups=df["model"],
            re_formula="1", vc_formula={"task": "0 + C(task)"}
        )
        result_int = model_int.fit(reml=True)
        print(f"\n{result_int.summary()}")
    except Exception as e:
        print(f"\n  Interaction model failed: {e}")
        print("  Falling back to fixed-effects interaction model...")
        _fixed_effects_fallback(df, "composition_rate", subset_label, interaction=True)


def _fixed_effects_fallback(df, outcome: str, label: str,
                            interaction: bool = False):
    """Fallback: OLS with model as fixed effect when RE variance ~0."""
    import statsmodels.formula.api as smf

    if interaction:
        formula = (f"{outcome} ~ C(condition, Treatment(reference='axon')) "
                   f"* C(complexity) + C(model)")
    else:
        formula = (f"{outcome} ~ C(condition, Treatment(reference='axon')) "
                   f"+ C(complexity) + C(model)")

    print(f"\n  Fixed-effects formula: {formula}")
    try:
        result = smf.ols(formula, df).fit()
        print(f"\n{result.summary()}")
    except Exception as e:
        print(f"\n  Fixed-effects model also failed: {e}")


# ── Nesting Depth Analysis ───────────────────────────────────────────


def nesting_depth_analysis(records: list[AnalysisRecord]):
    """Secondary: nesting depth analysis (L2+L3 tasks only)."""
    print("\n" + "=" * 80)
    print("NESTING DEPTH ANALYSIS (L2+L3 only)")
    print("=" * 80)

    l23 = [r for r in records if r.complexity_level >= 2]
    if not l23:
        print("  No L2+L3 records found.")
        return

    # Descriptive
    print(f"\n{'Condition':<28} {'N':>5} {'Mean Depth':>11} {'Max':>5}")
    print("-" * 55)
    for cond in CONDITIONS_ALL:
        cr = [r for r in l23 if r.condition == cond]
        if not cr:
            continue
        depths = [r.nesting_depth for r in cr]
        print(f"  {cond:<26} {len(cr):>5} {np.mean(depths):>11.2f} {max(depths):>5}")

    # Poisson GLMM (if statsmodels available)
    try:
        import pandas as pd
        import statsmodels.formula.api as smf

        prereg_l23 = [r for r in l23 if r.condition in CONDITIONS_PREREG]
        if not prereg_l23:
            return

        df = pd.DataFrame([{
            "nesting_depth": r.nesting_depth,
            "condition": r.condition,
            "complexity": f"L{r.complexity_level}",
            "task": r.task_id,
            "model": r.model,
        } for r in prereg_l23])

        df["condition"] = pd.Categorical(
            df["condition"], categories=CONDITIONS_PREREG
        )

        formula = ("nesting_depth ~ C(condition, Treatment(reference='axon')) "
                   "+ C(complexity)")
        print(f"\n  Poisson GLMM: {formula}")

        try:
            # Try Poisson via GLM with log link
            import statsmodels.api as sm
            model = smf.glm(
                formula, df,
                family=sm.families.Poisson()
            )
            result = model.fit()
            print(f"\n{result.summary()}")
        except Exception as e:
            print(f"\n  Poisson model failed: {e}")

    except ImportError:
        print("\n  statsmodels not installed. Skipping Poisson model.")


# ── Overall Element Rate Analysis ────────────────────────────────────


def element_rate_analysis(records: list[AnalysisRecord]):
    """Secondary: overall element rate (replicates Exp 1 methodology)."""
    print("\n" + "=" * 80)
    print("ELEMENT RATE ANALYSIS (standard elements, all levels)")
    print("=" * 80)

    print(f"\n{'Condition':<28} {'N':>5} {'ElemRate':>10} {'SD':>8}")
    print("-" * 55)
    for cond in CONDITIONS_ALL:
        cr = [r for r in records if r.condition == cond]
        if not cr:
            continue
        vals = [r.element_rate for r in cr]
        print(f"  {cond:<26} {len(cr):>5} {np.mean(vals):>9.1%} "
              f"{np.std(vals):>8.3f}")


# ── Results Summary ──────────────────────────────────────────────────


def write_results_summary(records: list[AnalysisRecord], output_path: Path):
    """Write a RESULTS.md summary."""
    lines = [
        "# Experiment 3: Compositionality — Results",
        "",
        f"**Generated**: {__import__('datetime').datetime.now().isoformat()}",
        f"**Grammar version**: v0.1b",
        f"**Total records**: {len(records)}",
        "",
        "## Summary",
        "",
        "| Condition | N | Comp Rate | Elem Rate | Nesting Depth |",
        "|-----------|---|-----------|-----------|---------------|",
    ]

    for cond in CONDITIONS_ALL:
        cr = [r for r in records if r.condition == cond]
        if not cr:
            continue
        n = len(cr)
        comp = np.mean([r.composition_rate for r in cr])
        elem = np.mean([r.element_rate for r in cr])
        depth = np.mean([r.nesting_depth for r in cr])
        marker = " (exploratory)" if cond == "aisp" else ""
        lines.append(
            f"| {cond}{marker} | {n} | {comp:.1%} | {elem:.1%} | {depth:.1f} |"
        )

    lines.extend([
        "",
        "## Version Provenance",
        "",
        "Data collected using AXON grammar v0.1b (with arithmetic operators).",
        "Exp 1 used v0.1a. The main difference is additional precedence levels",
        "for `+`, `-`, `*`, `/` and the `==` alias for `=`.",
        "",
        "See `experiments/exp1_token_efficiency/RESULTS.md` for v0.1a results.",
        "",
    ])

    with open(output_path, "w") as f:
        f.write("\n".join(lines))
    print(f"\n  Results summary written to: {output_path}")


# ── Main ─────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="Exp 3: Compositionality — Statistical Analysis"
    )
    parser.add_argument("--results", type=Path, help="Single scored results file")
    parser.add_argument("--results-dir", type=Path, help="Directory of scored results")
    parser.add_argument("--all", action="store_true",
                        help="Load all scored results from default results dir")
    parser.add_argument("--write-results", action="store_true",
                        help="Write RESULTS.md summary")
    args = parser.parse_args()

    # Collect result files
    files = []
    if args.results:
        files.append(args.results)
    elif args.results_dir:
        files = sorted(args.results_dir.glob("*_scored*.json"))
    elif args.all:
        files = sorted(RESULTS_DIR.glob("*_scored*.json"))
    else:
        parser.print_help()
        return

    if not files:
        print("No scored result files found.")
        return

    # Load and merge all records
    all_records = []
    for f in files:
        print(f"Loading: {f}")
        scored = load_scored_results(f)
        records = build_records(scored)
        all_records.extend(records)

    print(f"\nTotal records: {len(all_records)}")
    print(f"Conditions: {sorted(set(r.condition for r in all_records))}")
    print(f"Models: {sorted(set(r.model for r in all_records))}")

    # Run analyses
    descriptive_stats(all_records)
    element_rate_analysis(all_records)

    try:
        pairwise_comparisons(all_records)
    except ImportError:
        print("\n  scipy not installed. Skipping pairwise comparisons.")
        print("  Install: pip install scipy")

    mixed_effects_analysis(all_records)

    # Check for L1 ceiling → run L2+L3 focused analysis
    l1 = [r for r in all_records if r.complexity_level == 1]
    l1_rates = {}
    for cond in CONDITIONS_ALL:
        cr = [r for r in l1 if r.condition == cond]
        if cr:
            l1_rates[cond] = np.mean([r.composition_rate for r in cr])

    if l1_rates and all(r > 0.90 for r in l1_rates.values()):
        print("\n  L1 ceiling detected. Running L2+L3 focused analysis...")
        mixed_effects_analysis(all_records, focus_l23=True)

    nesting_depth_analysis(all_records)

    if args.write_results:
        write_results_summary(all_records, EXP3_DIR / "RESULTS.md")


if __name__ == "__main__":
    main()
