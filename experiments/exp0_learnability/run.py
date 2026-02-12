"""
Exp 0: Learnability Gate — Runner Script

Tests whether LLMs can produce valid output in each of the 6 experimental
conditions after seeing only the system prompt (zero-shot learnability).

Usage:
    python3 experiments/exp0_learnability/run.py --dry-run
    python3 experiments/exp0_learnability/run.py --condition axon --task L1-01
    python3 experiments/exp0_learnability/run.py --all
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass, asdict
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
    output: str
    valid: bool
    errors: list[str]
    token_counts: dict | None
    timestamp: str


def load_tasks() -> list[TaskDef]:
    with open(TASKS_FILE) as f:
        data = json.load(f)
    return [TaskDef(**t) for t in data["tasks"]]


def load_prompt(condition: str) -> str:
    path = PROMPTS_DIR / f"{condition}.txt"
    with open(path) as f:
        return f.read().strip()


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

    # Verify token counter is importable
    try:
        from lib.token_counter import count_tokens, measure
        sample = "QRY(@a>@b): status(@server)"
        m = measure(sample)
        print(f"\nToken counter OK: '{sample}' = {m['tokens']} tokens ({m['encoding']})")
    except ImportError as e:
        print(f"\nToken counter NOT AVAILABLE: {e}")
        print("  Install: pip install tiktoken")

    print("\nDry run complete. Use --all to execute (requires LLM API key).")


def main():
    parser = argparse.ArgumentParser(description="Exp 0: Learnability Gate")
    parser.add_argument("--dry-run", action="store_true", help="Show plan without executing")
    parser.add_argument("--condition", choices=CONDITIONS, help="Run single condition")
    parser.add_argument("--task", help="Run single task by ID")
    parser.add_argument("--all", action="store_true", help="Run all conditions x all tasks")
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

    if args.all:
        print("Full experiment run not yet implemented.")
        print("This requires LLM API integration (deferred until Exp 0 gate passes).")
        sys.exit(1)

    if args.condition:
        conditions = [args.condition]
        if args.task:
            tasks = [t for t in tasks if t.id == args.task]
        print(f"Single condition run not yet implemented.")
        print(f"Would run: {args.condition} x {len(tasks)} tasks")
        sys.exit(1)


if __name__ == "__main__":
    main()
