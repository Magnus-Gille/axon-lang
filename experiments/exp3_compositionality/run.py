"""
Exp 3: Compositionality — Runner Script

Tests whether LLMs can correctly compose multi-step messages using
composition operators (sequence, parallel, alternative, causal, negation).

Uses CLI tools (claude, codex) — zero API cost via existing subscriptions.

Reuses system prompts from Exp 0 (same condition definitions).

Usage:
    python3 experiments/exp3_compositionality/run.py --dry-run
    python3 experiments/exp3_compositionality/run.py --condition axon --task L1-01 --runs 1
    python3 experiments/exp3_compositionality/run.py --all
    python3 experiments/exp3_compositionality/run.py --all --runs 3
    python3 experiments/exp3_compositionality/run.py --all --model claude-haiku
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path

# Add project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "experiments"))

from lib.condition_adapter import CONDITIONS, validate_output


# Reuse Exp 0 prompts — they define the format, not the task
PROMPTS_DIR = PROJECT_ROOT / "experiments" / "exp0_learnability" / "prompts"
TASKS_FILE = Path(__file__).parent / "tasks" / "tasks.json"
RESULTS_DIR = Path(__file__).parent / "results"

# Model configs: (cli_tool, model_flag, display_name)
MODELS = {
    "claude-haiku": ("claude", "haiku", "Claude Haiku 4.5"),
    "claude-sonnet": ("claude", "sonnet", "Claude Sonnet 4.5"),
    "codex": ("codex", "gpt-5.3-codex", "GPT-5.3 Codex"),
}
DEFAULT_MODELS = ["claude-haiku", "claude-sonnet", "codex"]


@dataclass
class TaskDef:
    id: str
    level: int
    description: str
    instruction: str
    expected_elements: list[str]
    operators_tested: list[str]


@dataclass
class RunResult:
    task_id: str
    condition: str
    model: str
    run_number: int
    output: str
    valid: bool
    errors: list[str]
    token_counts: dict | None
    latency_ms: int
    timestamp: str
    complexity_level: int
    operators_tested: list[str]


def load_tasks() -> list[TaskDef]:
    with open(TASKS_FILE) as f:
        data = json.load(f)
    return [
        TaskDef(
            id=t["id"],
            level=t["level"],
            description=t["description"],
            instruction=t["instruction"],
            expected_elements=t["expected_elements"],
            operators_tested=t.get("operators_tested", []),
        )
        for t in data["tasks"]
    ]


def load_prompt(condition: str) -> str:
    path = PROMPTS_DIR / f"{condition}.txt"
    with open(path) as f:
        return f.read().strip()


def call_claude(system_prompt: str, user_prompt: str, model: str) -> tuple[str, int]:
    """Call Claude CLI in print mode. Returns (output, latency_ms)."""
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    start = time.monotonic()
    result = subprocess.run(
        [
            "claude", "-p",
            "--system-prompt", system_prompt,
            "--model", model,
            "--no-session-persistence",
            "--tools", "",
        ],
        input=user_prompt,
        capture_output=True,
        text=True,
        timeout=120,
        env=env,
    )
    latency_ms = int((time.monotonic() - start) * 1000)

    if result.returncode != 0:
        raise RuntimeError(f"claude CLI failed (rc={result.returncode}): {result.stderr.strip()}")

    return result.stdout.strip(), latency_ms


def call_codex(system_prompt: str, user_prompt: str, model: str) -> tuple[str, int]:
    """Call Codex CLI in exec mode. Returns (output, latency_ms)."""
    import tempfile
    combined_prompt = f"{system_prompt}\n\n---\n\nTask: {user_prompt}"
    outfile = tempfile.mktemp(suffix=".txt")
    start = time.monotonic()
    try:
        result = subprocess.run(
            [
                "codex", "exec",
                "--model", model,
                "-o", outfile,
                combined_prompt,
            ],
            capture_output=True,
            text=True,
            timeout=180,
        )
        latency_ms = int((time.monotonic() - start) * 1000)

        if result.returncode != 0:
            stderr = result.stderr.strip()
            raise RuntimeError(f"codex CLI failed (rc={result.returncode}): {stderr}")

        with open(outfile) as f:
            output = f.read().strip()
    finally:
        if os.path.exists(outfile):
            os.unlink(outfile)

    return output, latency_ms


def call_llm(system_prompt: str, user_prompt: str, model_key: str) -> tuple[str, int]:
    """Dispatch to the right CLI tool based on model key."""
    cli_tool, model_flag, _ = MODELS[model_key]
    if cli_tool == "claude":
        return call_claude(system_prompt, user_prompt, model_flag)
    elif cli_tool == "codex":
        return call_codex(system_prompt, user_prompt, model_flag)
    else:
        raise ValueError(f"Unknown CLI tool: {cli_tool}")


def run_single(
    condition: str,
    task: TaskDef,
    model_key: str,
    run_number: int,
) -> RunResult:
    """Execute a single (condition, task, model, run) cell."""
    system_prompt = load_prompt(condition)
    user_prompt = (
        f"Task: {task.instruction}\n\n"
        f"Respond with ONLY the message in the required format. "
        f"Do not include explanations or commentary."
    )

    try:
        output, latency_ms = call_llm(system_prompt, user_prompt, model_key)
    except Exception as e:
        output = ""
        latency_ms = 0
        validation = {"valid": False, "errors": [f"CLI error: {e}"]}
    else:
        validation = validate_output(condition, output)

    # Token counting
    token_counts = None
    try:
        from lib.token_counter import count_tokens_multi
        token_counts = count_tokens_multi(output)
    except ImportError:
        pass

    return RunResult(
        task_id=task.id,
        condition=condition,
        model=model_key,
        run_number=run_number,
        output=output,
        valid=validation["valid"],
        errors=validation.get("errors", []),
        token_counts=token_counts,
        latency_ms=latency_ms,
        timestamp=datetime.now(timezone.utc).isoformat(),
        complexity_level=task.level,
        operators_tested=task.operators_tested,
    )


def save_results(results: list[RunResult], model_key: str):
    """Save results to JSON file."""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    outfile = RESULTS_DIR / f"exp3_{model_key}_{timestamp}.json"

    data = {
        "experiment": "exp3_compositionality",
        "grammar_version": "v0.1b",
        "model": model_key,
        "model_display": MODELS[model_key][2],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_runs": len(results),
        "valid_count": sum(1 for r in results if r.valid),
        "results": [asdict(r) for r in results],
    }

    with open(outfile, "w") as f:
        json.dump(data, f, indent=2)

    return outfile


def print_summary(results: list[RunResult]):
    """Print a summary table of results."""
    print("\n" + "=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)

    # Per-condition compliance
    conditions = sorted(set(r.condition for r in results))
    print(f"\n{'Condition':<28} {'Valid':>6} {'Total':>6} {'Rate':>7}")
    print("-" * 50)
    for c in conditions:
        c_results = [r for r in results if r.condition == c]
        valid = sum(1 for r in c_results if r.valid)
        total = len(c_results)
        rate = valid / total if total > 0 else 0
        print(f"  {c:<26} {valid:>6} {total:>6} {rate:>6.1%}")

    # Per-level compliance
    print(f"\n{'Level':<28} {'Valid':>6} {'Total':>6} {'Rate':>7}")
    print("-" * 50)
    for level_prefix in ["L1", "L2", "L3"]:
        l_results = [r for r in results if r.task_id.startswith(level_prefix)]
        valid = sum(1 for r in l_results if r.valid)
        total = len(l_results)
        rate = valid / total if total > 0 else 0
        print(f"  {level_prefix:<26} {valid:>6} {total:>6} {rate:>6.1%}")

    # Token counts
    has_tokens = any(r.token_counts for r in results if r.valid)
    if has_tokens:
        print(f"\n{'MEAN TOKENS (cl100k_base)':<28}")
        print("-" * 50)
        for c in conditions:
            c_results = [r for r in results if r.condition == c and r.valid and r.token_counts]
            if c_results:
                mean_tokens = sum(r.token_counts["cl100k_base"] for r in c_results) / len(c_results)
                print(f"  {c:<26} {mean_tokens:>8.1f}")

    # Errors
    error_results = [r for r in results if not r.valid]
    if error_results:
        print(f"\n{'ERRORS':=^70}")
        for r in error_results[:10]:
            print(f"  [{r.task_id}] {r.condition} run#{r.run_number}: {'; '.join(r.errors[:2])}")
        if len(error_results) > 10:
            print(f"  ... and {len(error_results) - 10} more")


def run_dry(conditions: list[str], tasks: list[TaskDef]):
    """Dry run: show what would be executed without calling any LLM."""
    print("=" * 60)
    print("Exp 3 Compositionality — DRY RUN")
    print("=" * 60)
    print(f"\nConditions: {len(conditions)}")
    for c in conditions:
        prompt = load_prompt(c)
        print(f"  - {c}: prompt {len(prompt)} chars")
    print(f"\nTasks: {len(tasks)}")
    for t in tasks:
        ops = ", ".join(t.operators_tested)
        print(f"  - [{t.id}] L{t.level}: {t.description} ({ops})")

    # Load annotations and show element counts
    ann_path = Path(__file__).parent / "tasks" / "element_annotations.json"
    with open(ann_path) as f:
        annotations = json.load(f)

    print(f"\nElement counts per task:")
    total_elements = 0
    total_cs = 0
    for task_ann in annotations["tasks"]:
        elem_count = task_ann["elements"]["count"]
        cs_count = task_ann["composition_structure"]["count"]
        total_elements += elem_count
        total_cs += cs_count
        print(f"  - [{task_ann['id']}] {elem_count} elements + {cs_count} composition-structure")
    print(f"  Total: {total_elements} elements + {total_cs} composition-structure")

    runs = 3  # prereg
    total_cells = len(conditions) * len(tasks) * runs
    print(f"\nTotal cells (3 runs): {len(conditions)} x {len(tasks)} x {runs} = {total_cells}")

    print(f"\nValidation check (empty outputs):")
    for c in conditions:
        result = validate_output(c, "")
        status = "PASS" if result["valid"] else f"FAIL ({result['errors']})"
        print(f"  - {c}: {status}")

    # Verify token counter
    try:
        from lib.token_counter import count_tokens, measure
        sample = "REQ(@a>@b): fetch() -> parse() -> store()"
        m = measure(sample)
        print(f"\nToken counter OK: '{sample}' = {m['tokens']} tokens ({m['encoding']})")
    except ImportError as e:
        print(f"\nToken counter NOT AVAILABLE: {e}")
        print("  Install: pip install tiktoken")

    # Verify CLI tools
    print("\nCLI tool check:")
    for name, cmd in [("claude", ["claude", "--version"]), ("codex", ["codex", "--version"])]:
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            version = r.stdout.strip().split("\n")[0] if r.stdout else "unknown"
            print(f"  - {name}: {version}")
        except FileNotFoundError:
            print(f"  - {name}: NOT FOUND")

    # Test composition extractor
    print("\nComposition extractor check:")
    try:
        from exp3_compositionality.scoring.composition_extractor import (
            extract_axon_composition,
            measure_nesting_depth,
        )
        test_out = 'REQ(@a>@b): x() -> y() -> z()'
        depth = measure_nesting_depth(test_out)
        print(f"  Nesting depth test: '{test_out}' = depth {depth}")
        print(f"  Extractor: OK")
    except Exception as e:
        print(f"  Extractor: FAILED ({e})")

    print("\nDry run complete. Use --all to execute.")


def main():
    parser = argparse.ArgumentParser(description="Exp 3: Compositionality")
    parser.add_argument("--dry-run", action="store_true", help="Show plan without executing")
    parser.add_argument("--condition", choices=CONDITIONS, help="Run single condition")
    parser.add_argument("--task", help="Run single task by ID")
    parser.add_argument("--all", action="store_true", help="Run all conditions x all tasks")
    parser.add_argument("--runs", type=int, default=1, help="Runs per cell (default: 1, prereg: 3)")
    parser.add_argument(
        "--model", action="append", dest="models", choices=list(MODELS.keys()),
        help="Model(s) to use (repeatable, default: all 3)",
    )
    args = parser.parse_args()

    tasks = load_tasks()

    if args.dry_run:
        conditions = CONDITIONS
        if args.condition:
            conditions = [args.condition]
        if args.task:
            tasks = [t for t in tasks if t.id == args.task]
        run_dry(conditions, tasks)
        return

    if not args.all and not args.condition:
        run_dry(CONDITIONS, tasks)
        return

    # Determine models and conditions
    models = args.models or DEFAULT_MODELS
    conditions = CONDITIONS
    if args.condition:
        conditions = [args.condition]
    if args.task:
        tasks = [t for t in tasks if t.id == args.task]

    total_cells = len(conditions) * len(tasks) * args.runs
    print(f"Exp 3 Compositionality — LIVE RUN")
    print(f"  Grammar version: v0.1b")
    print(f"  Conditions: {len(conditions)}")
    print(f"  Tasks: {len(tasks)}")
    print(f"  Runs per cell: {args.runs}")
    print(f"  Total cells per model: {total_cells}")
    print(f"  Models: {', '.join(models)}")
    print()

    for model_key in models:
        _, _, display_name = MODELS[model_key]
        print(f"\n{'=' * 70}")
        print(f"MODEL: {display_name} ({model_key})")
        print(f"{'=' * 70}")

        results: list[RunResult] = []
        cell = 0
        pass_count = 0
        start_time = time.monotonic()

        for run_num in range(1, args.runs + 1):
            for condition in conditions:
                for task in tasks:
                    cell += 1
                    elapsed = time.monotonic() - start_time
                    avg_per_cell = elapsed / cell if cell > 1 else 0
                    eta = avg_per_cell * (total_cells - cell)
                    eta_str = f" ETA {int(eta)}s" if cell > 1 else ""
                    label = f"[{cell}/{total_cells}]{eta_str} {condition}/{task.id} run#{run_num}"
                    print(f"  {label} ... ", end="", flush=True)

                    result = run_single(condition, task, model_key, run_num)
                    results.append(result)

                    if result.valid:
                        pass_count += 1
                    status = "PASS" if result.valid else "FAIL"
                    tokens = ""
                    if result.token_counts:
                        tokens = f" ({result.token_counts.get('cl100k_base', '?')} tok)"
                    running_rate = f" [{pass_count}/{cell} = {pass_count/cell:.0%}]"
                    print(f"{status} [{result.latency_ms}ms]{tokens}{running_rate}")

                    if not result.valid and result.errors:
                        for err in result.errors[:2]:
                            print(f"         {err}")

        # Save and summarize
        outfile = save_results(results, model_key)
        print(f"\nResults saved: {outfile}")
        print_summary(results)


if __name__ == "__main__":
    main()
