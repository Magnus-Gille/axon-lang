"""
JSON + Contracts — Data Generation Runner

Generates 81 cells (9 tasks × 3 models × 3 runs) using the JSON+Contracts
condition on Exp 3 compositionality tasks.

Reuses Exp 3 infrastructure (tasks, prompts, CLI tools).

Usage:
    python3 experiments/exp_json_contracts/run.py --dry-run
    python3 experiments/exp_json_contracts/run.py --all
    python3 experiments/exp_json_contracts/run.py --all --model codex
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

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "experiments"))

from lib.condition_adapter import validate_output
from lib.token_counter import count_tokens_multi

# Reuse Exp 3 tasks
TASKS_FILE = PROJECT_ROOT / "experiments" / "exp3_compositionality" / "tasks" / "tasks.json"
PROMPTS_DIR = PROJECT_ROOT / "experiments" / "exp0_learnability" / "prompts"
RESULTS_DIR = Path(__file__).parent / "results"

CONDITION = "json_contracts"

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
            id=t["id"], level=t["level"],
            description=t["description"],
            instruction=t["instruction"],
            operators_tested=t.get("operators_tested", []),
        )
        for t in data["tasks"]
    ]


def load_prompt() -> str:
    path = PROMPTS_DIR / f"{CONDITION}.txt"
    with open(path) as f:
        return f.read().strip()


def call_claude(system_prompt: str, user_prompt: str, model: str) -> tuple[str, int]:
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    start = time.monotonic()
    result = subprocess.run(
        ["claude", "-p", "--system-prompt", system_prompt,
         "--model", model, "--no-session-persistence", "--tools", ""],
        input=user_prompt, capture_output=True, text=True, timeout=120, env=env,
    )
    latency_ms = int((time.monotonic() - start) * 1000)
    if result.returncode != 0:
        raise RuntimeError(f"claude CLI failed: {result.stderr.strip()}")
    return result.stdout.strip(), latency_ms


def call_codex(system_prompt: str, user_prompt: str, model: str) -> tuple[str, int]:
    import tempfile
    combined = f"{system_prompt}\n\n---\n\nTask: {user_prompt}"
    outfile = tempfile.mktemp(suffix=".txt")
    start = time.monotonic()
    try:
        result = subprocess.run(
            ["codex", "exec", "--model", model, "-o", outfile, combined],
            capture_output=True, text=True, timeout=180,
        )
        latency_ms = int((time.monotonic() - start) * 1000)
        if result.returncode != 0:
            raise RuntimeError(f"codex CLI failed: {result.stderr.strip()}")
        with open(outfile) as f:
            output = f.read().strip()
    finally:
        if os.path.exists(outfile):
            os.unlink(outfile)
    return output, latency_ms


def call_llm(system_prompt: str, user_prompt: str, model_key: str) -> tuple[str, int]:
    cli_tool, model_flag, _ = MODELS[model_key]
    if cli_tool == "claude":
        return call_claude(system_prompt, user_prompt, model_flag)
    elif cli_tool == "codex":
        return call_codex(system_prompt, user_prompt, model_flag)
    raise ValueError(f"Unknown CLI tool: {cli_tool}")


def run_single(task: TaskDef, model_key: str, run_number: int,
               system_prompt: str) -> RunResult:
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
        validation = validate_output(CONDITION, output)

    token_counts = None
    try:
        token_counts = count_tokens_multi(output)
    except Exception:
        pass

    return RunResult(
        task_id=task.id,
        condition=CONDITION,
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


def main():
    parser = argparse.ArgumentParser(
        description="JSON + Contracts — Data Generation"
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--model", action="append", dest="models",
                        choices=list(MODELS.keys()))
    args = parser.parse_args()

    tasks = load_tasks()
    system_prompt = load_prompt()

    if args.dry_run or not args.all:
        print("JSON + Contracts — DRY RUN")
        print(f"  Condition: {CONDITION}")
        print(f"  System prompt: {len(system_prompt)} chars")
        print(f"  Tasks: {len(tasks)}")
        for t in tasks:
            print(f"    [{t.id}] L{t.level}: {t.description}")
        total = len(tasks) * args.runs
        print(f"  Cells per model: {total}")
        print(f"  Total (3 models): {total * 3}")

        # Validate empty output
        v = validate_output(CONDITION, "")
        print(f"\n  Empty output validation: {'PASS' if not v['valid'] else 'UNEXPECTED PASS'}")

        # Test with a valid contract
        test = json.dumps({
            "performative": "request",
            "from": "a", "to": "b",
            "preconditions": ["ready"],
            "postconditions": ["done"],
            "lifecycle_stage": "execution",
            "content": {"action": "test"},
        })
        v2 = validate_output(CONDITION, test)
        print(f"  Valid contract: {'PASS' if v2['valid'] else 'FAIL: ' + str(v2['errors'])}")
        return

    models = args.models or DEFAULT_MODELS
    print(f"JSON + Contracts — LIVE RUN")
    print(f"  Tasks: {len(tasks)}, Runs: {args.runs}, Models: {', '.join(models)}")

    for model_key in models:
        _, _, display = MODELS[model_key]
        print(f"\n{'=' * 70}")
        print(f"MODEL: {display}")
        print(f"{'=' * 70}")

        results = []
        total_cells = len(tasks) * args.runs
        cell = 0
        start = time.monotonic()

        for run_num in range(1, args.runs + 1):
            for task in tasks:
                cell += 1
                elapsed = time.monotonic() - start
                avg = elapsed / cell if cell > 1 else 0
                eta = avg * (total_cells - cell)
                eta_str = f" ETA {int(eta)}s" if cell > 1 else ""
                print(f"  [{cell}/{total_cells}]{eta_str} {task.id} run#{run_num} ... ",
                      end="", flush=True)

                result = run_single(task, model_key, run_num, system_prompt)
                results.append(result)

                status = "PASS" if result.valid else "FAIL"
                toks = f" ({result.token_counts.get('cl100k_base', '?')} tok)" if result.token_counts else ""
                print(f"{status} [{result.latency_ms}ms]{toks}")
                if not result.valid:
                    for err in result.errors[:2]:
                        print(f"         {err}")

        # Save
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        outfile = RESULTS_DIR / f"json_contracts_{model_key}_{ts}.json"
        data = {
            "experiment": "exp_json_contracts",
            "condition": CONDITION,
            "model": model_key,
            "model_display": display,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_runs": len(results),
            "valid_count": sum(1 for r in results if r.valid),
            "results": [asdict(r) for r in results],
        }
        with open(outfile, "w") as f:
            json.dump(data, f, indent=2)
        print(f"\nSaved: {outfile}")

        valid_count = sum(1 for r in results if r.valid)
        print(f"  Valid: {valid_count}/{len(results)} ({valid_count/len(results):.0%})")


if __name__ == "__main__":
    main()
