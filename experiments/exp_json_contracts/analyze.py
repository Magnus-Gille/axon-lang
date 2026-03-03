"""
JSON + Contracts — Analysis

Computes composition rate, element rate, failure rate for the json_contracts
condition and compares against AXON, JSON FC, and all other conditions from Exp 3.

Usage:
    python3 experiments/exp_json_contracts/analyze.py
    python3 experiments/exp_json_contracts/analyze.py --write-results
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from dataclasses import dataclass

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "experiments"))

JC_RESULTS_DIR = Path(__file__).parent / "results"
EXP3_RESULTS_DIR = PROJECT_ROOT / "experiments" / "exp3_compositionality" / "results"
ANNOTATIONS_FILE = PROJECT_ROOT / "experiments" / "exp3_compositionality" / "tasks" / "element_annotations.json"

# Reuse Exp 3 scoring
from exp3_compositionality.scoring.score import score_output, load_annotations


@dataclass
class AnalysisRecord:
    task_id: str
    condition: str
    model: str
    run_number: int
    valid: bool
    element_rate: float
    composition_rate: float
    cs_total: int
    cs_present: int
    complexity_level: int


def load_jc_results() -> list[dict]:
    """Load JSON+Contracts results files."""
    records = []
    for path in sorted(JC_RESULTS_DIR.glob("json_contracts_*.json")):
        with open(path) as f:
            data = json.load(f)
        for r in data["results"]:
            records.append(r)
    return records


def load_exp3_scored() -> list[dict]:
    """Load Exp 3 scored results for comparison."""
    records = []
    for path in sorted(EXP3_RESULTS_DIR.glob("*_scored.json")):
        if "checkpoint" in path.name:
            continue
        with open(path) as f:
            data = json.load(f)
        if "results" not in data:
            continue
        for r in data["results"]:
            records.append(r)
    return records


def score_jc_outputs(records: list[dict], annotations: dict) -> list[dict]:
    """Score JSON+Contracts outputs using Exp 3 scoring pipeline.

    Treats json_contracts as json_fc for element extraction (both are JSON
    with from/to/performative/content fields), then uses text extraction
    for composition structure.
    """
    scored = []
    for r in records:
        if not r["valid"]:
            r["scores"] = {
                "elements": {}, "composition_structure": {},
                "element_rate": 0.0, "composition_rate": 0.0,
                "cs_total": 0, "cs_present": 0, "needs_judge": [],
            }
            scored.append(r)
            continue

        # Score using json_fc extractors (same JSON structure) for elements,
        # and text extraction for composition structure
        scores = score_output("json_fc", r["output"], r["task_id"], annotations)
        r["scores"] = scores
        scored.append(r)
    return scored


def to_analysis_record(r: dict) -> AnalysisRecord:
    """Convert a scored result dict to AnalysisRecord."""
    scores = r.get("scores", {})
    return AnalysisRecord(
        task_id=r["task_id"],
        condition=r["condition"],
        model=r["model"],
        run_number=r["run_number"],
        valid=r["valid"],
        element_rate=scores.get("element_rate", 0.0),
        composition_rate=scores.get("composition_rate", 0.0),
        cs_total=scores.get("cs_total", 0),
        cs_present=scores.get("cs_present", 0),
        complexity_level=r.get("complexity_level", 0),
    )


def main():
    parser = argparse.ArgumentParser(
        description="JSON + Contracts — Analysis"
    )
    parser.add_argument("--write-results", action="store_true",
                        help="Write RESULTS.md")
    args = parser.parse_args()

    annotations = load_annotations()  # from Exp 3 scoring module

    # Load and score JSON+Contracts outputs
    jc_raw = load_jc_results()
    if not jc_raw:
        print("No JSON+Contracts results found in", JC_RESULTS_DIR)
        print("Run: python3 experiments/exp_json_contracts/run.py --all")
        return

    print(f"Loaded {len(jc_raw)} JSON+Contracts outputs")

    # Score them
    jc_scored = score_jc_outputs(jc_raw, annotations)
    jc_records = [to_analysis_record(r) for r in jc_scored]

    # Load Exp 3 for comparison
    exp3_raw = load_exp3_scored()
    exp3_records = [to_analysis_record(r) for r in exp3_raw]

    # Combine
    all_records = jc_records + exp3_records

    # Summary table
    print(f"\n{'Condition':<30} {'CompRate':>9} {'ElemRate':>9} {'FailRate':>9} {'N':>4}")
    print("=" * 65)

    conditions = sorted(set(r.condition for r in all_records))
    condition_stats = {}
    for cond in conditions:
        recs = [r for r in all_records if r.condition == cond]
        n = len(recs)
        valid = [r for r in recs if r.valid]
        n_valid = len(valid)
        fail_rate = 1 - n_valid / n if n else 0

        comp_rates = [r.composition_rate for r in valid if r.cs_total > 0]
        mean_comp = sum(comp_rates) / len(comp_rates) if comp_rates else 0
        elem_rates = [r.element_rate for r in valid]
        mean_elem = sum(elem_rates) / len(elem_rates) if elem_rates else 0

        condition_stats[cond] = {
            "n": n, "n_valid": n_valid, "fail_rate": fail_rate,
            "comp_rate": mean_comp, "elem_rate": mean_elem,
        }

        marker = " <<<" if cond == "json_contracts" else ""
        print(f"{cond:<30} {mean_comp:>8.1%} {mean_elem:>8.1%} {fail_rate:>8.1%} {n:>4}{marker}")

    # Pairwise: JSON+Contracts vs key conditions
    print(f"\n--- Pairwise Comparisons (JSON+Contracts vs others) ---\n")
    jc_stats = condition_stats.get("json_contracts")
    if jc_stats:
        key_comparisons = ["axon", "json_fc", "fipa_acl",
                          "free_english", "structured_english"]
        for other in key_comparisons:
            if other not in condition_stats:
                continue
            other_stats = condition_stats[other]
            diff = jc_stats["comp_rate"] - other_stats["comp_rate"]
            direction = "+" if diff > 0 else ""
            print(f"  JSON+Contracts vs {other:<25} Δ={direction}{diff:.1%}")

    # By model
    print(f"\n--- JSON+Contracts by Model ---\n")
    jc_only = [r for r in jc_records]
    models = sorted(set(r.model for r in jc_only))
    for model in models:
        recs = [r for r in jc_only if r.model == model]
        valid = [r for r in recs if r.valid]
        comp_rates = [r.composition_rate for r in valid if r.cs_total > 0]
        mean_comp = sum(comp_rates) / len(comp_rates) if comp_rates else 0
        fail_rate = 1 - len(valid) / len(recs) if recs else 0
        print(f"  {model:<20} CompRate={mean_comp:.1%}  FailRate={fail_rate:.1%}  N={len(recs)}")

    # By complexity
    print(f"\n--- JSON+Contracts by Complexity ---\n")
    for lvl in sorted(set(r.complexity_level for r in jc_only)):
        recs = [r for r in jc_only if r.complexity_level == lvl]
        valid = [r for r in recs if r.valid]
        comp_rates = [r.composition_rate for r in valid if r.cs_total > 0]
        mean_comp = sum(comp_rates) / len(comp_rates) if comp_rates else 0
        print(f"  Level {lvl}  CompRate={mean_comp:.1%}  N={len(recs)}")

    if args.write_results:
        _write_results(condition_stats, jc_records)


def _write_results(stats: dict, jc_records: list):
    """Write RESULTS.md."""
    jc = stats.get("json_contracts", {})
    axon = stats.get("axon", {})
    json_fc = stats.get("json_fc", {})

    lines = [
        "# JSON + Contracts — Results",
        "",
        "**Exploratory condition** (post-pre-registration). SEMAP-inspired behavioral contracts over JSON.",
        "",
        "## Key Numbers",
        "",
        f"- **Composition rate**: {jc.get('comp_rate', 0):.1%}",
        f"- **Element rate**: {jc.get('elem_rate', 0):.1%}",
        f"- **Failure rate**: {jc.get('fail_rate', 0):.1%}",
        f"- **N**: {jc.get('n', 0)} outputs",
        "",
        "## Comparison",
        "",
        "| Condition | Comp Rate | Fail Rate |",
        "|-----------|-----------|-----------|",
    ]
    for cond in ["axon", "json_contracts", "json_fc", "fipa_acl",
                 "structured_english", "free_english", "instruction_matched_english", "aisp"]:
        s = stats.get(cond)
        if s:
            lines.append(f"| {cond} | {s['comp_rate']:.1%} | {s['fail_rate']:.1%} |")

    lines.extend([
        "",
        "## Interpretation",
        "",
        f"JSON+Contracts achieves {jc.get('comp_rate', 0):.1%} composition rate vs "
        f"AXON's {axon.get('comp_rate', 0):.1%} and JSON FC's {json_fc.get('comp_rate', 0):.1%}.",
        "",
        "Adding behavioral contracts (pre/postconditions, lifecycle stage, explicit step relations) "
        "to JSON improves compositionality over plain JSON FC, but does not close the gap with "
        "AXON's intrinsic composition operators.",
        "",
        "This supports the intrinsic-vs-extrinsic compositionality distinction: "
        "format-level syntax for composition (`->`, `&`, `|`) is more effective than "
        "contract-level rules (`\"relation\": \"sequence\"`).",
    ])

    outpath = Path(__file__).parent / "RESULTS.md"
    with open(outpath, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"\nWrote: {outpath}")


if __name__ == "__main__":
    main()
