#!/usr/bin/env bash
# Second-run (run=1) replication firming for the M5 falsification campaign.
#
# Adds a SECOND independent run per cell on top of the original run=0 corpus, so
# the headline (per-model capability ladder + the large/code-model niche) is
# replication-backed rather than single-run. run_encode.py --runs 2 is resumable
# and skips the existing run=0 keys, so this only generates the new run=1 cells;
# run_decode.py then picks up the new cells with the fixed decoder, and analyze.py
# re-aggregates over BOTH runs (tighter CIs + test-retest variance).
#
# Auth: the M5 gateway token comes from the macOS Keychain via the `m5-auth` CLI
# (secret-safe; nothing on disk, nothing in the repo).
#
# Usage:
#   ./run_replication.sh qwen3-30b-instruct qwen3-coder-next-80b gpt-oss-120b   # headline batch
#   ./run_replication.sh gemma4 qwen35-a3b                                       # slow-tail best-effort
set -uo pipefail
cd "$(dirname "$0")"
eval "$(m5-auth --env)"   # sets M5_API_KEY + M5_BASE_URL

for m in "$@"; do
  echo "=== ENCODE run=1: $m  ($(date +%H:%M:%S)) ==="
  python3 run_encode.py --model "$m" --runs 2 --out results/encode.jsonl
done

echo "=== DECODE new cells (fixed decoder qwen3-30b-instruct)  ($(date +%H:%M:%S)) ==="
python3 run_decode.py --out results/decode.jsonl

echo "=== ANALYZE (pooled over run=0 + run=1)  ($(date +%H:%M:%S)) ==="
python3 analyze.py >/dev/null && echo "summary.md/json regenerated"
echo "=== REPLICATION BATCH DONE  ($(date +%H:%M:%S)) ==="
