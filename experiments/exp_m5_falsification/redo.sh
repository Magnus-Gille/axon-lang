#!/bin/bash
# Redo ONLY the budget-truncated cells (finish_reason=length) for the two
# reasoning-heavy models, with much larger token budgets. The clean models
# (qwen3-30b, qwen3-coder, gpt-oss-120b) are left untouched. run_encode resumes
# by key, so after we drop the truncated cells it refills exactly those.
set -u
cd "$(dirname "$0")"
RES=results
echo "===== REDO truncated cells $(date) ====="
python3 - <<'PY'
import json
p='results/encode.jsonl'
lines=open(p).readlines()
keep=[]
dropped=0
for l in lines:
    r=json.loads(l)
    if r['model'] in ('gemma4','qwen35-a3b') and r.get('finish_reason')=='length':
        dropped+=1
        continue
    keep.append(l)
open(p,'w').writelines(keep)
print(f">>> filtered: kept {len(keep)}, dropped {dropped} truncated cells")
PY
echo ">>> [redo encode] gemma4 $(date +%H:%M:%S)"
python3 run_encode.py --model gemma4 --runs 1 --max-tokens 6000 --out "$RES/encode.jsonl"
echo ">>> [redo encode] qwen35-a3b $(date +%H:%M:%S)"
python3 run_encode.py --model qwen35-a3b --runs 1 --max-tokens 8000 --out "$RES/encode.jsonl"
echo "===== REDO ALL DONE $(date) ====="
