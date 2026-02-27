#!/usr/bin/env python3
"""
Benchmarks 2 & 3: LLM Generation Head-to-Head + Home-Turf Comparison

Benchmark 2: Same agent-communication tasks, AXON vs AISP prompts, 3 models.
Benchmark 3: Agent-message tasks (AXON turf) + specification tasks (AISP turf).

Measures: validity, token count, semantic completeness (element checklist).

Usage:
    python3 experiments/exp_aisp_comparison/benchmark_23_runner.py
    python3 experiments/exp_aisp_comparison/benchmark_23_runner.py --dry-run
    python3 experiments/exp_aisp_comparison/benchmark_23_runner.py --model claude-haiku
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "experiments" / "lib"))

from condition_adapter import validate_output
from token_counter import count_tokens_multi


# ── Tasks ────────────────────────────────────────────────────────────

@dataclass
class Task:
    id: str
    category: str  # "agent-message" (AXON turf) or "specification" (AISP turf)
    instruction: str
    elements: list[str]  # semantic elements to check for


TASKS = [
    # === Benchmark 2 + 3a: Agent-message tasks (AXON's home turf) ===
    Task(
        id="AM-01",
        category="agent-message",
        instruction="Agent A asks Agent B for the current status of the web server named 'prod-web-3'. Include a message ID and protocol version.",
        elements=["sender", "receiver", "intent_query", "server_name", "message_id", "protocol_version"],
    ),
    Task(
        id="AM-02",
        category="agent-message",
        instruction="Agent B replies to Agent A's message 'm1' with server status: healthy, uptime 99.7%, response time 45ms. Include reply reference.",
        elements=["sender", "receiver", "intent_inform", "health_status", "uptime_value", "response_time", "reply_reference"],
    ),
    Task(
        id="AM-03",
        category="agent-message",
        instruction="Agent A proposes to Agent B: run a load test on the staging environment, estimated cost $2.50, estimated duration 45 minutes.",
        elements=["sender", "receiver", "intent_propose", "task_description", "cost_value", "duration_value"],
    ),
    Task(
        id="AM-04",
        category="agent-message",
        instruction="Monitoring agent broadcasts an alert to all agents: disk usage at 94% on storage-1, severity critical, affects backup-service and log-service.",
        elements=["sender", "receiver_broadcast", "intent_alert", "disk_usage_value", "severity_critical", "affected_services"],
    ),
    Task(
        id="AM-05",
        category="agent-message",
        instruction="Agent B reports an error to Agent A: connection timeout on api-gateway, caused by DNS failure on resolver dns-1, caused by network partition in zone-b.",
        elements=["sender", "receiver", "intent_error", "timeout_error", "dns_cause", "partition_root_cause"],
    ),

    # === Benchmark 3b: Specification tasks (AISP's home turf) ===
    Task(
        id="SP-01",
        category="specification",
        instruction="Write a formal specification for a tic-tac-toe game. Define the types (Player, Cell, Board), the rules (valid moves, win conditions), and a function to check if the game is over.",
        elements=["player_type", "cell_type", "board_type", "valid_move_rule", "win_condition", "game_over_function"],
    ),
    Task(
        id="SP-02",
        category="specification",
        instruction="Write a formal specification for a simple banking system. Define types for Account and Transaction, rules for minimum balance ($0) and maximum withdrawal ($10,000), and functions for deposit and withdraw.",
        elements=["account_type", "transaction_type", "min_balance_rule", "max_withdrawal_rule", "deposit_function", "withdraw_function"],
    ),
    Task(
        id="SP-03",
        category="specification",
        instruction="Write a formal specification for a task scheduling system. Define types for Task (with priority 1-5 and deadline) and Worker, rules for task assignment (one task per worker, respect priority), and a function to find the next unassigned highest-priority task.",
        elements=["task_type", "worker_type", "one_task_rule", "priority_ordering", "assignment_function", "next_task_function"],
    ),
]


# ── Model Invocation ─────────────────────────────────────────────────

def invoke_claude(system_prompt: str, user_prompt: str, model: str) -> tuple[str, int]:
    """Invoke Claude via CLI. Returns (output, latency_ms)."""
    env = os.environ.copy()
    env.pop("CLAUDECODE", None)

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
    latency = int((time.monotonic() - start) * 1000)
    output = result.stdout.strip() if result.returncode == 0 else f"ERROR: {result.stderr.strip()}"
    return output, latency


def invoke_codex(system_prompt: str, user_prompt: str, model: str = "gpt-5.3-codex") -> tuple[str, int]:
    """Invoke Codex via CLI. Returns (output, latency_ms)."""
    combined = f"{system_prompt}\n\n---\n\n{user_prompt}"

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        outfile = f.name

    start = time.monotonic()
    try:
        result = subprocess.run(
            ["codex", "exec", "--model", model, "-o", outfile, combined],
            capture_output=True,
            text=True,
            timeout=180,
        )
        latency = int((time.monotonic() - start) * 1000)
        if result.returncode == 0 and os.path.exists(outfile):
            output = Path(outfile).read_text().strip()
        else:
            output = f"ERROR: {result.stderr.strip()}"
    finally:
        if os.path.exists(outfile):
            os.unlink(outfile)

    return output, latency


def invoke_model(system_prompt: str, user_prompt: str, model: str) -> tuple[str, int]:
    """Dispatch to correct CLI tool."""
    if model.startswith("claude"):
        claude_model = model.replace("claude-", "")
        return invoke_claude(system_prompt, user_prompt, claude_model)
    elif "codex" in model:
        return invoke_codex(system_prompt, user_prompt, model)
    else:
        return f"ERROR: Unknown model {model}", 0


# ── Prompts ──────────────────────────────────────────────────────────

def load_prompt(condition: str) -> str:
    """Load the system prompt for a condition."""
    prompts_dir = PROJECT_ROOT / "experiments" / "exp0_learnability" / "prompts"
    path = prompts_dir / f"{condition}.txt"
    return path.read_text().strip()


# For spec tasks, we need slightly different framing
AXON_SPEC_ADDENDUM = """

