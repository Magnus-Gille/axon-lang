#!/usr/bin/env python3
"""
Benchmark C: Methodology Rigor Audit

10-item research methodology rubric scored 0-2 for both AXON and AISP.
Items drawn from standard research methodology checklists.

Usage:
    python3 experiments/exp_aisp_comparison/benchmark_c_methodology.py
"""

from __future__ import annotations

import json
from pathlib import Path


RUBRIC = [
    {
        "id": 1,
        "item": "Pre-registration",
        "scoring": {
            0: "None",
            1: "Informal plan",
            2: "Formal pre-registration with frozen analysis plan",
        },
        "axon": {
            "score": 2,
            "justification": "PREREGISTRATION.md frozen before data collection (2026-02-12). "
                             "Includes hypotheses, conditions, metrics, sample sizes, and analysis plan.",
            "evidence": "experiments/PREREGISTRATION.md",
        },
        "aisp": {
            "score": 0,
            "justification": "No pre-registration exists. No analysis plan documented.",
            "evidence": "Repository contains zero experimental methodology files.",
        },
    },
    {
        "id": 2,
        "item": "Controlled comparison",
        "scoring": {
            0: "None",
            1: "Single baseline",
            2: "Multiple controlled baselines",
        },
        "axon": {
            "score": 2,
            "justification": "5 controlled baselines: free English, structured English, "
                             "instruction-matched English, JSON function calling, FIPA-ACL.",
            "evidence": "experiments/PREREGISTRATION.md, experiments/lib/condition_adapter.py",
        },
        "aisp": {
            "score": 0,
            "justification": "Comparison only to undefined 'traditional prose'. "
                             "No controlled baselines, no baseline definition.",
            "evidence": "README.md comparison table references 'Traditional Approach' without specification.",
        },
    },
    {
        "id": 3,
        "item": "Blinding",
        "scoring": {
            0: "None",
            1: "Partial blinding",
            2: "Full blinding (judges don't know condition)",
        },
        "axon": {
            "score": 2,
            "justification": "FAIRNESS.md specifies judges don't see condition labels. "
                             "Outputs presented without format identification.",
            "evidence": "experiments/FAIRNESS.md",
        },
        "aisp": {
            "score": 0,
            "justification": "No evaluation procedure exists to blind. "
                             "All 'evidence' is self-reported by the project author.",
            "evidence": "evidence/ directory contains no evaluation methodology.",
        },
    },
    {
        "id": 4,
        "item": "Multiple models",
        "scoring": {
            0: "None",
            1: "1 model",
            2: "3+ models",
        },
        "axon": {
            "score": 2,
            "justification": "3 models tested: Claude Haiku, Claude Sonnet, Codex (gpt-5.3-codex). "
                             "Results reported per model and aggregated.",
            "evidence": "experiments/exp1_token_efficiency/RESULTS.md",
        },
        "aisp": {
            "score": 0,
            "justification": "No experiments conducted with any model. "
                             "Claims do not reference specific model evaluations.",
            "evidence": "No experimental data in repository.",
        },
    },
    {
        "id": 5,
        "item": "Replication",
        "scoring": {
            0: "None",
            1: "2 runs",
            2: "3+ runs per cell",
        },
        "axon": {
            "score": 2,
            "justification": "3 runs per cell in Exp 1 (486 total = 6 conditions × 3 models × 9 tasks × 3 runs). "
                             "Exp 0 replicated 3 times.",
            "evidence": "experiments/exp0_learnability/RESULTS.md, experiments/exp1_token_efficiency/RESULTS.md",
        },
        "aisp": {
            "score": 0,
            "justification": "No experiments to replicate.",
            "evidence": "No experimental infrastructure in repository.",
        },
    },
    {
        "id": 6,
        "item": "Statistical analysis",
        "scoring": {
            0: "None",
            1: "Descriptive only",
            2: "Inferential with multiple comparison correction",
        },
        "axon": {
            "score": 2,
            "justification": "Welch's t-test, Holm-Bonferroni correction for 5 pairwise comparisons, "
                             "Cohen's d effect sizes, block bootstrap CIs, mixed-effects models.",
            "evidence": "experiments/exp1_token_efficiency/analysis/analyze.py",
        },
        "aisp": {
            "score": 0,
            "justification": "No statistical analysis. The '97x' claim is a mathematical derivation "
                             "from assumed (not measured) per-step accuracy rates.",
            "evidence": "reference.md contains the 97x derivation: (0.98^10)/(0.62^10).",
        },
    },
    {
        "id": 7,
        "item": "Adversarial review",
        "scoring": {
            0: "None",
            1: "Self-review",
            2: "Structured cross-model adversarial review",
        },
        "axon": {
            "score": 2,
            "justification": "Structured Claude↔Codex adversarial debates. ~100 critique points raised, "
                             "~85% resolved. Self-review ablation tracked. Debate transcripts preserved.",
            "evidence": "debate/ directory contains 15+ debate summaries with structured metadata.",
        },
        "aisp": {
            "score": 0,
            "justification": "No review process documented. Single contributor, no code review, "
                             "no external critique.",
            "evidence": "Repository has 7 commits by 1 contributor, 0 merged PRs.",
        },
    },
    {
        "id": 8,
        "item": "Fairness protocol",
        "scoring": {
            0: "None",
            1: "Informal considerations",
            2: "Documented protocol with specific constraints",
        },
        "axon": {
            "score": 2,
            "justification": "FAIRNESS.md: symmetric prompt budgets (8:1 max ratio), metadata equivalence, "
                             "3-judge panel, human validation subset, blinding protocol.",
            "evidence": "experiments/FAIRNESS.md",
        },
        "aisp": {
            "score": 0,
            "justification": "No fairness considerations documented. Comparison to undefined baseline "
                             "with no attempt to control for confounds.",
            "evidence": "No methodology documentation in repository.",
        },
    },
    {
        "id": 9,
        "item": "Quantified claims with CIs",
        "scoring": {
            0: "None",
            1: "Point estimates only",
            2: "Effect sizes with confidence intervals",
        },
        "axon": {
            "score": 2,
            "justification": "Primary claim: '~32% better tok/unit vs JSON FC' with Cohen's d=-0.43, "
                             "95% bootstrap CI [-0.73, -0.13]. All pairwise comparisons include CIs.",
            "evidence": "experiments/exp1_token_efficiency/RESULTS.md (statistical analysis output)",
        },
        "aisp": {
            "score": 0,
            "justification": "Claims are unquantified assertions ('97x improvement') derived from assumed "
                             "base rates. No confidence intervals, no effect sizes, no sample sizes.",
            "evidence": "README.md, evidence/README.md — no statistical measures reported.",
        },
    },
    {
        "id": 10,
        "item": "Negative result commitment",
        "scoring": {
            0: "None",
            1: "Implied",
            2: "Explicit pre-commitment to publish null results",
        },
        "axon": {
            "score": 2,
            "justification": "PREREGISTRATION.md includes explicit commitment: 'If AXON does not "
                             "outperform baselines, results will be reported as-is.'",
            "evidence": "experiments/PREREGISTRATION.md",
        },
        "aisp": {
            "score": 0,
            "justification": "No experimental framework exists to produce null results. "
                             "Evidence directory contains placeholder data and unsupported claims.",
            "evidence": "evidence/tic-tac-toe/analysis.md: 'Status: Placeholder — Full analysis data coming soon'",
        },
    },
]


