"""
Exp 1: Cross-Validation and Human Validation

Cross-validation: Re-scores 30 machine-scored outputs with the 3-judge LLM panel
to verify machine extraction agrees with judges. Per scoring_contract.json §validation_protocol.

Human validation: Generates scoring sheets for human rater, then compares human
verdicts against machine/judge verdicts.

Usage:
    # Cross-validation (30 items × 3 judges = ~90 LLM calls)
    python3 experiments/exp1_token_efficiency/scoring/cross_validate.py --cross-validate

    # Resume interrupted cross-validation
    python3 experiments/exp1_token_efficiency/scoring/cross_validate.py --cross-validate --resume

    # Generate human scoring sheet
    python3 experiments/exp1_token_efficiency/scoring/cross_validate.py --human-select

    # Score completed human sheet
    python3 experiments/exp1_token_efficiency/scoring/cross_validate.py --human-score
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
import time
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

# Ensure imports work
SCRIPT_DIR = Path(__file__).resolve().parent
EXP1_DIR = SCRIPT_DIR.parent
PROJECT_ROOT = EXP1_DIR.parent.parent
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(PROJECT_ROOT / "experiments"))

from score import (
    load_annotations,
    load_judge_prompt,
    load_exp0_results,
    score_single_output,
    select_human_validation_subset,
    get_task_elements,
    get_task_instruction,
    RESULTS_DIR,
)
from extractors import MACHINE_SCORED_CONDITIONS
from lib.condition_adapter import CONDITIONS

STRUCTURED_CONDITIONS = ["axon", "json_fc", "fipa_acl"]
TASK_IDS = ["L1-01", "L1-02", "L1-03", "L2-01", "L2-02", "L2-03", "L3-01", "L3-02", "L3-03"]
L3_TASKS = ["L3-01", "L3-02", "L3-03"]

CROSS_VAL_RESULTS_FILE = RESULTS_DIR / "cross_validation_results.json"
CROSS_VAL_CHECKPOINT_FILE = RESULTS_DIR / "cross_validation_checkpoint.json"
HUMAN_SHEET_FILE = RESULTS_DIR / "human_validation_sheet.md"
HUMAN_RESULTS_FILE = RESULTS_DIR / "human_validation_results.json"

AGREEMENT_TARGET = 0.90
AGREEMENT_EXPANSION_TRIGGER = 0.80


# ── Cross-Validation ──────────────────────────────────────────────────


def select_cross_validation_items(scored_results: list[dict], seed: int = 42) -> list[dict]:
    """Select 30 items for cross-validation: 10 per structured format.

    Strategy per format:
    - 1 output per task (9 tasks) — random run
    - 1 extra from L3 tasks (different run from the one already picked)
    Total: 10 per format × 3 formats = 30
    """
    rng = random.Random(seed)
    selected = []

    for condition in STRUCTURED_CONDITIONS:
        cond_items = [r for r in scored_results if r["condition"] == condition]

        # Group by task_id
        by_task = {}
        for item in cond_items:
            by_task.setdefault(item["task_id"], []).append(item)

        # Pick 1 per task
        picked_keys = set()
        format_picks = []
        for task_id in TASK_IDS:
            candidates = by_task.get(task_id, [])
            if candidates:
                pick = rng.choice(candidates)
                format_picks.append(pick)
                picked_keys.add(_item_key(pick))

        # Pick 1 extra from L3 (different run)
        l3_remaining = []
        for task_id in L3_TASKS:
            for item in by_task.get(task_id, []):
                if _item_key(item) not in picked_keys:
                    l3_remaining.append(item)

        if l3_remaining:
            extra = rng.choice(l3_remaining)
            format_picks.append(extra)

        selected.extend(format_picks)

    return selected


def _item_key(item: dict) -> str:
    return f"{item['task_id']}_{item['condition']}_{item['run_number']}"


def run_cross_validation(seed: int = 42, resume: bool = False):
    """Run cross-validation: re-score 30 machine-scored items with judges."""
    print("=" * 70)
    print("CROSS-VALIDATION: Machine vs Judge Agreement")
    print("=" * 70)

    # Load scored codex results
    scored_files = sorted(RESULTS_DIR.glob("exp1_scored_codex_tracka_*.json"))
    if not scored_files:
        print("ERROR: No scored codex results found in", RESULTS_DIR)
        sys.exit(1)

    scored_file = scored_files[-1]  # Most recent
    print(f"\nSource: {scored_file.name}")

    with open(scored_file) as f:
        scored_data = json.load(f)

    scored_results = scored_data["results"]
    annotations = load_annotations()
    judge_prompt_template = load_judge_prompt()

    # Select items
    items = select_cross_validation_items(scored_results, seed)
    print(f"Selected {len(items)} items for cross-validation:")
    for cond in STRUCTURED_CONDITIONS:
        n = sum(1 for i in items if i["condition"] == cond)
        print(f"  {cond}: {n}")

    # Load checkpoint if resuming
    completed = {}
    if resume and CROSS_VAL_CHECKPOINT_FILE.exists():
        with open(CROSS_VAL_CHECKPOINT_FILE) as f:
            checkpoint = json.load(f)
        completed = {r["key"]: r for r in checkpoint.get("results", [])}
        print(f"\nResuming: {len(completed)} items already scored")

    # Score each item with judges
    results = []
    for idx, item in enumerate(items):
        key = _item_key(item)

        # Skip if already done
        if key in completed:
            results.append(completed[key])
            continue

        # Reconstruct raw record for score_single_output
        raw_record = {
            "task_id": item["task_id"],
            "condition": item["condition"],
            "model": item["model"],
            "run_number": item["run_number"],
            "output": item["output"],
            "valid": item["valid"],
            "token_counts": item.get("token_counts"),
        }

        # Determine judges
        rng = random.Random(seed + idx)
        judge_c_model = rng.choice(["claude", "codex"])
        judges_to_use = [
            ("claude", "claude"),
            ("codex", "codex"),
            (f"{judge_c_model}_c", judge_c_model),
        ]

        progress = f"{idx + 1}/{len(items)}"
        print(f"\n  [{progress}] {item['condition']}/{item['task_id']} "
              f"run#{item['run_number']} (judges: A,B,{judge_c_model[0].upper()}) ... ",
              end="", flush=True)

        start = time.monotonic()
        judge_scored = score_single_output(
            raw_record, annotations, "a", judge_prompt_template,
            judges_to_use, force_judge=True,
        )
        elapsed = time.monotonic() - start

        # Compare machine vs judge per element
        machine_scores = item["element_scores"]
        judge_scores = asdict(judge_scored)["element_scores"]

        comparisons = []
        agreements = 0
        total_elements = 0

        for eid, machine_data in machine_scores.items():
            if eid not in judge_scores:
                continue
            total_elements += 1
            machine_verdict = machine_data["majority"]
            judge_verdict = judge_scores[eid]["majority"]
            agree = machine_verdict == judge_verdict
            if agree:
                agreements += 1

            comparisons.append({
                "element_id": eid,
                "element_name": machine_data["name"],
                "machine_verdict": machine_verdict,
                "judge_verdict": judge_verdict,
                "judge_verdicts_detail": judge_scores[eid]["verdicts"],
                "agree": agree,
            })

        agreement_rate = agreements / total_elements if total_elements > 0 else 0.0

        result = {
            "key": key,
            "task_id": item["task_id"],
            "condition": item["condition"],
            "run_number": item["run_number"],
            "output": item["output"],
            "element_comparisons": comparisons,
            "agreement_rate": round(agreement_rate, 4),
            "total_elements": total_elements,
            "agreements": agreements,
            "elapsed_ms": int(elapsed * 1000),
        }
        results.append(result)

        print(f"{agreements}/{total_elements} agree ({agreement_rate:.0%}), "
              f"{int(elapsed)}s")

        # Checkpoint
        _save_cross_val_checkpoint(results)

    # Save final results
    _save_cross_val_results(results)

    # Report
    print_cross_validation_report(results)

    # Clean up checkpoint
    if CROSS_VAL_CHECKPOINT_FILE.exists():
        CROSS_VAL_CHECKPOINT_FILE.unlink()


def _save_cross_val_checkpoint(results: list[dict]):
    data = {
        "checkpoint_time": datetime.now(timezone.utc).isoformat(),
        "total": len(results),
        "results": results,
    }
    tmp = CROSS_VAL_CHECKPOINT_FILE.with_suffix(".tmp")
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2)
    tmp.rename(CROSS_VAL_CHECKPOINT_FILE)


def _save_cross_val_results(results: list[dict]):
    data = {
        "experiment": "exp1_token_efficiency",
        "validation_type": "cross_validation",
        "description": "Machine extraction vs 3-judge panel agreement on 30 structured-format outputs",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_items": len(results),
        "results": results,
    }
    with open(CROSS_VAL_RESULTS_FILE, "w") as f:
        json.dump(data, f, indent=2)
    print(f"\nResults saved: {CROSS_VAL_RESULTS_FILE}")


def print_cross_validation_report(results: list[dict]):
    """Print cross-validation agreement report."""
    print(f"\n{'=' * 70}")
    print("CROSS-VALIDATION REPORT")
    print(f"{'=' * 70}")

    # Overall
    total_elements = sum(r["total_elements"] for r in results)
    total_agreements = sum(r["agreements"] for r in results)
    overall = total_agreements / total_elements if total_elements > 0 else 0
    print(f"\nOverall agreement: {total_agreements}/{total_elements} = {overall:.1%}")
    status = "PASS" if overall >= AGREEMENT_TARGET else "FAIL"
    print(f"Target: {AGREEMENT_TARGET:.0%} — {status}")

    # Per format
    print(f"\n{'Format':<20} {'Items':>6} {'Elements':>10} {'Agree':>8} {'Rate':>8} {'Status':>8}")
    print("-" * 62)
    for cond in STRUCTURED_CONDITIONS:
        cond_results = [r for r in results if r["condition"] == cond]
        n_items = len(cond_results)
        n_elements = sum(r["total_elements"] for r in cond_results)
        n_agree = sum(r["agreements"] for r in cond_results)
        rate = n_agree / n_elements if n_elements > 0 else 0
        cond_status = "PASS" if rate >= AGREEMENT_TARGET else "FAIL"
        print(f"  {cond:<18} {n_items:>6} {n_elements:>10} {n_agree:>8} {rate:>7.1%} {cond_status:>8}")

    # Flagged disagreements
    disagreements = []
    for r in results:
        for comp in r["element_comparisons"]:
            if not comp["agree"]:
                disagreements.append({
                    "item": f"{r['condition']}/{r['task_id']} run#{r['run_number']}",
                    "element": f"{comp['element_id']} ({comp['element_name']})",
                    "machine": comp["machine_verdict"],
                    "judge": comp["judge_verdict"],
                    "judge_detail": comp["judge_verdicts_detail"],
                })

    if disagreements:
        print(f"\nDisagreements ({len(disagreements)}):")
        for d in disagreements:
            print(f"  {d['item']} — {d['element']}: "
                  f"machine={d['machine']}, judge={d['judge']} "
                  f"(detail: {d['judge_detail']})")
    else:
        print("\nNo disagreements found.")

    # Per element category (aggregate across all formats)
    print(f"\nPer-element agreement:")
    element_stats = {}
    for r in results:
        for comp in r["element_comparisons"]:
            name = comp["element_name"]
            element_stats.setdefault(name, {"agree": 0, "total": 0})
            element_stats[name]["total"] += 1
            if comp["agree"]:
                element_stats[name]["agree"] += 1

    for name, stats in sorted(element_stats.items()):
        rate = stats["agree"] / stats["total"] if stats["total"] > 0 else 0
        flag = " ***" if rate < AGREEMENT_TARGET else ""
        print(f"  {name:<30} {stats['agree']}/{stats['total']} = {rate:.0%}{flag}")


# ── Human Validation ──────────────────────────────────────────────────


def generate_human_sheet(seed: int = 42):
    """Generate a human-readable scoring sheet for 30 items (5 per condition)."""
    print("=" * 70)
    print("HUMAN VALIDATION: Generating Scoring Sheet")
    print("=" * 70)

    # Load scored results for all models — use codex for consistency
    scored_files = sorted(RESULTS_DIR.glob("exp1_scored_codex_tracka_*.json"))
    if not scored_files:
        print("ERROR: No scored codex results found")
        sys.exit(1)

    with open(scored_files[-1]) as f:
        scored_data = json.load(f)

    scored_results = scored_data["results"]
    annotations = load_annotations()

    random.seed(seed)
    subset = select_human_validation_subset(scored_results, annotations)
    print(f"Selected {len(subset)} items for human validation")

    # Build the markdown sheet
    lines = [
        "# Human Validation Scoring Sheet",
        "",
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"Source: codex results, seed={seed}",
        f"Items: {len(subset)} (target: 5 per condition)",
        "",
        "## Instructions",
        "",
        "For each item below, read the task instruction and the model's output.",
        "Then mark each element as:",
        "- **P** = PRESENT (the element is expressed accurately)",
        "- **A** = ABSENT (the element is not expressed)",
        "- **I** = INCORRECT (the element is expressed but factually wrong)",
        "",
        "Replace the `[ ]` with `[P]`, `[A]`, or `[I]`.",
        "",
        "---",
        "",
    ]

    for idx, item in enumerate(subset):
        task_id = item["task_id"]
        condition = item["condition"]
        run_num = item["run_number"]
        output = item["output"]
        elements = get_task_elements(annotations, task_id, "a")
        instruction = get_task_instruction(annotations, task_id)

        # Determine current scoring method and verdict
        method = item.get("element_scores", {})
        current_method = "machine" if condition in MACHINE_SCORED_CONDITIONS else "judge"

        lines.append(f"## Item {idx + 1}: {task_id} / {condition} / codex / run#{run_num}")
        lines.append("")
        lines.append(f"**Task**: {instruction}")
        lines.append("")
        lines.append("**Output**:")
        lines.append("```")
        lines.append(output)
        lines.append("```")
        lines.append("")
        lines.append(f"**Scoring method**: {current_method}")
        lines.append("")
        lines.append("**Elements** (mark P, A, or I):")
        for elem in elements:
            eid = elem["id"]
            name = elem["name"]
            check = elem["check"]
            # Show current verdict as reference (hidden from human? No — transparency)
            current = method.get(eid, {}).get("majority", "?")
            lines.append(f"- [ ] {eid} {name} — {check} *(current: {current})*")
        lines.append("")
        lines.append("---")
        lines.append("")

    content = "\n".join(lines)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(HUMAN_SHEET_FILE, "w") as f:
        f.write(content)

    print(f"\nScoring sheet written: {HUMAN_SHEET_FILE}")
    print(f"Items per condition:")
    for cond in CONDITIONS:
        n = sum(1 for s in subset if s["condition"] == cond)
        print(f"  {cond}: {n}")
    print(f"\nNext step: Fill in the sheet, then run --human-score")


def parse_human_sheet() -> list[dict]:
    """Parse a completed human validation scoring sheet."""
    if not HUMAN_SHEET_FILE.exists():
        print(f"ERROR: {HUMAN_SHEET_FILE} not found. Run --human-select first.")
        sys.exit(1)

    with open(HUMAN_SHEET_FILE) as f:
        content = f.read()

    # Parse each item section
    items = []
    # Split on "## Item N:" headers
    sections = re.split(r"^## Item \d+:", content, flags=re.MULTILINE)

    for section in sections[1:]:  # Skip preamble
        # Extract header info
        header_match = re.match(r"\s*(L\d-\d+)\s*/\s*(\w+)\s*/\s*(\w+)\s*/\s*run#(\d+)", section)
        if not header_match:
            continue

        task_id = header_match.group(1)
        condition = header_match.group(2)
        model = header_match.group(3)
        run_number = int(header_match.group(4))

        # Extract element verdicts
        verdicts = {}
        for match in re.finditer(
            r"- \[([PAI])\]\s+([a-z]\d+)\s+(\w+)\s+—",
            section, re.IGNORECASE
        ):
            verdict_char = match.group(1).upper()
            eid = match.group(2)
            name = match.group(3)
            verdict_map = {"P": "PRESENT", "A": "ABSENT", "I": "INCORRECT"}
            verdicts[eid] = {
                "name": name,
                "human_verdict": verdict_map.get(verdict_char, "ABSENT"),
            }

        if verdicts:
            items.append({
                "task_id": task_id,
                "condition": condition,
                "model": model,
                "run_number": run_number,
                "human_verdicts": verdicts,
            })

    return items


def run_human_scoring():
    """Compare human verdicts against machine/judge verdicts."""
    print("=" * 70)
    print("HUMAN VALIDATION: Scoring Analysis")
    print("=" * 70)

    human_items = parse_human_sheet()
    if not human_items:
        print("ERROR: No scored items found in the sheet.")
        print("Make sure you filled in [P], [A], or [I] for each element.")
        sys.exit(1)

    print(f"Parsed {len(human_items)} items from human sheet")

    # Load machine/judge scored results
    scored_files = sorted(RESULTS_DIR.glob("exp1_scored_codex_tracka_*.json"))
    if not scored_files:
        print("ERROR: No scored codex results found")
        sys.exit(1)

    with open(scored_files[-1]) as f:
        scored_data = json.load(f)

    # Index scored results by key
    scored_index = {}
    for r in scored_data["results"]:
        key = f"{r['task_id']}_{r['condition']}_{r['run_number']}"
        scored_index[key] = r

    # Compare
    results = []
    for item in human_items:
        key = f"{item['task_id']}_{item['condition']}_{item['run_number']}"
        scored = scored_index.get(key)
        if not scored:
            print(f"  WARNING: No scored result for {key}")
            continue

        comparisons = []
        agreements = 0
        total = 0

        for eid, human_data in item["human_verdicts"].items():
            scored_elem = scored.get("element_scores", {}).get(eid, {})
            auto_verdict = scored_elem.get("majority", "?")
            human_verdict = human_data["human_verdict"]
            method = scored_elem.get("method", "unknown")

            total += 1
            agree = human_verdict == auto_verdict
            if agree:
                agreements += 1

            comparisons.append({
                "element_id": eid,
                "element_name": human_data["name"],
                "human_verdict": human_verdict,
                "auto_verdict": auto_verdict,
                "auto_method": method,
                "agree": agree,
            })

        agreement_rate = agreements / total if total > 0 else 0.0

        results.append({
            "task_id": item["task_id"],
            "condition": item["condition"],
            "run_number": item["run_number"],
            "comparisons": comparisons,
            "agreement_rate": round(agreement_rate, 4),
            "total_elements": total,
            "agreements": agreements,
        })

    # Save
    output = {
        "experiment": "exp1_token_efficiency",
        "validation_type": "human_validation",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_items": len(results),
        "results": results,
    }
    with open(HUMAN_RESULTS_FILE, "w") as f:
        json.dump(output, f, indent=2)

    # Report
    print_human_validation_report(results)


def print_human_validation_report(results: list[dict]):
    """Print human validation agreement report."""
    print(f"\n{'=' * 70}")
    print("HUMAN VALIDATION REPORT")
    print(f"{'=' * 70}")

    # Overall
    total_elements = sum(r["total_elements"] for r in results)
    total_agreements = sum(r["agreements"] for r in results)
    overall = total_agreements / total_elements if total_elements > 0 else 0
    print(f"\nOverall human-auto agreement: {total_agreements}/{total_elements} = {overall:.1%}")
    status = "PASS" if overall >= AGREEMENT_TARGET else "FAIL"
    print(f"Target: {AGREEMENT_TARGET:.0%} — {status}")

    # Per condition
    print(f"\n{'Condition':<30} {'Items':>6} {'Elements':>10} {'Agree':>8} {'Rate':>8} {'Status':>8}")
    print("-" * 72)
    expand_needed = []
    for cond in CONDITIONS:
        cond_results = [r for r in results if r["condition"] == cond]
        if not cond_results:
            continue
        n_items = len(cond_results)
        n_elements = sum(r["total_elements"] for r in cond_results)
        n_agree = sum(r["agreements"] for r in cond_results)
        rate = n_agree / n_elements if n_elements > 0 else 0
        if rate >= AGREEMENT_TARGET:
            cond_status = "PASS"
        elif rate >= AGREEMENT_EXPANSION_TRIGGER:
            cond_status = "WARN"
        else:
            cond_status = "EXPAND"
            expand_needed.append(cond)
        print(f"  {cond:<28} {n_items:>6} {n_elements:>10} {n_agree:>8} {rate:>7.1%} {cond_status:>8}")

    if expand_needed:
        print(f"\nExpansion needed for: {', '.join(expand_needed)}")
        print(f"Per scoring contract: expand to 10 items per condition (max 60 total)")

    # Per scoring method
    print(f"\nBy scoring method:")
    for method in ["machine", "judge"]:
        method_comps = []
        for r in results:
            for c in r["comparisons"]:
                if c["auto_method"] == method:
                    method_comps.append(c)
        if method_comps:
            agree = sum(1 for c in method_comps if c["agree"])
            total = len(method_comps)
            rate = agree / total
            print(f"  {method}: {agree}/{total} = {rate:.1%}")

    # Disagreements
    disagreements = []
    for r in results:
        for c in r["comparisons"]:
            if not c["agree"]:
                disagreements.append({
                    "item": f"{r['condition']}/{r['task_id']} run#{r['run_number']}",
                    "element": f"{c['element_id']} ({c['element_name']})",
                    "human": c["human_verdict"],
                    "auto": c["auto_verdict"],
                    "method": c["auto_method"],
                })

    if disagreements:
        print(f"\nDisagreements ({len(disagreements)}):")
        for d in disagreements:
            print(f"  {d['item']} — {d['element']}: "
                  f"human={d['human']}, auto={d['auto']} ({d['method']})")

    print(f"\nResults saved: {HUMAN_RESULTS_FILE}")


# ── Main ──────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="Exp 1: Cross-Validation and Human Validation"
    )
    parser.add_argument("--cross-validate", action="store_true",
                        help="Run cross-validation (30 items × 3 judges)")
    parser.add_argument("--human-select", action="store_true",
                        help="Generate human scoring sheet (30 items, 5 per condition)")
    parser.add_argument("--human-score", action="store_true",
                        help="Score completed human sheet and report agreement")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed (default: 42)")
    parser.add_argument("--resume", action="store_true",
                        help="Resume interrupted cross-validation from checkpoint")
    args = parser.parse_args()

    if not any([args.cross_validate, args.human_select, args.human_score]):
        parser.print_help()
        return

    if args.cross_validate:
        run_cross_validation(seed=args.seed, resume=args.resume)

    if args.human_select:
        generate_human_sheet(seed=args.seed)

    if args.human_score:
        run_human_scoring()


if __name__ == "__main__":
    main()