For specification tasks, express everything as AXON messages. Routing is ALWAYS required.

Rules:
- Every message MUST have routing: INF(@spec>@reader): content
- Use lists [] for ordered collections: types: [#A{...}, #B{...}]
- Use records {} for named fields ONLY: rules: {name: expr, name2: expr2}
- Record keys must be plain identifiers, NOT tags
- Quantifiers use function syntax: forall($x: Type, predicate($x))
- Arithmetic works: balance + amount, price * qty, x >= 0

Example specification:
[id:"spec-1", %%:1]
INF(@spec>@reader): #BankSpec{
  types: [
    #Account{id: string, balance: number},
    #Transaction{id: string, amount: number}
  ],
  rules: {
    min_balance: balance >= 0usd,
    max_withdraw: amount <= 10000usd
  },
  functions: {
    deposit: deposit($acct, $amt) -> set($acct.balance, $acct.balance + $amt),
    withdraw: withdraw($acct, $amt) -> if($acct.balance >= $amt, set($acct.balance, $acct.balance - $amt), #error{msg:"insufficient funds"})
  }
}
"""

AISP_SPEC_ADDENDUM = """

For specification tasks, use AISP's block structure naturally:
- ⟦Σ:Types⟧ for type definitions
- ⟦Γ:Rules⟧ for constraints and invariants
- ⟦Λ:Funcs⟧ for function definitions
"""


# ── Runner ───────────────────────────────────────────────────────────

@dataclass
class RunResult:
    task_id: str
    category: str
    condition: str
    model: str
    output: str
    valid: bool
    errors: list[str]
    token_counts: dict | None
    latency_ms: int
    timestamp: str
    elements: list[str]


def run_single(task: Task, condition: str, model: str, dry_run: bool = False) -> RunResult:
    """Run a single task with a single condition and model."""
    system_prompt = load_prompt(condition)

    # Add spec addendum for specification tasks
    if task.category == "specification":
        if condition == "axon":
            system_prompt += AXON_SPEC_ADDENDUM
        elif condition == "aisp":
            system_prompt += AISP_SPEC_ADDENDUM

    user_prompt = (
        f"Task: {task.instruction}\n\n"
        f"Respond with ONLY the output in the required format. "
        f"Do not include explanations or commentary."
    )

    if dry_run:
        output = f"[DRY RUN] Would invoke {model} with {condition} prompt for {task.id}"
        latency = 0
    else:
        output, latency = invoke_model(system_prompt, user_prompt, model)

    # Validate
    validation = validate_output(condition, output)
    tokens = count_tokens_multi(output) if output and not output.startswith("ERROR") else None

    return RunResult(
        task_id=task.id,
        category=task.category,
        condition=condition,
        model=model,
        output=output,
        valid=validation["valid"],
        errors=validation.get("errors", []),
        token_counts=tokens,
        latency_ms=latency,
        timestamp=datetime.now(timezone.utc).isoformat(),
        elements=task.elements,
    )


def run_all(models: list[str], dry_run: bool = False) -> list[RunResult]:
    """Run all tasks across both conditions and specified models."""
    conditions = ["axon", "aisp"]
    results = []
    total = len(TASKS) * len(conditions) * len(models)
    done = 0

    for task in TASKS:
        for condition in conditions:
            for model in models:
                done += 1
                print(f"  [{done}/{total}] {task.id} | {condition:<5} | {model}")
                result = run_single(task, condition, model, dry_run)
                results.append(result)
                if not dry_run:
                    status = "VALID" if result.valid else f"INVALID: {result.errors}"
                    tok = result.token_counts.get("cl100k_base", "?") if result.token_counts else "?"
                    print(f"           {status} | {tok} tokens | {result.latency_ms}ms")

    return results


# ── Analysis ─────────────────────────────────────────────────────────

def analyze_results(results: list[RunResult]):
    """Print analysis of benchmark results."""

    print("\n" + "=" * 80)
    print("BENCHMARK 2: Agent-Message Tasks (AXON's Home Turf)")
    print("=" * 80)

    am_results = [r for r in results if r.category == "agent-message"]
    _print_condition_summary(am_results, "agent-message")

    print("\n" + "=" * 80)
    print("BENCHMARK 3: Specification Tasks (AISP's Home Turf)")
    print("=" * 80)

    sp_results = [r for r in results if r.category == "specification"]
    _print_condition_summary(sp_results, "specification")

    # Combined summary
    print("\n" + "=" * 80)
    print("COMBINED SUMMARY")
    print("=" * 80)
    _print_condition_summary(results, "all")

    # Home turf analysis
    print("\n  HOME-TURF ANALYSIS:")
    for category, label in [("agent-message", "Agent messages (AXON turf)"),
                            ("specification", "Specifications (AISP turf)")]:
        cat_results = [r for r in results if r.category == category]
        axon_toks = [r.token_counts["cl100k_base"] for r in cat_results
                     if r.condition == "axon" and r.token_counts and r.valid]
        aisp_toks = [r.token_counts["cl100k_base"] for r in cat_results
                     if r.condition == "aisp" and r.token_counts and r.valid]

        if axon_toks and aisp_toks:
            axon_mean = sum(axon_toks) / len(axon_toks)
            aisp_mean = sum(aisp_toks) / len(aisp_toks)
            ratio = aisp_mean / axon_mean if axon_mean > 0 else float("inf")
            print(f"\n  {label}:")
            print(f"    AXON mean: {axon_mean:.0f} tokens (N={len(axon_toks)} valid)")
            print(f"    AISP mean: {aisp_mean:.0f} tokens (N={len(aisp_toks)} valid)")
            print(f"    Ratio: AISP uses {ratio:.1f}x more tokens")
        else:
            print(f"\n  {label}: insufficient valid outputs to compare")


def _print_condition_summary(results: list[RunResult], label: str):
    """Print summary table for a set of results."""
    conditions = ["axon", "aisp"]

    print(f"\n  {'Condition':<8} {'Valid':>6} {'Total':>6} {'Rate':>7} "
          f"{'Mean Tok':>9} {'Med Tok':>8} {'Min':>5} {'Max':>5}")
    print("  " + "-" * 62)

    for cond in conditions:
        cr = [r for r in results if r.condition == cond]
        if not cr:
            continue
        n_valid = sum(1 for r in cr if r.valid)
        n_total = len(cr)
        rate = n_valid / n_total if n_total > 0 else 0

        toks = [r.token_counts["cl100k_base"] for r in cr if r.token_counts and r.valid]
        if toks:
            mean_t = sum(toks) / len(toks)
            sorted_t = sorted(toks)
            med_t = sorted_t[len(sorted_t) // 2]
            min_t = min(toks)
            max_t = max(toks)
            print(f"  {cond:<8} {n_valid:>6} {n_total:>6} {rate:>7.0%} "
                  f"{mean_t:>9.0f} {med_t:>8} {min_t:>5} {max_t:>5}")
        else:
            print(f"  {cond:<8} {n_valid:>6} {n_total:>6} {rate:>7.0%} "
                  f"{'n/a':>9} {'n/a':>8} {'n/a':>5} {'n/a':>5}")

    # Per-model breakdown
    models = sorted(set(r.model for r in results))
    if len(models) > 1:
        print(f"\n  Per-model breakdown:")
        for model in models:
            print(f"\n  {model}:")
            for cond in conditions:
                cr = [r for r in results if r.condition == cond and r.model == model]
                toks = [r.token_counts["cl100k_base"] for r in cr if r.token_counts and r.valid]
                n_valid = sum(1 for r in cr if r.valid)
                if toks:
                    mean_t = sum(toks) / len(toks)
                    print(f"    {cond:<8} valid={n_valid}/{len(cr)}  mean={mean_t:.0f} tok")
                else:
                    print(f"    {cond:<8} valid={n_valid}/{len(cr)}  no valid outputs")


# ── Main ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Benchmarks 2 & 3: LLM Generation")
    parser.add_argument("--dry-run", action="store_true", help="Don't invoke models")
    parser.add_argument("--model", type=str, nargs="+",
                        default=["claude-haiku", "claude-sonnet", "codex"],
                        help="Models to test")
    args = parser.parse_args()

    # Normalize model names
    models = []
    for m in args.model:
        if m == "codex":
            models.append("gpt-5.3-codex")
        elif m.startswith("claude-"):
            models.append(m)
        else:
            models.append(m)

    print("=" * 80)
    print("BENCHMARKS 2 & 3: LLM Generation — AXON vs AISP")
    print("=" * 80)
    print(f"\n  Models: {models}")
    print(f"  Tasks: {len(TASKS)} ({sum(1 for t in TASKS if t.category == 'agent-message')} agent-message, "
          f"{sum(1 for t in TASKS if t.category == 'specification')} specification)")
    print(f"  Conditions: axon, aisp")
    print(f"  Total runs: {len(TASKS) * 2 * len(models)}")
    if args.dry_run:
        print(f"  MODE: DRY RUN\n")
    else:
        print()

    results = run_all(models, dry_run=args.dry_run)

    if not args.dry_run:
        analyze_results(results)

        # Save results
        out_path = Path(__file__).parent / "benchmark_23_results.json"
        with open(out_path, "w") as f:
            json.dump({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "models": models,
                "results": [asdict(r) for r in results],
            }, f, indent=2)
        print(f"\n  Results saved to {out_path}")
    else:
        print(f"\n  Dry run complete. {len(results)} runs would execute.")


if __name__ == "__main__":
    main()