def run_benchmark():
    """Score and display Benchmark C results."""
    print("=" * 80)
    print("BENCHMARK C: Methodology Rigor Audit")
    print("=" * 80)
    print("\n  10-item rubric, 0-2 per item, max 20 points\n")

    axon_total = 0
    aisp_total = 0

    print(f"  {'#':<3} {'Item':<30} {'AXON':>5} {'AISP':>5}")
    print("  " + "-" * 45)

    for item in RUBRIC:
        axon_score = item["axon"]["score"]
        aisp_score = item["aisp"]["score"]
        axon_total += axon_score
        aisp_total += aisp_score
        print(f"  {item['id']:<3} {item['item']:<30} {axon_score:>5} {aisp_score:>5}")

    print("  " + "-" * 45)
    print(f"  {'':>3} {'TOTAL':<30} {axon_total:>5} {aisp_total:>5}")
    print(f"  {'':>3} {'':>30} {'/ 20':>5} {'/ 20':>5}")

    # Detailed justifications
    print("\n\n  DETAILED JUSTIFICATIONS")
    print("  " + "=" * 70)
    for item in RUBRIC:
        print(f"\n  {item['id']}. {item['item']}")
        print(f"     Scoring: 0={item['scoring'][0]} | 1={item['scoring'][1]} | 2={item['scoring'][2]}")
        print(f"     AXON ({item['axon']['score']}/2): {item['axon']['justification']}")
        print(f"       Evidence: {item['axon']['evidence']}")
        print(f"     AISP ({item['aisp']['score']}/2): {item['aisp']['justification']}")
        print(f"       Evidence: {item['aisp']['evidence']}")

    # Interpretation
    print("\n\n  INTERPRETATION")
    print("  " + "=" * 70)
    print(f"  AXON: {axon_total}/20 — Meets all standard research methodology criteria")
    print(f"  AISP: {aisp_total}/20 — No standard research methodology applied")
    print()
    print("  The 20-point gap reflects a fundamental difference in approach:")
    print("  AXON is a research project with empirical methodology.")
    print("  AISP is a documentation/marketing project with aspirational claims.")
    print("  The rubric items are standard research methodology criteria")
    print("  (pre-registration, blinding, replication, etc.) that any project")
    print("  following standard methodology would score well on.")

    return {"axon_total": axon_total, "aisp_total": aisp_total, "rubric": RUBRIC}


def save_results(results: dict):
    """Save results to JSON."""
    out_path = Path(__file__).parent / "benchmark_c_results.json"
    serializable = {
        "axon_total": results["axon_total"],
        "aisp_total": results["aisp_total"],
        "max_score": 20,
        "items": [
            {
                "id": item["id"],
                "item": item["item"],
                "axon_score": item["axon"]["score"],
                "axon_justification": item["axon"]["justification"],
                "axon_evidence": item["axon"]["evidence"],
                "aisp_score": item["aisp"]["score"],
                "aisp_justification": item["aisp"]["justification"],
                "aisp_evidence": item["aisp"]["evidence"],
            }
            for item in results["rubric"]
        ],
    }
    with open(out_path, "w") as f:
        json.dump(serializable, f, indent=2)
    print(f"\n  Results saved to {out_path}")


def main():
    results = run_benchmark()
    save_results(results)


if __name__ == "__main__":
    main()
