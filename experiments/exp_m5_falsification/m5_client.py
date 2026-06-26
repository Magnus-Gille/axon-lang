#!/usr/bin/env python3
"""OpenAI-compatible client for the M5 home inference box (inference.gille.ai).

The bearer auth header is read from a file (env ``M5_AUTH_FILE``) so no secret
ever lives in the repo. We capture: content, the reasoning channel (thinking
models surface it separately), token usage, finish_reason, and wall-clock
latency.

Operational facts learned by probing the box (2026-06-25):
  * The box serves ONE model at a time. Switching models is a cold-swap that
    costs minutes and can surface as a 503 or a hung connection on the first
    hit. Therefore the runner must drain ALL work for a model before swapping.
  * Thinking models (qwen35-a3b, gpt-oss-120b, tongyi-dr) spend completion
    tokens on a hidden reasoning channel and return EMPTY content if the
    max_tokens budget is too small. Always give a generous budget.
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request

BASE = os.environ.get("M5_BASE", "https://inference.gille.ai/v1")

# Default points at the session scratchpad file holding "Bearer <token>".
# Override with M5_AUTH_FILE. The file lives outside the repo and is never
# committed.
DEFAULT_AUTH_FILE = os.environ.get(
    "M5_AUTH_FILE",
    "/private/tmp/claude-501/-Users-magnus-repos-invent-new-language/"
    "53c42d89-2684-449c-9a8c-43bc4c4c2a2e/scratchpad/.m5auth",
)

_RETRYABLE = {408, 409, 425, 429, 500, 502, 503, 504}


def _auth() -> str:
    with open(DEFAULT_AUTH_FILE) as f:
        return f.read().strip()


def chat(
    model: str,
    messages: list[dict],
    max_tokens: int = 2048,
    temperature: float = 0.2,
    timeout: int = 200,
    retries: int = 4,
    backoff: float = 6.0,
) -> dict:
    """Single chat completion. Returns a result dict (never raises).

    Result keys: ok, content, reasoning, usage, latency_s, finish_reason,
    error, attempts.
    """
    url = f"{BASE}/chat/completions"
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    data = json.dumps(payload).encode()
    last_err = None
    for attempt in range(retries):
        # Cloudflare fronts the box and 403s (code 1010) on the default
        # Python-urllib User-Agent, so present a normal browser UA.
        headers = {
            "Authorization": _auth(),
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        }
        t0 = time.time()
        try:
            req = urllib.request.Request(url, data=data, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                body = json.loads(resp.read().decode())
            dt = time.time() - t0
            choice = body["choices"][0]
            msg = choice.get("message", {})
            return {
                "ok": True,
                "content": msg.get("content") or "",
                "reasoning": msg.get("reasoning_content") or msg.get("reasoning") or "",
                "usage": body.get("usage", {}) or {},
                "latency_s": round(dt, 3),
                "finish_reason": choice.get("finish_reason"),
                "error": None,
                "attempts": attempt + 1,
            }
        except urllib.error.HTTPError as e:
            try:
                detail = e.read()[:200]
            except Exception:
                detail = b""
            last_err = f"HTTP {e.code}: {detail!r}"
            if e.code not in _RETRYABLE:
                break  # 4xx (bad request etc.) — retrying won't help
        except Exception as e:  # timeout (cold swap), conn reset, JSON error
            last_err = f"{type(e).__name__}: {e}"
        time.sleep(backoff * (attempt + 1))
    return {
        "ok": False,
        "content": "",
        "reasoning": "",
        "usage": {},
        "latency_s": None,
        "finish_reason": None,
        "error": last_err,
        "attempts": retries,
    }


if __name__ == "__main__":
    import sys

    m = sys.argv[1] if len(sys.argv) > 1 else "mellum"
    r = chat(m, [{"role": "user", "content": "Reply with the word PONG only."}], max_tokens=20)
    print(json.dumps({k: r[k] for k in ("ok", "content", "latency_s", "usage", "error")}, indent=2))
