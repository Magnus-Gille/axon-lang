#!/bin/bash
# Orchestrator for the M5 falsification campaign.
# The M5 box serves ONE model at a time (multi-minute cold-swaps) and rejects
# concurrent requests (503). So everything is strictly serial and phased:
# encode ALL models, THEN decode (one fixed model), THEN analyze. We checkpoint
# after a single-run pass so a complete dataset exists even if the replication
# pass is truncated.
set -u
cd "$(dirname "$0")"
RES=results
mkdir -p "$RES"
# Fast/reliable models first; slow thinking model (qwen35-a3b) last.
MODELS="qwen3-30b-instruct gemma4 qwen3-coder-next-80b gpt-oss-120b qwen35-a3b"
DECODER=qwen3-30b-instruct

stamp(){ date '+%H:%M:%S'; }

echo "===== M5 FALSIFICATION RUN start $(date) ====="

echo "===== PASS 1 (runs=1 — full matrix coverage) $(stamp) ====="
for m in $MODELS; do
  echo ">>> [encode p1] $m $(stamp)"
  python3 run_encode.py --model "$m" --runs 1 --out "$RES/encode.jsonl"
done
echo ">>> [decode p1] $(stamp)"
python3 run_decode.py --decoder "$DECODER" --in "$RES/encode.jsonl" --out "$RES/decode.jsonl"
echo ">>> [analyze p1] $(stamp)"
python3 analyze.py --enc "$RES/encode.jsonl" --dec "$RES/decode.jsonl" --out "$RES/summary.md" >/dev/null
echo "===== PASS 1 COMPLETE — interim summary written $(stamp) ====="

echo "===== PASS 2 (runs=2 — replication) $(stamp) ====="
for m in $MODELS; do
  echo ">>> [encode p2] $m $(stamp)"
  python3 run_encode.py --model "$m" --runs 2 --out "$RES/encode.jsonl"
done
echo ">>> [decode p2] $(stamp)"
python3 run_decode.py --decoder "$DECODER" --in "$RES/encode.jsonl" --out "$RES/decode.jsonl"
echo ">>> [analyze p2] $(stamp)"
python3 analyze.py --enc "$RES/encode.jsonl" --dec "$RES/decode.jsonl" --out "$RES/summary.md" >/dev/null

echo "===== ALL DONE $(date) ====="
