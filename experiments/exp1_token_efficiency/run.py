"""
Exp 1: Token Efficiency — Orchestrator

Coordinates scoring of Exp 0 outputs and statistical analysis.

Usage:
    python3 experiments/exp1_token_efficiency/run.py --dry-run
    python3 experiments/exp1_token_efficiency/run.py --score --track a
    python3 experiments/exp1_token_efficiency/run.py --score --track b
    python3 experiments/exp1_token_efficiency/run.py --analyze
    python3 experiments/exp1_token_efficiency/run.py --all --track a
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

EXP1_DIR = Path(__file__).resolve().parent
SCORING_SCRIPT = EXP1_DIR / "scoring" / "score.py"
ANALYSIS_SCRIPT = EXP1_DIR / "analysis" / "analyze.py"


def run_dry(args):
    """Dry run: show what would happen."""
    cmd = [sys.executable, str(SCORING_SCRIPT), "--dry-run", "--track", args.track]
    subprocess.run(cmd)


def run_score(args):
    """Score Exp 0 outputs."""
    cmd = [sys.executable, str(SCORING_SCRIPT), "--score", "--track", args.track]
    if args.seed:
        cmd.extend(["--seed", str(args.seed)])
    if args.limit:
        cmd.extend(["--limit", str(args.limit)])
    if args.models:
        for m in args.models:
            cmd.extend(["--model", m])
    subprocess.run(cmd)


def run_analyze(args):
    """Run statistical analysis on scored results."""
    cmd = [sys.executable, str(ANALYSIS_SCRIPT), "--all"]
    subprocess.run(cmd)


def main():
    parser = argparse.ArgumentParser(description="Exp 1: Token Efficiency Orchestrator")
    parser.add_argument("--dry-run", action="store_true", help="Show plan without executing")
    parser.add_argument("--score", action="store_true", help="Score Exp 0 outputs")
    parser.add_argument("--analyze", action="store_true", help="Run statistical analysis")
    parser.add_argument("--all", action="store_true", help="Score + analyze")
    parser.add_argument("--track", choices=["a", "b"], default="a",
                        help="Element track (default: a)")
    parser.add_argument("--model", action="append", dest="models",
                        choices=["claude-haiku", "claude-sonnet", "codex"],
                        help="Model(s) to score (repeatable, default: all)")
    parser.add_argument("--limit", type=int, default=0,
                        help="Max outputs to score this run (0=all)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    if args.dry_run or (not args.score and not args.analyze and not args.all):
        run_dry(args)
        return

    if args.score or args.all:
        run_score(args)

    if args.analyze or args.all:
        run_analyze(args)


if __name__ == "__main__":
    main()
