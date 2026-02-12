"""
Exp 0: Learnability Gate — Runner Script

Tests whether LLMs can produce valid output in each of the 6 experimental
conditions after seeing only the system prompt (zero-shot learnability).

Uses CLI tools (claude, codex) instead of direct API calls — leverages
existing subscriptions instead of per-token API costs.

Usage:
    python3 experiments/exp0_learnability/run.py --dry-run
    python3 experiments/exp0_learnability/run.py --condition axon --task L1-01
    python3 experiments/exp0_learnability/run.py --all
    python3 experiments/exp0_learnability/run.py --all --runs 3
    python3 experiments/exp0_learnability/run.py --all --model claude-haiku
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path

# Add project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "experiments"))

from lib.condition_adapter import CONDITIONS, validate_output


PROMPTS_DIR = Path(__file__).parent / "prompts"
TASKS_FILE = Path(__file__).parent / "tasks" / "tasks.json"
RESULTS_DIR = Path(__file__).parent / "results"

# Model configs: (cli_tool, model_flag, display_name)
MODELS = {
    "claude-haiku": ("claude", "haiku", "Claude Haiku 4.5"),
    "claude-sonnet": ("claude", "sonnet", "Claude Sonnet 4.5"),
    "codex": ("codex", "gpt-5.3-codex", "GPT-5.3 Codex"),
}
DEFAULT_MODELS = ["claude-haiku", "codex"]


@dataclass
class TaskDef:
    id: str
    level: int
    description: str
    instruction: str
    expected_elements: list[str]


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


def load_tasks() -> list[TaskDef]:
    with open(TASKS_FILE) as f:
        data = json.load(f)
    return [TaskDef(**t) for t in data["tasks"]]


def load_prompt(condition: str) -> str:
    path = PROMPTS_DIR / f"{condition}.txt"
    with open(path) as f:
        return f.read().strip()


def call_claude(system_prompt: str, user_prompt: str, model: str) -> tuple[str, int]:
    """Call Claude CLI in print mode. Returns (output, latency_ms)."""
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
    )


def save_results(results: list[RunResult], model_key: str):
    """Save results to JSON file."""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    outfile = RESULTS_DIR / f"exp0_{model_key}_{timestamp}.json"

    data = {
        "experiment": "exp0_learnability",
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
        marker = " ***" if c == "axon" and rate < 0.8 else ""
        print(f"  {c:<26} {valid:>6} {total:>6} {rate:>6.1%}{marker}")

    # Per-level compliance
    print(f"\n{'Level':<28} {'Valid':>6} {'Total':>6} {'Rate':>7}")
    print("-" * 50)
    for level_prefix in ["L1", "L2", "L3"]:
        l_results = [r for r in results if r.task_id.startswith(level_prefix)]
        valid = sum(1 for r in l_results if r.valid)
        total = len(l_results)
        rate = valid / total if total > 0 else 0
        print(f"  {level_prefix:<26} {valid:>6} {total:>6} {rate:>6.1%}")

    # Gate check
    axon_results = [r for r in results if r.condition == "axon"]
    json_results = [r for r in results if r.condition == "json_fc"]
    axon_rate = sum(1 for r in axon_results if r.valid) / len(axon_results) if axon_results else 0
    json_rate = sum(1 for r in json_results if r.valid) / len(json_results) if json_results else 0

    print(f"\n{'GATE CHECK':=^70}")
    print(f"  AXON compliance rate:    {axon_rate:.1%} (threshold: >= 80%)")
    print(f"  JSON FC compliance rate: {json_rate:.1%} (AXON must not be worse)")
    if axon_rate >= 0.8:
        print("  >> GATE: PASS")
    else:
        print("  >> GATE: FAIL — AXON below 80% threshold")

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
        print(f"\n{'ERRORS ({len(error_results)} failures)':=^70}")
        for r in error_results:
            print(f"  [{r.task_id}] {r.condition} run#{r.run_number}: {'; '.join(r.errors)}")


def run_dry(conditions: list[str], tasks: list[TaskDef]):
    """Dry run: show what would be executed without calling any LLM."""
    print("=" * 60)
    print("Exp 0 Learnability — DRY RUN")
    print("=" * 60)
    print(f"\nConditions: {len(conditions)}")
    for c in conditions:
        prompt = load_prompt(c)
        print(f"  - {c}: prompt {len(prompt)} chars")
    print(f"\nTasks: {len(tasks)}")
    for t in tasks:
        print(f"  - [{t.id}] L{t.level}: {t.description}")
    print(f"\nTotal runs: {len(conditions)} x {len(tasks)} = {len(conditions) * len(tasks)}")
    print("\nValidation check (empty outputs):")
    for c in conditions:
        result = validate_output(c, "")
        status = "PASS" if result["valid"] else f"FAIL ({result['errors']})"
        print(f"  - {c}: {status}")

    # Verify token counter
    try:
        from lib.token_counter import count_tokens, measure
        sample = "QRY(@a>@b): status(@server)"
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

    print("\nDry run complete. Use --all to execute.")


def main():
    parser = argparse.ArgumentParser(description="Exp 0: Learnability Gate")
    parser.add_argument("--dry-run", action="store_true", help="Show plan without executing")
    parser.add_argument("--condition", choices=CONDITIONS, help="Run single condition")
    parser.add_argument("--task", help="Run single task by ID")
    parser.add_argument("--all", action="store_true", help="Run all conditions x all tasks")
    parser.add_argument("--runs", type=int, default=1, help="Runs per cell (default: 1, prereg: 3)")
    parser.add_argument(
        "--model", action="append", dest="models", choices=list(MODELS.keys()),
        help="Model(s) to use (repeatable, default: claude-haiku + codex-o4-mini)",
    )
    args = parser.parse_args()

    tasks = load_tasks()

    if args.dry_run or (not args.all and not args.condition):
        conditions = CONDITIONS
        if args.condition:
            conditions = [args.condition]
        if args.task:
            tasks = [t for t in tasks if t.id == args.task]
        run_dry(conditions, tasks)
        return

    # Determine models and conditions
    models = args.models or DEFAULT_MODELS
    conditions = CONDITIONS
    if args.condition:
        conditions = [args.condition]
    if args.task:
        tasks = [t for t in tasks if t.id == args.task]

    total_cells = len(conditions) * len(tasks) * args.runs
    print(f"Exp 0 Learnability — LIVE RUN")
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
