"""
Exp 3 Phase 2: Round-Trip Decomposition — Runner

Tests whether a different model can correctly decompose a composed message
back into its individual steps and relationships.

Cross-model pairs: Codex→Sonnet, Haiku→Codex, Sonnet→Haiku
Uses run #1 only, 1 output per (condition × task × model).

Usage:
    python3 experiments/exp3_compositionality/phase2/run.py --dry-run
    python3 experiments/exp3_compositionality/phase2/run.py --all
    python3 experiments/exp3_compositionality/phase2/run.py --all --limit 10
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

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "experiments"))

PHASE2_DIR = Path(__file__).parent
RESULTS_DIR = PHASE2_DIR / "results"
PROMPT_FILE = PHASE2_DIR / "decomposition_prompt.txt"
EXP3_RESULTS_DIR = PROJECT_ROOT / "experiments" / "exp3_compositionality" / "results"
ANNOTATIONS_FILE = PROJECT_ROOT / "experiments" / "exp3_compositionality" / "tasks" / "element_annotations.json"

# Cross-model pairing: original_model → decomposition_model
CROSS_PAIRS = {
    "codex": "claude-sonnet",
    "claude-haiku": "codex",
    "claude-sonnet": "claude-haiku",
}

# Model configs for CLI
MODELS = {
    "claude-haiku": ("claude", "haiku"),
    "claude-sonnet": ("claude", "sonnet"),
    "codex": ("codex", "gpt-5.3-codex"),
}

CONDITIONS = [
    "free_english", "structured_english", "instruction_matched_english",
    "json_fc", "fipa_acl", "axon", "aisp",
]


@dataclass
class DecompResult:
    task_id: str
    condition: str
    original_model: str
    decomp_model: str
    original_output: str
    decomp_output: str
    decomp_parsed: dict | None  # Parsed JSON if successful
    latency_ms: int
    timestamp: str
    complexity_level: int


def load_decomp_prompt() -> str:
    with open(PROMPT_FILE) as f:
        return f.read().strip()


def load_annotations() -> dict:
    with open(ANNOTATIONS_FILE) as f:
        return json.load(f)


def select_outputs() -> list[dict]:
    """Select 1 output per (condition × task × model), run #1 only.

    Returns list of {task_id, condition, model, output, complexity_level}.
    """
    selected = []
    seen = set()

    for path in sorted(EXP3_RESULTS_DIR.glob("*_scored*.json")):
        with open(path) as f:
            data = json.load(f)

        for r in data["results"]:
            if r["run_number"] != 1:
                continue
            if not r.get("valid", False):
                continue

            key = (r["task_id"], r["condition"], r["model"])
            if key in seen:
                continue
            seen.add(key)

            selected.append({
                "task_id": r["task_id"],
                "condition": r["condition"],
                "model": r["model"],
                "output": r["output"],
                "complexity_level": r.get("complexity_level", 0),
            })

    return selected


def call_claude(prompt: str, model: str) -> tuple[str, int]:
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    system = "You are a precise message analysis assistant. Output only the requested JSON."
    start = time.monotonic()
    result = subprocess.run(
        ["claude", "-p", "--system-prompt", system,
         "--model", model, "--no-session-persistence", "--tools", ""],
        input=prompt, capture_output=True, text=True, timeout=120, env=env,
    )
    latency = int((time.monotonic() - start) * 1000)
    if result.returncode != 0:
        raise RuntimeError(f"claude failed: {result.stderr.strip()}")
    return result.stdout.strip(), latency


def call_codex(prompt: str, model: str) -> tuple[str, int]:
    import tempfile
    combined = f"You are a precise message analysis assistant. Output only the requested JSON.\n\n{prompt}"
    outfile = tempfile.mktemp(suffix=".txt")
    start = time.monotonic()
    try:
        result = subprocess.run(
            ["codex", "exec", "--model", model, "-o", outfile, combined],
            capture_output=True, text=True, timeout=180,
        )
        latency = int((time.monotonic() - start) * 1000)
        if result.returncode != 0:
            raise RuntimeError(f"codex failed: {result.stderr.strip()}")
        with open(outfile) as f:
            output = f.read().strip()
    finally:
        if os.path.exists(outfile):
            os.unlink(outfile)
    return output, latency


def call_decomp(prompt: str, model_key: str) -> tuple[str, int]:
    tool, model_flag = MODELS[model_key]
    if tool == "claude":
        return call_claude(prompt, model_flag)
    return call_codex(prompt, model_flag)


def parse_decomp_response(response: str) -> dict | None:
    """Try to parse JSON from the decomposition response."""
    import re
    # Try to find JSON block
    json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass

    # Try direct JSON parse
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        pass

    # Try to find any JSON object
    json_match = re.search(r'\{.*\}', response, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(0))
        except json.JSONDecodeError:
            pass

    return None


def main():
    parser = argparse.ArgumentParser(
        description="Exp 3 Phase 2: Round-Trip Decomposition"
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--limit", type=int, default=0,
                        help="Max outputs to process (0=all)")
    parser.add_argument("--condition", help="Filter to single condition")
    args = parser.parse_args()

    outputs = select_outputs()
    print(f"Selected {len(outputs)} outputs (1 per condition × task × model, run #1)")

    if args.condition:
        outputs = [o for o in outputs if o["condition"] == args.condition]
        print(f"  Filtered to {args.condition}: {len(outputs)} outputs")

    by_cond = {}
    for o in outputs:
        by_cond[o["condition"]] = by_cond.get(o["condition"], 0) + 1
    for c in sorted(by_cond):
        print(f"  {c}: {by_cond[c]}")

    if args.dry_run or not args.all:
        print(f"\nCross-model pairs:")
        for orig, decomp in CROSS_PAIRS.items():
            n = sum(1 for o in outputs if o["model"] == orig)
            print(f"  {orig} → {decomp}: {n} outputs")
        total = len(outputs)
        print(f"\nTotal decomposition calls: {total}")
        return

    decomp_prompt_template = load_decomp_prompt()
    results = []
    cell = 0
    start_time = time.monotonic()

    for output_rec in outputs:
        if args.limit and cell >= args.limit:
            break

        orig_model = output_rec["model"]
        decomp_model = CROSS_PAIRS.get(orig_model)
        if not decomp_model:
            continue

        cell += 1
        elapsed = time.monotonic() - start_time
        avg = elapsed / cell if cell > 1 else 0
        total = len(outputs) if not args.limit else min(args.limit, len(outputs))
        eta = avg * (total - cell)
        eta_str = f" ETA {int(eta)}s" if cell > 1 else ""

        print(f"  [{cell}/{total}]{eta_str} {output_rec['condition']}/{output_rec['task_id']} "
              f"({orig_model}→{decomp_model}) ... ", end="", flush=True)

        prompt = (
            f"{decomp_prompt_template}\n\n"
            f"## Message to Analyze\n\n"
            f"```\n{output_rec['output']}\n```"
        )

        try:
            response, latency = call_decomp(prompt, decomp_model)
            parsed = parse_decomp_response(response)
        except Exception as e:
            response = f"ERROR: {e}"
            latency = 0
            parsed = None

        results.append(DecompResult(
            task_id=output_rec["task_id"],
            condition=output_rec["condition"],
            original_model=orig_model,
            decomp_model=decomp_model,
            original_output=output_rec["output"],
            decomp_output=response,
            decomp_parsed=parsed,
            latency_ms=latency,
            timestamp=datetime.now(timezone.utc).isoformat(),
            complexity_level=output_rec["complexity_level"],
        ))

        n_steps = len(parsed.get("steps", [])) if parsed else 0
        n_rels = len(parsed.get("relationships", [])) if parsed else 0
        status = f"{n_steps} steps, {n_rels} rels" if parsed else "PARSE FAIL"
        print(f"{status} [{latency}ms]")

    # Save
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    outfile = RESULTS_DIR / f"phase2_decomposition_{ts}.json"
    data = {
        "experiment": "exp3_compositionality_phase2",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_results": len(results),
        "parseable": sum(1 for r in results if r.decomp_parsed),
        "results": [asdict(r) for r in results],
    }
    with open(outfile, "w") as f:
        json.dump(data, f, indent=2)
    print(f"\nSaved: {outfile}")

    parseable = sum(1 for r in results if r.decomp_parsed)
    print(f"Parseable: {parseable}/{len(results)} ({parseable/len(results):.0%})")


if __name__ == "__main__":
    main()
