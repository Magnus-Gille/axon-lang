"""
Exp 3: Compositionality — Hybrid Scorer

Scores both standard elements (reusing Exp 1 extractors) and
composition-structure elements (new for Exp 3).

Usage:
    # Machine-score a results file (AXON AST + text extraction)
    python3 experiments/exp3_compositionality/scoring/score.py results/exp3_codex_*.json

    # Score with judge panel for English conditions (requires CLI tools)
    python3 experiments/exp3_compositionality/scoring/score.py --judge results/*_scored.json

    # Limit judge scoring to N outputs per run (checkpoint-resumable)
    python3 experiments/exp3_compositionality/scoring/score.py --judge --limit 10 results/*_scored.json

    # Test extractor on a known-good AXON output
    python3 experiments/exp3_compositionality/scoring/score.py --test

    # Cross-validate AXON machine scores against judge panel
    python3 experiments/exp3_compositionality/scoring/score.py --cross-validate results/exp3_*.json
"""

from __future__ import annotations

import argparse
import json
import os
import random
import re
import subprocess
import sys
import time
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


# ── Judge Infrastructure ──────────────────────────────────────────────

JUDGE_PROMPT_FILE = Path(__file__).parent / "composition_judge_prompt.txt"
EXP1_JUDGE_PROMPT_FILE = (
    PROJECT_ROOT / "experiments" / "exp1_token_efficiency" / "scoring" / "judge_prompt.txt"
)


def load_judge_prompt(path: Path) -> str:
    with open(path) as f:
        return f.read().strip()


def call_claude_judge(prompt: str) -> tuple[str, int]:
    """Call Claude as a judge via CLI."""
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    system = (
        "You are a precise scoring assistant. Follow the instructions exactly. "
        "Output only the scoring lines, nothing else."
    )
    start = time.monotonic()
    result = subprocess.run(
        [
            "claude", "-p",
            "--system-prompt", system,
            "--model", "sonnet",
            "--no-session-persistence",
            "--tools", "",
        ],
        input=prompt,
        capture_output=True,
        text=True,
        timeout=120,
        env=env,
    )
    latency_ms = int((time.monotonic() - start) * 1000)
    if result.returncode != 0:
        raise RuntimeError(f"claude judge failed: {result.stderr.strip()}")
    return result.stdout.strip(), latency_ms


def call_codex_judge(prompt: str) -> tuple[str, int]:
    """Call Codex as a judge via CLI."""
    import tempfile
    outfile = tempfile.mktemp(suffix=".txt")
    combined = (
        "You are a precise scoring assistant. Follow the instructions exactly. "
        "Output only the scoring lines, nothing else.\n\n"
        f"{prompt}"
    )
    start = time.monotonic()
    try:
        result = subprocess.run(
            ["codex", "exec", "--model", "gpt-5.3-codex", "-o", outfile, combined],
            capture_output=True, text=True, timeout=180,
        )
        latency_ms = int((time.monotonic() - start) * 1000)
        if result.returncode != 0:
            raise RuntimeError(f"codex judge failed: {result.stderr.strip()}")
        with open(outfile) as f:
            output = f.read().strip()
    finally:
        if os.path.exists(outfile):
            os.unlink(outfile)
    return output, latency_ms


def call_judge(judge_id: str, prompt: str) -> tuple[str, int]:
    if judge_id in ("claude", "claude_c"):
        return call_claude_judge(prompt)
    elif judge_id in ("codex", "codex_c"):
        return call_codex_judge(prompt)
    else:
        raise ValueError(f"Unknown judge: {judge_id}")


def format_element_prompt(template: str, instruction: str, output: str,
                          elements: list[dict]) -> str:
    """Format the standard element judge prompt (Exp 1 pattern)."""
    checklist = "\n".join(
        f'{e["id"]}. {e["name"]}: {e["check"]}' for e in elements
    )
    example_id = elements[0]["id"] if elements else "e1"
    prompt = template.replace("{task_instruction}", instruction)
    prompt = prompt.replace("{output}", output)
    prompt = prompt.replace("{element_checklist}", checklist)
    prompt = prompt.replace("{element_id}", example_id)
    return prompt


def format_composition_prompt(template: str, output: str,
                              cs_elements: list[dict]) -> str:
    """Format the composition-structure judge prompt."""
    checklist = "\n".join(
        f'{e["id"]}. [{e["type"].upper()}] {e["name"]}: {e["check"]}'
        for e in cs_elements
    )
    prompt = (
        f"{template}\n\n"
        f"## Message to Evaluate\n\n"
        f"```\n{output}\n```\n\n"
        f"## Elements to Score\n\n{checklist}\n\n"
        f"Respond with a JSON object containing one entry per element ID."
    )
    return prompt


