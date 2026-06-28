#!/usr/bin/env python3
"""Structured-outputs arm of the in-context pilot.

Emit each task with the box's `response_format: json_schema` built from the task's
own fields — forcing the model to the EXACT keys + types. Then a deterministic
consumer extracts by literal key (guaranteed present by the constraint) and scores
fidelity. Tests the pilot's positive claim: in the in-context deterministic regime,
the winner is SCHEMA-CONSTRAINED emission (a JSON technique), not a dense notation.

Usage: python run_structured.py --model qwen3-30b-instruct [--model ...]
"""
from __future__ import annotations
import argparse, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
M5 = os.path.join(HERE, "..", "exp_m5_falsification")
sys.path.insert(0, M5)
import scoring_lib as S
from m5_client import chat

try:
    import tiktoken
    _ENC = tiktoken.get_encoding("cl100k_base")
    ntok = lambda s: len(_ENC.encode(s or ""))
except Exception:
    ntok = lambda s: max(1, round(len(s or "") / 4))

_KIND2JSON = {
    "enum": {"type": "string"}, "ref": {"type": "string"}, "text": {"type": "string"},
    "num": {"type": "number"}, "bool": {"type": "boolean"},
    "list_ordered": {"type": "array", "items": {"type": "string"}},
    "list_set": {"type": "array", "items": {"type": "string"}},
}


def schema_for(task):
    props = {k: _KIND2JSON.get(spec["kind"], {"type": "string"}) for k, spec in task["fields"].items()}
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "agent_message", "strict": True,
            "schema": {"type": "object", "properties": props,
                       "required": list(task["fields"].keys()), "additionalProperties": False},
        },
    }


SYS = ("You are Agent A in an agent-to-agent system. Convey the intent as a single JSON object "
       "matching the provided schema exactly. Fill every field from the intent; use null only if "
       "truly absent. Numbers carry no units; agent refs keep their @ name.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", action="append", required=True)
    ap.add_argument("--out", default=os.path.join(HERE, "results", "structured.jsonl"))
    ap.add_argument("--max-tokens", type=int, default=600)
    args = ap.parse_args()
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    tasks = json.load(open(os.path.join(M5, "tasks.json")))["tasks"]
    done = set()
    if os.path.exists(args.out):
        for l in open(args.out):
            try:
                done.add(json.loads(l)["key"])
            except Exception:
                pass
    out = open(args.out, "a")
    for model in args.model:
        nok = nvalid = 0
        for t in tasks:
            key = f"{model}|structured|{t['id']}|0"
            if key in done:
                continue
            msgs = [{"role": "system", "content": SYS},
                    {"role": "user", "content": f"Intent:\n{t['nl_intent']}\n\nEmit the JSON object."}]
            r = chat(model, msgs, max_tokens=args.max_tokens, temperature=0.2, response_format=schema_for(t))
            rec_obj, valid = None, False
            if r["ok"]:
                try:
                    rec_obj = json.loads(r["content"])
                    valid = isinstance(rec_obj, dict)
                except Exception:
                    valid = False
            # strict deterministic extraction: literal key lookup (keys guaranteed by schema)
            extracted = {k: rec_obj.get(k) for k in t["fields"]} if valid else None
            fid, _ = S.score_task(extracted, t)
            rec = {"key": key, "model": model, "condition": "structured", "task_id": t["id"],
                   "level": t["level"], "ok": r["ok"], "valid": valid,
                   "msg": r["content"][:600] if r["ok"] else "",
                   "neutral_tokens": ntok(r["content"] if r["ok"] else ""), "det_fidelity": fid,
                   "latency_s": r["latency_s"], "error": r["error"]}
            out.write(json.dumps(rec) + "\n"); out.flush()
            nok += int(r["ok"]); nvalid += int(valid)
            print(f"[{model}] {t['id']} valid={valid} ntok={rec['neutral_tokens']} fid={fid:.2f}", flush=True)
        print(f"[{model}] DONE ok={nok} valid={nvalid}/{len(tasks)}", flush=True)


if __name__ == "__main__":
    main()
