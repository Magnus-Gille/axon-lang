"""
Exp 1: Token Efficiency — Semantic Element Scorer

Scores Exp 0 outputs for semantic element presence using a 3-judge LLM panel.
Implements the protocol defined in DEVIATION.md.

Usage:
    python3 experiments/exp1_token_efficiency/scoring/score.py --dry-run
    python3 experiments/exp1_token_efficiency/scoring/score.py --calibrate
    python3 experiments/exp1_token_efficiency/scoring/score.py --score --track a
    python3 experiments/exp1_token_efficiency/scoring/score.py --score --track b
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
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path

# Import automated extractors
from extractors import extract_elements, MACHINE_SCORED_CONDITIONS, JUDGE_SCORED_CONDITIONS

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
EXP1_DIR = Path(__file__).resolve().parent.parent
EXP0_RESULTS_DIR = PROJECT_ROOT / "experiments" / "exp0_learnability" / "results"
ANNOTATIONS_FILE = EXP1_DIR / "tasks" / "element_annotations.json"
JUDGE_PROMPT_FILE = EXP1_DIR / "scoring" / "judge_prompt.txt"
RESULTS_DIR = EXP1_DIR / "results"

# Use the 3x replication files (2026-02-13)
EXP0_RESULT_FILES = {
    "claude-haiku": "exp0_claude-haiku_20260213_094541.json",
    "claude-sonnet": "exp0_claude-sonnet_20260213_095053.json",
    "codex": "exp0_codex_20260213_103011.json",
}

# Judge models
JUDGES = {
    "claude": {"tool": "claude", "model": "sonnet", "display": "Claude Sonnet 4.5"},
    "codex": {"tool": "codex", "model": "gpt-5.3-codex", "display": "GPT-5.3 Codex"},
}


@dataclass
class ElementScore:
    element_id: str
    element_name: str
    verdict: str  # PRESENT, ABSENT, INCORRECT
    justification: str


@dataclass
class JudgeResult:
    judge_id: str
    element_scores: list[ElementScore]
    raw_response: str
    latency_ms: int


@dataclass
class ScoredOutput:
    task_id: str
    condition: str
    model: str
    run_number: int
    output: str
    valid: bool
    token_counts: dict | None
    track: str
    element_count_total: int
    element_count_present: int
    element_scores: dict  # {element_id: {verdict, judges, majority}}
    judge_agreement: float
    tokens_per_unit: float | None  # None if element_count_present == 0


def load_annotations() -> dict:
    with open(ANNOTATIONS_FILE) as f:
        return json.load(f)


def load_judge_prompt() -> str:
    with open(JUDGE_PROMPT_FILE) as f:
        return f.read().strip()


def load_exp0_results(model_key: str) -> list[dict]:
    path = EXP0_RESULTS_DIR / EXP0_RESULT_FILES[model_key]
    with open(path) as f:
        data = json.load(f)
    return data["results"]


def get_task_elements(annotations: dict, task_id: str, track: str) -> list[dict]:
    """Get element definitions for a task and track."""
    for task in annotations["tasks"]:
        if task["id"] == task_id:
            track_key = f"track_{track}"
            return task[track_key]["elements"]
    raise ValueError(f"Task {task_id} not found in annotations")


def get_task_instruction(annotations: dict, task_id: str) -> str:
    for task in annotations["tasks"]:
        if task["id"] == task_id:
            return task["instruction"]
    raise ValueError(f"Task {task_id} not found")


def format_judge_prompt(template: str, task_instruction: str,
                        output: str, elements: list[dict]) -> str:
    """Format the judge prompt with task-specific content. No condition labels (blinding)."""
    checklist_lines = []
    for elem in elements:
        checklist_lines.append(f'{elem["id"]}. {elem["name"]}: {elem["check"]}')
    checklist = "\n".join(checklist_lines)

    # Use first element id as example format
    example_id = elements[0]["id"] if elements else "1"

    prompt = template.replace("{task_instruction}", task_instruction)
    prompt = prompt.replace("{output}", output)
    prompt = prompt.replace("{element_checklist}", checklist)
    prompt = prompt.replace("{element_id}", example_id)
    return prompt


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
    if judge_id == "claude":
        return call_claude_judge(prompt)
    elif judge_id == "codex":
        return call_codex_judge(prompt)
    else:
        raise ValueError(f"Unknown judge: {judge_id}")


def parse_judge_response(response: str, elements: list[dict]) -> list[ElementScore]:
    """Parse judge response into element scores."""
    scores = []
    response_upper = response.upper()

    for elem in elements:
        eid = elem["id"]
        name = elem["name"]

        # Look for the element id pattern in the response
        # Match patterns like "a1. PRESENT", "b3. ABSENT", etc.
        pattern = rf'{re.escape(eid)}\.\s*(PRESENT|ABSENT|INCORRECT)\s*[—\-–]?\s*(.*?)(?=\n[a-z]\d+\.|$)'
        match = re.search(pattern, response, re.IGNORECASE | re.DOTALL)

        if match:
            verdict = match.group(1).upper()
            justification = match.group(2).strip()
        else:
            # Fallback: look for the element name
            pattern2 = rf'{re.escape(name)}.*?(PRESENT|ABSENT|INCORRECT)\s*[—\-–]?\s*(.*?)(?=\n|$)'
            match2 = re.search(pattern2, response, re.IGNORECASE)
            if match2:
                verdict = match2.group(1).upper()
                justification = match2.group(2).strip()
            else:
                verdict = "ABSENT"
                justification = "Judge did not score this element"

        scores.append(ElementScore(
            element_id=eid, element_name=name,
            verdict=verdict, justification=justification
        ))
    return scores


def majority_vote(verdicts: list[str]) -> str:
    """Return majority verdict from 3 judges."""
    present_count = sum(1 for v in verdicts if v == "PRESENT")
    return "PRESENT" if present_count >= 2 else "ABSENT"


def score_single_output(
    output_record: dict,
    annotations: dict,
    track: str,
    judge_prompt_template: str,
    judges_to_use: list[tuple[str, str]] | list[str],
    force_judge: bool = False,
) -> ScoredOutput:
    """Score a single output using hybrid approach.

    For structured formats (AXON, JSON FC, FIPA-ACL): automated extraction.
    For English formats: 3-judge LLM panel.
    force_judge=True overrides to use judges for all conditions (for cross-validation).

    judges_to_use: list of (unique_id, model_key) tuples, or plain strings for backward compat.
    """
    # Normalize to tuple format
    if judges_to_use and isinstance(judges_to_use[0], str):
        judges_to_use = [(j, j) for j in judges_to_use]
    task_id = output_record["task_id"]
    condition = output_record["condition"]
    elements = get_task_elements(annotations, task_id, track)
    instruction = get_task_instruction(annotations, task_id)
    raw_output = output_record["output"]
    total_elements = len(elements)

    # Try automated extraction for structured formats
    if not force_judge and condition in MACHINE_SCORED_CONDITIONS:
        extraction = extract_elements(condition, raw_output, elements, task_id)
        if extraction is not None:
            element_results = {}
            for elem in elements:
                eid = elem["id"]
                ext = extraction.get(eid, {"verdict": "ABSENT", "evidence": "No extraction result"})
                element_results[eid] = {
                    "name": elem["name"],
                    "verdicts": {"machine": ext["verdict"]},
                    "majority": ext["verdict"],
                    "unanimous": True,
                    "method": "machine",
                    "evidence": ext["evidence"],
                }

            present_count = sum(
                1 for er in element_results.values() if er["majority"] == "PRESENT"
            )
            agreement_rate = 1.0  # Machine scoring is deterministic

            token_counts = output_record.get("token_counts")
            tokens_per_unit = None
            if token_counts and present_count > 0:
                cl100k = token_counts.get("cl100k_base", 0)
                tokens_per_unit = cl100k / present_count

            return ScoredOutput(
                task_id=task_id,
                condition=condition,
                model=output_record["model"],
                run_number=output_record["run_number"],
                output=raw_output,
                valid=output_record["valid"],
                token_counts=token_counts,
                track=track,
                element_count_total=total_elements,
                element_count_present=present_count,
                element_scores=element_results,
                judge_agreement=round(agreement_rate, 4),
                tokens_per_unit=round(tokens_per_unit, 4) if tokens_per_unit else None,
            )

    # Fall back to LLM judge scoring (English conditions or force_judge mode)
    prompt = format_judge_prompt(judge_prompt_template, instruction, raw_output, elements)

    # Call each judge
    judge_results = []
    for unique_id, model_key in judges_to_use:
        try:
            response, latency = call_judge(model_key, prompt)
            element_scores = parse_judge_response(response, elements)
            judge_results.append(JudgeResult(
                judge_id=unique_id, element_scores=element_scores,
                raw_response=response, latency_ms=latency
            ))
        except Exception as e:
            print(f"    Judge {unique_id} failed: {e}")
            # Create all-ABSENT fallback
            fallback_scores = [
                ElementScore(element_id=elem["id"], element_name=elem["name"],
                             verdict="ABSENT", justification=f"Judge error: {e}")
                for elem in elements
            ]
            judge_results.append(JudgeResult(
                judge_id=unique_id, element_scores=fallback_scores,
                raw_response=str(e), latency_ms=0
            ))

    # Compute majority vote per element
    element_results = {}
    agreements = 0

    for i, elem in enumerate(elements):
        verdicts = [jr.element_scores[i].verdict for jr in judge_results]
        majority = majority_vote(verdicts)
        all_agree = len(set(verdicts)) == 1
        if all_agree:
            agreements += 1

        element_results[elem["id"]] = {
            "name": elem["name"],
            "verdicts": {jr.judge_id: jr.element_scores[i].verdict for jr in judge_results},
            "majority": majority,
            "unanimous": all_agree,
            "method": "judge",
        }

    present_count = sum(
        1 for er in element_results.values() if er["majority"] == "PRESENT"
    )
    agreement_rate = agreements / total_elements if total_elements > 0 else 0

    # Compute tokens per unit
    token_counts = output_record.get("token_counts")
    tokens_per_unit = None
    if token_counts and present_count > 0:
        cl100k = token_counts.get("cl100k_base", 0)
        tokens_per_unit = cl100k / present_count

    return ScoredOutput(
        task_id=task_id,
        condition=condition,
        model=output_record["model"],
        run_number=output_record["run_number"],
        output=raw_output,
        valid=output_record["valid"],
        token_counts=token_counts,
        track=track,
        element_count_total=total_elements,
        element_count_present=present_count,
        element_scores=element_results,
        judge_agreement=round(agreement_rate, 4),
        tokens_per_unit=round(tokens_per_unit, 4) if tokens_per_unit else None,
    )


def select_human_validation_subset(all_results: list[dict],
                                   annotations: dict) -> list[dict]:
    """Select 30 items for human validation: 5 per condition, spanning complexity levels."""
    from lib.condition_adapter import CONDITIONS
    subset = []
    for condition in CONDITIONS:
        cond_results = [r for r in all_results if r["condition"] == condition]
        # Pick 1 per level + 2 edge cases
        by_level = {}
        for r in cond_results:
            level = r["task_id"].split("-")[0]  # L1, L2, L3
            by_level.setdefault(level, []).append(r)

        picked = []
        for level in ["L1", "L2", "L3"]:
            candidates = by_level.get(level, [])
            if candidates:
                picked.append(random.choice(candidates))

        # 2 edge cases: prefer invalid or borderline outputs
        remaining = [r for r in cond_results if r not in picked]
        invalids = [r for r in remaining if not r["valid"]]
        if len(invalids) >= 2:
            picked.extend(random.sample(invalids, 2))
        elif invalids:
            picked.extend(invalids)
            others = [r for r in remaining if r not in invalids]
            if others:
                picked.append(random.choice(others))
        else:
            if len(remaining) >= 2:
                picked.extend(random.sample(remaining, 2))

        subset.extend(picked[:5])

    return subset


def run_dry(annotations: dict, track: str):
    """Show what would be scored without calling any LLM."""
    print("=" * 60)
    print(f"Exp 1 Token Efficiency — DRY RUN (Track {track.upper()})")
    print("=" * 60)

    tasks = annotations["tasks"]
    track_key = f"track_{track}"
    total_elements = 0
    for task in tasks:
        t = task[track_key]
        total_elements += t["count"]
        print(f"  [{task['id']}] {task['description']}: {t['count']} elements")
    print(f"\n  Total elements per output set: {total_elements}")
    print(f"  Mean elements per task: {total_elements / len(tasks):.1f}")

    # Count available Exp 0 outputs
    total_outputs = 0
    for model_key, filename in EXP0_RESULT_FILES.items():
        path = EXP0_RESULTS_DIR / filename
        if path.exists():
            with open(path) as f:
                data = json.load(f)
            n = len(data["results"])
            total_outputs += n
            print(f"\n  {model_key}: {n} outputs ({path.name})")
        else:
            print(f"\n  {model_key}: FILE NOT FOUND ({filename})")

    # With hybrid scoring, structured formats use machine extraction
    machine_outputs = total_outputs // 2  # 3 of 6 conditions are machine-scored
    judge_outputs = total_outputs - machine_outputs
    total_judge_calls = judge_outputs * 3  # 3 judges per judge-scored output
    total_element_scores = total_outputs * total_elements / len(tasks)
    print(f"\n  Total outputs to score: {total_outputs}")
    print(f"    Machine-scored (AXON/JSON/FIPA): {machine_outputs}")
    print(f"    Judge-scored (English ×3):       {judge_outputs}")
    print(f"  Judge calls needed: {total_judge_calls} (3 per judge-scored output)")
    print(f"  Estimated element scores: {int(total_element_scores)}")

    # Check CLI tools
    print("\n  CLI tool check:")
    for name, cmd in [("claude", ["claude", "--version"]), ("codex", ["codex", "--version"])]:
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            version = r.stdout.strip().split("\n")[0] if r.stdout else "unknown"
            print(f"    {name}: {version}")
        except FileNotFoundError:
            print(f"    {name}: NOT FOUND")

    print("\nDry run complete. Use --score to execute.")


def _checkpoint_path(model_key: str, track: str) -> Path:
    """Return path for the incremental checkpoint file."""
    return RESULTS_DIR / f"exp1_checkpoint_{model_key}_track{track}.json"


def _load_checkpoint(model_key: str, track: str) -> list[dict]:
    """Load previously scored results from checkpoint. Returns [] if none."""
    cp = _checkpoint_path(model_key, track)
    if cp.exists():
        with open(cp) as f:
            data = json.load(f)
        return data.get("results", [])
    return []


def _save_checkpoint(scored: list[ScoredOutput], model_key: str, track: str):
    """Save current progress to checkpoint file (overwrites)."""
    cp = _checkpoint_path(model_key, track)
    data = {
        "experiment": "exp1_token_efficiency",
        "track": track,
        "model": model_key,
        "checkpoint_time": datetime.now(timezone.utc).isoformat(),
        "total_scored": len(scored),
        "results": [asdict(r) for r in scored],
    }
    # Write atomically via temp file
    tmp = cp.with_suffix(".tmp")
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2)
    tmp.rename(cp)


def _result_key(record: dict) -> str:
    """Unique key for a (task, condition, run) cell."""
    return f"{record['task_id']}_{record['condition']}_{record['run_number']}"


def run_scoring(annotations: dict, track: str, models: list[str] | None = None,
                limit: int = 0):
    """Score all Exp 0 outputs for semantic elements.

    Features:
    - Checkpoints after every output (resume-safe for long runs)
    - Skips already-scored outputs on resume
    - --limit N stops after N new scores (checkpoint preserved for resume)
    - Saves final results + removes checkpoint only when ALL outputs are done
    """
    judge_prompt_template = load_judge_prompt()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    if models is None:
        models = list(EXP0_RESULT_FILES.keys())

    for model_key in models:
        print(f"\n{'=' * 70}")
        print(f"SCORING: {model_key} — Track {track.upper()}")
        print(f"{'=' * 70}")

        results = load_exp0_results(model_key)

        # Load checkpoint if resuming
        existing = _load_checkpoint(model_key, track)
        existing_keys = set()
        scored: list[ScoredOutput] = []
        if existing:
            existing_keys = {_result_key(r) for r in existing}
            # Reconstruct ScoredOutput objects from checkpoint dicts
            for r in existing:
                scored.append(ScoredOutput(**{
                    k: r[k] for k in ScoredOutput.__dataclass_fields__
                }))
            print(f"  Resumed from checkpoint: {len(scored)} already scored")

        cell = 0
        skipped = 0
        new_scored = 0
        total = len(results)
        start_time = time.monotonic()

        for record in results:
            cell += 1
            task_id = record["task_id"]
            condition = record["condition"]
            run_num = record["run_number"]

            # Skip if already scored
            key = _result_key(record)
            if key in existing_keys:
                skipped += 1
                continue

            # Stop if we've hit the limit for this run
            if limit and new_scored >= limit:
                print(f"\n  Limit reached ({limit} outputs). "
                      f"Checkpoint saved ({len(scored)} total). "
                      f"Re-run to continue.")
                break

            # Determine judges: A=claude, B=codex, C=random(A,B)
            judge_c_model = random.choice(["claude", "codex"])
            # Use unique IDs so dict keys don't collide
            judges_to_use = [
                ("claude", "claude"),
                ("codex", "codex"),
                (f"{judge_c_model}_c", judge_c_model),
            ]

            remaining = total - cell
            elapsed = time.monotonic() - start_time
            avg = elapsed / new_scored if new_scored > 0 else 0
            eta = avg * (min(limit, remaining) if limit else remaining)
            eta_str = f" ETA {int(eta)}s" if new_scored > 0 else ""
            progress = f"{len(scored)+1}/{total}"
            method = "machine" if condition in MACHINE_SCORED_CONDITIONS else "judge"
            judge_info = f"(judges: A,B,{judge_c_model[0].upper()})" if method == "judge" else "(auto)"
            print(f"  [{progress}]{eta_str} {condition}/{task_id} run#{run_num} "
                  f"{judge_info} ... ", end="", flush=True)

            result = score_single_output(
                record, annotations, track, judge_prompt_template, judges_to_use
            )
            scored.append(result)
            new_scored += 1

            tpu = f"{result.tokens_per_unit:.1f}" if result.tokens_per_unit else "N/A"
            print(f"{result.element_count_present}/{result.element_count_total} "
                  f"elements, {tpu} tok/unit, "
                  f"agreement={result.judge_agreement:.0%}")

            # Checkpoint after every output
            _save_checkpoint(scored, model_key, track)

        all_done = len(scored) >= total

        if all_done:
            # Save final results and clean up checkpoint
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            outfile = RESULTS_DIR / f"exp1_scored_{model_key}_track{track}_{timestamp}.json"
            data = {
                "experiment": "exp1_token_efficiency",
                "track": track,
                "model": model_key,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "total_scored": len(scored),
                "results": [asdict(r) for r in scored],
            }
            with open(outfile, "w") as f:
                json.dump(data, f, indent=2)

            cp = _checkpoint_path(model_key, track)
            if cp.exists():
                cp.unlink()

            print(f"\nAll done! Results saved: {outfile}")
        else:
            print(f"\n  Progress: {len(scored)}/{total} scored. "
                  f"Re-run same command to continue.")

        if skipped:
            print(f"  ({skipped} resumed from checkpoint, {new_scored} new this run)")

        # Summary of what we have so far
        print_scoring_summary(scored, track)


def print_scoring_summary(scored: list[ScoredOutput], track: str):
    """Print summary statistics for scored outputs."""
    sys.path.insert(0, str(PROJECT_ROOT / "experiments"))
    from lib.condition_adapter import CONDITIONS

    print(f"\n{'=' * 70}")
    print(f"SCORING SUMMARY — Track {track.upper()}")
    print(f"{'=' * 70}")

    print(f"\n{'Condition':<28} {'Elements':>10} {'Tok/Unit':>10} {'Agreement':>10}")
    print("-" * 60)
    for condition in CONDITIONS:
        c_results = [r for r in scored if r.condition == condition]
        if not c_results:
            continue
        mean_present = sum(r.element_count_present for r in c_results) / len(c_results)
        tpu_values = [r.tokens_per_unit for r in c_results if r.tokens_per_unit is not None]
        mean_tpu = sum(tpu_values) / len(tpu_values) if tpu_values else 0
        mean_agree = sum(r.judge_agreement for r in c_results) / len(c_results)
        print(f"  {condition:<26} {mean_present:>10.1f} {mean_tpu:>10.1f} {mean_agree:>10.1%}")

    # Zero-element outputs
    zeros = [r for r in scored if r.element_count_present == 0]
    if zeros:
        print(f"\n  Zero-element outputs (complete failures): {len(zeros)}")
        for r in zeros:
            print(f"    [{r.task_id}] {r.condition} run#{r.run_number}")


def main():
    parser = argparse.ArgumentParser(description="Exp 1: Semantic Element Scorer")
    parser.add_argument("--dry-run", action="store_true", help="Show plan without executing")
    parser.add_argument("--score", action="store_true", help="Score all Exp 0 outputs")
    parser.add_argument("--calibrate", action="store_true",
                        help="Run calibration on 36-item subset")
    parser.add_argument("--track", choices=["a", "b"], default="a",
                        help="Element track: a=prereg-faithful, b=expanded (default: a)")
    parser.add_argument("--model", action="append", dest="models",
                        choices=list(EXP0_RESULT_FILES.keys()),
                        help="Model(s) to score (repeatable, default: all)")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed for judge C selection and subset sampling")
    parser.add_argument("--limit", type=int, default=0,
                        help="Max outputs to score this run (0=all). Checkpoints after each, resume later.")
    parser.add_argument("--resume", action="store_true",
                        help="Resume from checkpoint (auto-detected, this flag is a no-op reminder)")
    args = parser.parse_args()

    random.seed(args.seed)
    annotations = load_annotations()

    if args.dry_run or (not args.score and not args.calibrate):
        run_dry(annotations, args.track)
        return

    if args.calibrate:
        print("Calibration mode: scoring 36-item human validation subset")
        print("(Implement human ground truth comparison here)")
        # TODO: implement calibration against human-scored ground truth
        return

    if args.score:
        # Resume is automatic — checkpoint is detected if present
        run_scoring(annotations, args.track, args.models, limit=args.limit)


if __name__ == "__main__":
    main()