def parse_element_response(response: str, elements: list[dict]) -> dict:
    """Parse standard element judge response into verdicts."""
    results = {}
    for elem in elements:
        eid = elem["id"]
        pattern = rf'{re.escape(eid)}\.\s*(PRESENT|ABSENT|INCORRECT)\s*[—\-–]?\s*(.*?)(?=\n[a-z]\d+\.|$)'
        match = re.search(pattern, response, re.IGNORECASE | re.DOTALL)
        if match:
            results[eid] = match.group(1).upper()
        else:
            pattern2 = rf'{re.escape(elem["name"])}.*?(PRESENT|ABSENT|INCORRECT)'
            match2 = re.search(pattern2, response, re.IGNORECASE)
            results[eid] = match2.group(1).upper() if match2 else "ABSENT"
    return results


def parse_composition_response(response: str, cs_elements: list[dict]) -> dict:
    """Parse composition judge response into verdicts.

    Tries JSON first, falls back to line-based parsing.
    """
    results = {}

    # Try JSON extraction
    json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response, re.DOTALL)
    if json_match:
        try:
            parsed = json.loads(json_match.group(0))
            for elem in cs_elements:
                eid = elem["id"]
                if eid in parsed:
                    entry = parsed[eid]
                    if isinstance(entry, dict):
                        results[eid] = entry.get("verdict", "ABSENT").upper()
                    elif isinstance(entry, str):
                        results[eid] = entry.upper() if entry.upper() in ("PRESENT", "ABSENT", "INCORRECT") else "ABSENT"
            if len(results) == len(cs_elements):
                return results
        except (json.JSONDecodeError, TypeError):
            pass

    # Fallback: line-based parsing
    for elem in cs_elements:
        eid = elem["id"]
        if eid in results:
            continue
        pattern = rf'{re.escape(eid)}.*?(PRESENT|ABSENT|INCORRECT)'
        match = re.search(pattern, response, re.IGNORECASE)
        results[eid] = match.group(1).upper() if match else "ABSENT"

    return results


def majority_vote(verdicts: list[str]) -> str:
    """Return majority verdict from 3 judges."""
    present_count = sum(1 for v in verdicts if v == "PRESENT")
    return "PRESENT" if present_count >= 2 else "ABSENT"


def _result_key(result: dict) -> str:
    """Unique key for checkpoint tracking."""
    return f"{result['task_id']}_{result['condition']}_{result['run_number']}"


def _checkpoint_path(scored_file: str) -> Path:
    """Checkpoint path for a scored file being judge-scored."""
    p = Path(scored_file)
    return p.parent / f"{p.stem}_judge_checkpoint.json"


def _load_checkpoint(scored_file: str) -> dict:
    """Load checkpoint: returns dict of result_key -> judge verdicts."""
    cp = _checkpoint_path(scored_file)
    if cp.exists():
        with open(cp) as f:
            return json.load(f)
    return {}


def _save_checkpoint(scored_file: str, checkpoint_data: dict):
    """Save checkpoint atomically."""
    cp = _checkpoint_path(scored_file)
    tmp = cp.with_suffix(".tmp")
    with open(tmp, "w") as f:
        json.dump(checkpoint_data, f, indent=2)
    tmp.rename(cp)


