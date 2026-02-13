"""
Exp 1: Token Efficiency — Statistical Analysis Pipeline

Implements the dual-track analysis plan from DEVIATION.md:
- Track A (Confirmatory): prereg-faithful elements
- Track B (Exploratory): expanded atomic elements
- Secondary: raw token counts (prereg model)

Usage:
    python3 experiments/exp1_token_efficiency/analysis/analyze.py --results <scored_json>
    python3 experiments/exp1_token_efficiency/analysis/analyze.py --results-dir results/
    python3 experiments/exp1_token_efficiency/analysis/analyze.py --all
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from dataclasses import dataclass

import numpy as np

EXP1_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = EXP1_DIR / "results"

CONDITIONS = [
    "free_english", "structured_english", "instruction_matched_english",
    "json_fc", "fipa_acl", "axon",
]

COMPLEXITY_MAP = {"L1": 1, "L2": 2, "L3": 3}


@dataclass
class AnalysisRecord:
    task_id: str
    condition: str
    model: str
    run_number: int
    complexity_level: int
    tokens_cl100k: int
    tokens_o200k: int
    elements_present: int
    elements_total: int
    tokens_per_unit: float | None  # None if elements_present == 0
    log_tokens_per_unit: float | None
    valid: bool


def load_scored_results(path: Path) -> list[dict]:
    with open(path) as f:
        data = json.load(f)
    return data["results"]


def build_records(scored_results: list[dict]) -> list[AnalysisRecord]:
    """Convert scored JSON results to analysis records."""
    records = []
    for r in scored_results:
        task_id = r["task_id"]
        level_str = task_id.split("-")[0]  # L1, L2, L3
        complexity = COMPLEXITY_MAP.get(level_str, 0)

        tc = r.get("token_counts") or {}
        cl100k = tc.get("cl100k_base", 0)
        o200k = tc.get("o200k_base", 0)

        ep = r["element_count_present"]
        tpu = r.get("tokens_per_unit")
        log_tpu = math.log(tpu) if tpu and tpu > 0 else None

        records.append(AnalysisRecord(
            task_id=task_id,
            condition=r["condition"],
            model=r["model"],
            run_number=r["run_number"],
            complexity_level=complexity,
            tokens_cl100k=cl100k,
            tokens_o200k=o200k,
            elements_present=ep,
            elements_total=r["element_count_total"],
            tokens_per_unit=tpu,
            log_tokens_per_unit=log_tpu,
            valid=r["valid"],
        ))
    return records


# ── Descriptive Statistics ───────────────────────────────────────────


def descriptive_stats(records: list[AnalysisRecord]):
    """Print descriptive statistics by condition."""
    print("\n" + "=" * 80)
    print("DESCRIPTIVE STATISTICS")
    print("=" * 80)

    # Raw tokens
    print(f"\n{'Condition':<28} {'N':>5} {'Tok(cl100k)':>12} {'Tok(o200k)':>12} "
          f"{'Elem':>6} {'Tok/Unit':>10}")
    print("-" * 75)
    for cond in CONDITIONS:
        cr = [r for r in records if r.condition == cond]
        if not cr:
            continue
        n = len(cr)
        mean_cl = np.mean([r.tokens_cl100k for r in cr])
        mean_o2 = np.mean([r.tokens_o200k for r in cr])
        mean_elem = np.mean([r.elements_present for r in cr])
        tpu_vals = [r.tokens_per_unit for r in cr if r.tokens_per_unit is not None]
        mean_tpu = np.mean(tpu_vals) if tpu_vals else float("nan")
        print(f"  {cond:<26} {n:>5} {mean_cl:>12.1f} {mean_o2:>12.1f} "
              f"{mean_elem:>6.1f} {mean_tpu:>10.2f}")

    # By complexity
    print(f"\n{'Level':<28} {'N':>5} {'Tok/Unit(mean)':>15} {'Tok/Unit(sd)':>13}")
    print("-" * 65)
    for level_name, level_num in COMPLEXITY_MAP.items():
        lr = [r for r in records if r.complexity_level == level_num]
        if not lr:
            continue
        tpu_vals = [r.tokens_per_unit for r in lr if r.tokens_per_unit is not None]
        if tpu_vals:
            print(f"  {level_name:<26} {len(lr):>5} {np.mean(tpu_vals):>15.2f} "
                  f"{np.std(tpu_vals):>13.2f}")

    # Zero-element count
    zeros = [r for r in records if r.elements_present == 0]
    print(f"\n  Zero-element outputs: {len(zeros)} / {len(records)}")
    if zeros:
        for r in zeros:
            print(f"    [{r.task_id}] {r.condition} {r.model} run#{r.run_number}")


# ── Two-Part Analysis ────────────────────────────────────────────────


def two_part_analysis(records: list[AnalysisRecord]):
    """Part 1: P(complete failure). Part 2: tokens/unit | elements > 0."""
    print("\n" + "=" * 80)
    print("TWO-PART ANALYSIS")
    print("=" * 80)

    # Part 1: failure rate by condition
    print("\nPart 1: P(elements = 0) by condition")
    print(f"  {'Condition':<28} {'Failures':>9} {'Total':>6} {'Rate':>7}")
    print("  " + "-" * 52)
    for cond in CONDITIONS:
        cr = [r for r in records if r.condition == cond]
        failures = sum(1 for r in cr if r.elements_present == 0)
        total = len(cr)
        rate = failures / total if total > 0 else 0
        print(f"  {cond:<28} {failures:>9} {total:>6} {rate:>7.1%}")

    # Part 2: conditional analysis
    valid_records = [r for r in records if r.tokens_per_unit is not None]
    print(f"\nPart 2: tokens/unit conditional on elements > 0 (N={len(valid_records)})")
    print(f"  {'Condition':<28} {'N':>5} {'Mean':>10} {'SD':>10} {'Median':>10}")
    print("  " + "-" * 65)
    for cond in CONDITIONS:
        cr = [r for r in valid_records if r.condition == cond]
        if not cr:
            continue
        vals = [r.tokens_per_unit for r in cr]
        print(f"  {cond:<28} {len(cr):>5} {np.mean(vals):>10.2f} "
              f"{np.std(vals):>10.2f} {np.median(vals):>10.2f}")


# ── Mixed-Effects Model ──────────────────────────────────────────────


def mixed_effects_analysis(records: list[AnalysisRecord], outcome: str = "log_tpu"):
    """Run mixed-effects model. Requires statsmodels."""
    valid = [r for r in records if r.tokens_per_unit is not None]
    if not valid:
        print("\n  No valid records for mixed-effects analysis.")
        return

    try:
        import pandas as pd
        import statsmodels.formula.api as smf
    except ImportError:
        print("\n  statsmodels/pandas not installed. Skipping mixed-effects model.")
        print("  Install: pip install statsmodels pandas")
        return

    print("\n" + "=" * 80)
    if outcome == "log_tpu":
        print("MIXED-EFFECTS MODEL — log(tokens_per_unit) [Primary]")
    elif outcome == "raw_tokens":
        print("MIXED-EFFECTS MODEL — raw tokens [Secondary, prereg-faithful]")
    print("=" * 80)

    # Build dataframe
    df = pd.DataFrame([{
        "log_tpu": r.log_tokens_per_unit,
        "tpu": r.tokens_per_unit,
        "tokens": r.tokens_cl100k,
        "condition": r.condition,
        "complexity": f"L{r.complexity_level}",
        "task": r.task_id,
        "model": r.model,
    } for r in valid])

    # Set AXON as reference
    df["condition"] = pd.Categorical(df["condition"], categories=CONDITIONS)

    if outcome == "log_tpu":
        formula = "log_tpu ~ C(condition, Treatment(reference='axon')) + C(complexity)"
        y_col = "log_tpu"
    else:
        formula = "tokens ~ C(condition, Treatment(reference='axon')) + C(complexity)"
        y_col = "tokens"

    try:
        model = smf.mixedlm(
            formula, df, groups=df["model"],
            re_formula="1", vc_formula={"task": "0 + C(task)"}
        )
        result = model.fit(reml=True)
        print(f"\n{result.summary()}")
    except Exception as e:
        # Fallback: simpler model without variance components
        print(f"\n  Full model failed ({e}), trying simplified model...")
        try:
            model = smf.mixedlm(formula, df, groups=df["task"])
            result = model.fit(reml=True)
            print(f"\n{result.summary()}")
        except Exception as e2:
            print(f"\n  Simplified model also failed: {e2}")
            print("  Falling back to descriptive pairwise comparisons only.")


# ── Pairwise Comparisons ─────────────────────────────────────────────


def pairwise_comparisons(records: list[AnalysisRecord]):
    """AXON vs each condition with Holm-Bonferroni correction."""
    from scipy import stats

    valid = [r for r in records if r.tokens_per_unit is not None]
    axon_vals = [r.tokens_per_unit for r in valid if r.condition == "axon"]

    if not axon_vals:
        print("\n  No valid AXON records for pairwise comparisons.")
        return

    print("\n" + "=" * 80)
    print("PAIRWISE COMPARISONS — AXON vs each condition")
    print("=" * 80)

    comparisons = []
    other_conditions = [c for c in CONDITIONS if c != "axon"]

    for cond in other_conditions:
        cond_vals = [r.tokens_per_unit for r in valid if r.condition == cond]
        if not cond_vals:
            continue

        # Two-sample t-test (Welch's)
        t_stat, p_value = stats.ttest_ind(axon_vals, cond_vals, equal_var=False)

        # Cohen's d
        pooled_std = math.sqrt(
            (np.std(axon_vals, ddof=1)**2 + np.std(cond_vals, ddof=1)**2) / 2
        )
        cohens_d = (np.mean(axon_vals) - np.mean(cond_vals)) / pooled_std if pooled_std > 0 else 0

        comparisons.append({
            "condition": cond,
            "axon_mean": np.mean(axon_vals),
            "cond_mean": np.mean(cond_vals),
            "diff": np.mean(axon_vals) - np.mean(cond_vals),
            "cohens_d": cohens_d,
            "t_stat": t_stat,
            "p_uncorrected": p_value,
        })

    # Holm-Bonferroni correction
    comparisons.sort(key=lambda x: x["p_uncorrected"])
    n_comparisons = len(comparisons)
    for i, comp in enumerate(comparisons):
        correction_factor = n_comparisons - i
        comp["p_corrected"] = min(comp["p_uncorrected"] * correction_factor, 1.0)
        comp["significant"] = comp["p_corrected"] < 0.05

    # Print results
    print(f"\n  {'Comparison':<35} {'Diff':>8} {'d':>7} {'p(raw)':>9} "
          f"{'p(HB)':>9} {'Sig':>5}")
    print("  " + "-" * 75)
    for comp in sorted(comparisons, key=lambda x: CONDITIONS.index(x["condition"])):
        label = f"AXON vs {comp['condition']}"
        sig = "*" if comp["significant"] else ""
        print(f"  {label:<35} {comp['diff']:>8.2f} {comp['cohens_d']:>7.2f} "
              f"{comp['p_uncorrected']:>9.4f} {comp['p_corrected']:>9.4f} {sig:>5}")

    print(f"\n  AXON mean tok/unit: {np.mean(axon_vals):.2f} "
          f"(N={len(axon_vals)})")


# ── Bootstrap Confidence Intervals ───────────────────────────────────


def bootstrap_ci(records: list[AnalysisRecord], n_boot: int = 10000, seed: int = 42):
    """Block bootstrap CIs at task x model level."""
    rng = np.random.default_rng(seed)
    valid = [r for r in records if r.tokens_per_unit is not None]

    if not valid:
        print("\n  No valid records for bootstrap.")
        return

    print("\n" + "=" * 80)
    print(f"BOOTSTRAP CONFIDENCE INTERVALS (n={n_boot}, block: task x model)")
    print("=" * 80)

    # Group by (task, model) blocks
    blocks = {}
    for r in valid:
        key = (r.task_id, r.model)
        blocks.setdefault(key, []).append(r)

    block_keys = list(blocks.keys())
    n_blocks = len(block_keys)

    # For each condition pair, compute bootstrap distribution of mean difference
    axon_vals_by_block = {}
    for key in block_keys:
        axon_in_block = [r.tokens_per_unit for r in blocks[key] if r.condition == "axon"]
        if axon_in_block:
            axon_vals_by_block[key] = np.mean(axon_in_block)

    other_conditions = [c for c in CONDITIONS if c != "axon"]

    print(f"\n  {'Comparison':<35} {'d':>7} {'95% CI':>20}")
    print("  " + "-" * 65)

    for cond in other_conditions:
        boot_diffs = []
        for _ in range(n_boot):
            # Resample blocks with replacement
            sampled_keys = rng.choice(block_keys, size=n_blocks, replace=True)
            axon_boot = []
            cond_boot = []
            for key in sampled_keys:
                for r in blocks[key]:
                    if r.condition == "axon" and r.tokens_per_unit is not None:
                        axon_boot.append(r.tokens_per_unit)
                    elif r.condition == cond and r.tokens_per_unit is not None:
                        cond_boot.append(r.tokens_per_unit)

            if axon_boot and cond_boot:
                pooled_std = math.sqrt(
                    (np.std(axon_boot, ddof=1)**2 + np.std(cond_boot, ddof=1)**2) / 2
                )
                if pooled_std > 0:
                    d = (np.mean(axon_boot) - np.mean(cond_boot)) / pooled_std
                    boot_diffs.append(d)

        if boot_diffs:
            boot_arr = np.array(boot_diffs)
            ci_lo = np.percentile(boot_arr, 2.5)
            ci_hi = np.percentile(boot_arr, 97.5)
            d_obs = np.mean(boot_arr)
            label = f"AXON vs {cond}"
            print(f"  {label:<35} {d_obs:>7.2f} [{ci_lo:>8.2f}, {ci_hi:>8.2f}]")
        else:
            print(f"  AXON vs {cond:<24} insufficient data")


# ── Prompt Overhead ──────────────────────────────────────────────────


def prompt_overhead_analysis():
    """Report prompt token counts and breakeven analysis."""
    PROJECT_ROOT = EXP1_DIR.parent.parent
    PROMPTS_DIR = PROJECT_ROOT / "experiments" / "exp0_learnability" / "prompts"

    print("\n" + "=" * 80)
    print("PROMPT OVERHEAD ANALYSIS")
    print("=" * 80)

    try:
        sys.path.insert(0, str(PROJECT_ROOT / "experiments"))
        from lib.token_counter import count_tokens_multi
    except ImportError:
        print("  tiktoken not available. Skipping prompt overhead.")
        return

    prompt_files = {
        "free_english": "free_english.txt",
        "structured_english": "structured_english.txt",
        "instruction_matched_english": "instruction_matched_english.txt",
        "json_fc": "json_fc.txt",
        "fipa_acl": "fipa_acl.txt",
        "axon": "axon.txt",
    }

    prompt_tokens = {}
    print(f"\n  {'Condition':<28} {'cl100k':>8} {'o200k':>8} {'Chars':>8}")
    print("  " + "-" * 55)
    for cond, filename in prompt_files.items():
        path = PROMPTS_DIR / filename
        if path.exists():
            text = path.read_text()
            counts = count_tokens_multi(text)
            prompt_tokens[cond] = counts
            print(f"  {cond:<28} {counts['cl100k_base']:>8} "
                  f"{counts['o200k_base']:>8} {len(text):>8}")

    # Breakeven analysis
    if "axon" in prompt_tokens and prompt_tokens:
        axon_prompt = prompt_tokens["axon"]["cl100k_base"]
        print(f"\n  Breakeven analysis (cl100k_base):")
        print(f"  AXON prompt overhead: {axon_prompt} tokens")
        for cond in CONDITIONS:
            if cond == "axon" or cond not in prompt_tokens:
                continue
            other_prompt = prompt_tokens[cond]["cl100k_base"]
            overhead_diff = axon_prompt - other_prompt
            if overhead_diff > 0:
                print(f"  vs {cond}: +{overhead_diff} prompt tokens "
                      f"(need per-msg savings to amortize)")
            else:
                print(f"  vs {cond}: {overhead_diff} prompt tokens (AXON prompt is smaller)")


# ── Main ─────────────────────────────────────────────────────────────


def run_analysis(results_paths: list[Path]):
    """Run full analysis pipeline on scored results."""
    all_records = []
    for path in results_paths:
        scored = load_scored_results(path)
        records = build_records(scored)
        all_records.extend(records)
        print(f"Loaded {len(records)} records from {path.name}")

    if not all_records:
        print("No records to analyze.")
        return

    track = all_records[0].task_id  # Just for labeling
    print(f"\nTotal records: {len(all_records)}")
    print(f"Models: {sorted(set(r.model for r in all_records))}")
    print(f"Conditions: {sorted(set(r.condition for r in all_records))}")

    # Run all analyses
    descriptive_stats(all_records)
    two_part_analysis(all_records)
    pairwise_comparisons(all_records)
    bootstrap_ci(all_records)
    prompt_overhead_analysis()

    # Mixed-effects models
    mixed_effects_analysis(all_records, outcome="log_tpu")
    mixed_effects_analysis(all_records, outcome="raw_tokens")


def main():
    parser = argparse.ArgumentParser(description="Exp 1: Statistical Analysis")
    parser.add_argument("--results", type=Path, nargs="+",
                        help="Scored result JSON file(s)")
    parser.add_argument("--results-dir", type=Path,
                        help="Directory containing scored results")
    parser.add_argument("--all", action="store_true",
                        help="Analyze all results in default results dir")
    args = parser.parse_args()

    if args.all:
        paths = sorted(RESULTS_DIR.glob("exp1_scored_*.json"))
    elif args.results_dir:
        paths = sorted(args.results_dir.glob("exp1_scored_*.json"))
    elif args.results:
        paths = args.results
    else:
        print("Specify --results, --results-dir, or --all")
        return

    if not paths:
        print("No scored result files found.")
        return

    run_analysis(paths)


if __name__ == "__main__":
    main()
