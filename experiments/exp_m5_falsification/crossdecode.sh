#!/bin/bash
set -u
cd "$(dirname "$0")"
echo "=== CROSS-DECODE (receiver capability) $(date) ==="
echo ">>> strong reader: qwen3-coder-next-80b $(date +%H:%M:%S)"
python3 run_decode.py --decoder qwen3-coder-next-80b --in results/encode_axjs.jsonl --out results/decode_coder.jsonl
echo ">>> weak reader: qwen35-a3b (best-effort) $(date +%H:%M:%S)"
python3 run_decode.py --decoder qwen35-a3b --in results/encode_axjs.jsonl --out results/decode_weak.jsonl
echo "=== CROSS-DECODE DONE $(date) ==="