def run_judge_scoring(scored_files: list[str], annotations: dict,
                      limit: int = 0, seed: int = 42):
    """Run 3-judge panel on scored results that have needs_judge items.

    Reads already-scored files, fills in judge verdicts for elements marked
    as needs_judge, and saves updated scored files.
    """
    random.seed(seed)
    elem_prompt_template = load_judge_prompt(EXP1_JUDGE_PROMPT_FILE)
    comp_prompt_template = load_judge_prompt(JUDGE_PROMPT_FILE)

    for scored_file in scored_files:
        print(f"\n{'=' * 70}")
        print(f"JUDGE SCORING: {scored_file}")
        print(f"{'=' * 70}")

        with open(scored_file) as f:
            data = json.load(f)

        results = data["results"]
        checkpoint = _load_checkpoint(scored_file)
        if checkpoint:
            print(f"  Resumed from checkpoint: {len(checkpoint)} outputs already judge-scored")

        total_outputs = len(results)
        new_scored = 0
        skipped_no_judge = 0
        skipped_checkpoint = 0
        total_judge_calls = 0
        start_time = time.monotonic()

        for i, result in enumerate(results):
            scores = result.get("scores", {})
            needs_judge = scores.get("needs_judge", [])

            if not needs_judge:
                skipped_no_judge += 1
                continue

            key = _result_key(result)
            if key in checkpoint:
                # Apply checkpoint verdicts
                _apply_judge_verdicts(result, checkpoint[key])
                skipped_checkpoint += 1
                continue

            if limit and new_scored >= limit:
                print(f"\n  Limit reached ({limit}). Checkpoint saved. Re-run to continue.")
                break

            # Determine judges: A=claude, B=codex, C=random
            judge_c_model = random.choice(["claude", "codex"])
            judges = [
                ("claude", "claude"),
                ("codex", "codex"),
                (f"{judge_c_model}_c", judge_c_model),
            ]

            task_id = result["task_id"]
            condition = result["condition"]
            output_text = result["output"]
            task_ann = get_task_annotations(annotations, task_id)

            elapsed = time.monotonic() - start_time
            avg = elapsed / new_scored if new_scored > 0 else 0
            remaining = sum(1 for r in results[i+1:] if r.get("scores", {}).get("needs_judge"))
            if limit:
                remaining = min(remaining, limit - new_scored)
            eta = avg * remaining
            eta_str = f" ETA {int(eta)}s" if new_scored > 0 else ""

            print(f"  [{i+1}/{total_outputs}]{eta_str} {condition}/{task_id} "
                  f"run#{result['run_number']} ({len(needs_judge)} items, "
                  f"judges: A,B,{judge_c_model[0].upper()}) ... ",
                  end="", flush=True)

            # Separate element IDs and composition-structure IDs
            elem_ids_needing = [eid for eid in needs_judge if eid.startswith("e")]
            cs_ids_needing = [eid for eid in needs_judge if eid.startswith("cs")]

            judge_verdicts = {"elements": {}, "composition_structure": {}}

            # Score standard elements via judge panel
            if elem_ids_needing and task_ann:
                all_elements = task_ann["elements"]["items"]
                needed_elements = [e for e in all_elements if e["id"] in elem_ids_needing]
                instruction = task_ann.get("instruction", "")
                prompt = format_element_prompt(
                    elem_prompt_template, instruction, output_text, needed_elements
                )

                for judge_uid, judge_model in judges:
                    try:
                        resp, latency = call_judge(judge_uid, prompt)
                        verdicts = parse_element_response(resp, needed_elements)
                        for eid, verdict in verdicts.items():
                            judge_verdicts["elements"].setdefault(eid, {})[judge_uid] = verdict
                        total_judge_calls += 1
                    except Exception as e:
                        print(f"ERR({judge_uid}) ", end="", flush=True)
                        for eid in elem_ids_needing:
                            judge_verdicts["elements"].setdefault(eid, {})[judge_uid] = "ABSENT"
                        total_judge_calls += 1

            # Score composition-structure via judge panel
            if cs_ids_needing and task_ann:
                all_cs = task_ann["composition_structure"]["items"]
                needed_cs = [e for e in all_cs if e["id"] in cs_ids_needing]
                prompt = format_composition_prompt(
                    comp_prompt_template, output_text, needed_cs
                )

                for judge_uid, judge_model in judges:
                    try:
                        resp, latency = call_judge(judge_uid, prompt)
                        verdicts = parse_composition_response(resp, needed_cs)
                        for eid, verdict in verdicts.items():
                            judge_verdicts["composition_structure"].setdefault(eid, {})[judge_uid] = verdict
                        total_judge_calls += 1
                    except Exception as e:
                        print(f"ERR({judge_uid}) ", end="", flush=True)
                        for eid in cs_ids_needing:
                            judge_verdicts["composition_structure"].setdefault(eid, {})[judge_uid] = "ABSENT"
                        total_judge_calls += 1

            # Apply verdicts
            _apply_judge_verdicts(result, judge_verdicts)

            # Compute agreement for this output
            all_unanimous = True
            for eid, jv in {**judge_verdicts.get("elements", {}),
                            **judge_verdicts.get("composition_structure", {})}.items():
                if len(set(jv.values())) > 1:
                    all_unanimous = False
                    break

            scores = result["scores"]
            print(f"elem={scores['element_present']}/{scores['element_total']} "
                  f"comp={scores['cs_present']}/{scores['cs_total']} "
                  f"{'unanimous' if all_unanimous else 'split'}")

            # Save to checkpoint
            checkpoint[key] = judge_verdicts
            _save_checkpoint(scored_file, checkpoint)
            new_scored += 1

        # Save updated scored file
        data["scoring"]["judge_timestamp"] = datetime.now(timezone.utc).isoformat()
        data["scoring"]["judge_calls"] = total_judge_calls
        data["scoring"]["method"] = (
            "machine (AXON AST) + text extraction + 3-judge panel "
            "(Claude A, Codex B, random C)"
        )

        with open(scored_file, "w") as f:
            json.dump(data, f, indent=2)

        # Clean up checkpoint if all done
        remaining_needs = sum(
            1 for r in data["results"]
            if r.get("scores", {}).get("needs_judge")
        )
        if remaining_needs == 0:
            cp = _checkpoint_path(scored_file)
            if cp.exists():
                cp.unlink()
            print(f"\n  All judge scoring complete. Checkpoint removed.")
        else:
            print(f"\n  {remaining_needs} outputs still need judge scoring.")

        print(f"\n  Summary: {new_scored} new, {skipped_checkpoint} resumed, "
              f"{skipped_no_judge} no-judge-needed, {total_judge_calls} judge calls")
        print(f"  Updated: {scored_file}")
        print_scoring_summary(data)


def _apply_judge_verdicts(result: dict, judge_verdicts: dict):
    """Apply judge verdicts to a result's scores, updating rates."""
    scores = result["scores"]

    # Apply element verdicts
    for eid, jv in judge_verdicts.get("elements", {}).items():
        verdicts_list = list(jv.values())
        maj = majority_vote(verdicts_list)
        scores["elements"][eid] = {
            "verdicts": jv,
            "majority": maj,
            "unanimous": len(set(verdicts_list)) == 1,
            "method": "judge",
        }

    # Apply composition-structure verdicts
    for eid, jv in judge_verdicts.get("composition_structure", {}).items():
        verdicts_list = list(jv.values())
        maj = majority_vote(verdicts_list)
        scores["composition_structure"][eid] = {
            "verdicts": jv,
            "majority": maj,
            "unanimous": len(set(verdicts_list)) == 1,
            "method": "judge",
        }

    # Clear needs_judge for items that now have verdicts
    scored_ids = set(judge_verdicts.get("elements", {}).keys()) | \
                 set(judge_verdicts.get("composition_structure", {}).keys())
    scores["needs_judge"] = [eid for eid in scores.get("needs_judge", [])
                             if eid not in scored_ids]

    # Recompute rates
    elem_total = scores.get("element_total", 0)
    elem_present = sum(
        1 for r in scores.get("elements", {}).values()
        if (r.get("majority") or r.get("verdict", "")) == "PRESENT"
    )
    scores["element_present"] = elem_present
    scores["element_rate"] = elem_present / elem_total if elem_total > 0 else 0.0

    cs_total = scores.get("cs_total", 0)
    cs_present = sum(
        1 for r in scores.get("composition_structure", {}).values()
        if (r.get("majority") or r.get("verdict", "")) == "PRESENT"
    )
    scores["cs_present"] = cs_present
    scores["composition_rate"] = cs_present / cs_total if cs_total > 0 else 0.0


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
                        help="Run 3-judge panel on scored files (fills needs_judge items)")
    parser.add_argument("--limit", type=int, default=0,
                        help="Max outputs to judge-score per file (0=all)")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed for judge C selection")
    parser.add_argument("--cross-validate", action="store_true",
                        help="Cross-validate AXON machine scores against judge panel")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be judge-scored without calling LLMs")
    args = parser.parse_args()

    if args.test:
        run_test()
        return

    if not args.files:
        parser.print_help()
        return

    annotations = load_annotations()

    if args.judge:
        if args.dry_run:
            # Show what needs judge scoring
            for filepath in args.files:
                with open(filepath) as f:
                    data = json.load(f)
                total_needs = sum(
                    len(r.get("scores", {}).get("needs_judge", []))
                    for r in data["results"]
                )
                outputs_needing = sum(
                    1 for r in data["results"]
                    if r.get("scores", {}).get("needs_judge")
                )
                print(f"{filepath}: {outputs_needing} outputs, {total_needs} elements need judge")
            return

        run_judge_scoring(args.files, annotations, limit=args.limit, seed=args.seed)
        return

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
