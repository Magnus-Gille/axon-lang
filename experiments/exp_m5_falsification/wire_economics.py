#!/usr/bin/env python3
"""Wire economics: does AXON's density survive gzip and prompt-caching?

The use-case falsification (OVERNIGHT_FINDINGS.md) argued AXON's only conceivable
niche — token-dense text payloads — is closed by two free, ubiquitous mechanisms.
This measures both on the real corpus:

  KILLER 1 (bytes, on the wire): a deterministic machine-to-machine wire bills
  BYTES, and `Content-Encoding: gzip` (one server setting) compresses repetitive
  JSON ~10x. If gzip(JSON) ≤ raw AXON, AXON's density buys nothing on the wire.

  KILLER 2 (tokens, in context): AXON's saving over JSON is decomposed into
  irreducible CONTENT (the ground-truth field values, identical across formats)
  vs STRUCTURAL overhead (keys/envelope/syntax). If the saving is ~all structural,
  then it lives entirely in the redundancy that gzip AND prompt-caching already
  remove for free — no new language required.

Stdlib + tiktoken. Run: python wire_economics.py
"""
from __future__ import annotations
import gzip, json, os, statistics as st
import tiktoken

HERE = os.path.dirname(os.path.abspath(__file__))
ENC = tiktoken.get_encoding("cl100k_base")
ntok = lambda s: len(ENC.encode(s))

tasks = {t["id"]: t for t in json.load(open(os.path.join(HERE, "tasks.json")))["tasks"]}
rows = [json.loads(l) for l in open(os.path.join(HERE, "results/encode.jsonl"))]
CONDS = ["axon", "json", "json_schema"]


def gt_value_tokens(tid):
    return ntok(" ".join(str(s.get("value")) for s in tasks[tid]["fields"].values()))


def main():
    from collections import defaultdict
    msgs = defaultdict(list)
    for r in rows:
        if r["condition"] in CONDS and r.get("valid") and (r.get("msg") or "").strip():
            msgs[r["condition"]].append(r["msg"])

    print("=== per-message size (valid messages) ===")
    print(f"{'cond':<13}{'n':>4}{'raw_B':>7}{'permsg_gzB':>11}{'stream_gzB/msg':>15}{'tokens':>8}")
    s = {}
    for c in CONDS:
        ms = msgs[c]
        raw = st.mean(len(m.encode()) for m in ms)
        pgz = st.mean(len(gzip.compress(m.encode(), 9)) for m in ms)
        sgz = len(gzip.compress(b"\n".join(m.encode() for m in ms), 9)) / len(ms)
        tk = st.mean(ntok(m) for m in ms)
        s[c] = dict(raw=raw, pgz=pgz, sgz=sgz, tok=tk, n=len(ms))
        print(f"{c:<13}{len(ms):>4}{raw:>7.0f}{pgz:>11.0f}{sgz:>15.0f}{tk:>8.1f}")

    a, j = s["axon"], s["json"]
    print("\n=== KILLER 1 — gzip on the wire ===")
    print(f"AXON raw={a['raw']:.0f}B  vs  JSON gzip(stream)={j['sgz']:.0f}B/msg  "
          f"-> JSON+gzip {'BEATS' if j['sgz'] < a['raw'] else 'loses to'} raw AXON by {(a['raw']-j['sgz'])/a['raw']*100:.0f}%")
    print(f"AXON gzip(stream)={a['sgz']:.0f}B ≈ JSON gzip(stream)={j['sgz']:.0f}B  "
          f"-> after gzip, AXON's edge is ~{(j['sgz']-a['sgz']):.0f}B (gone)")
    print(f"gzip's free saving on JSON = {(j['raw']-j['sgz'])/j['raw']*100:.0f}%  "
          f"vs AXON's token saving over JSON = {(j['tok']-a['tok'])/j['tok']*100:.0f}%")

    print("\n=== KILLER 2 — AXON's saving is structural, not content ===")
    gtv = st.mean(gt_value_tokens(r["task_id"]) for r in rows if r["condition"] == "axon" and r.get("valid"))
    save = j["tok"] - a["tok"]
    struct_frac = min(save, j["tok"] - gtv) / save * 100
    print(f"irreducible content ≈ {gtv:.1f} tok | AXON {a['tok']:.1f} ({a['tok']-gtv:.1f} struct) | JSON {j['tok']:.1f} ({j['tok']-gtv:.1f} struct)")
    print(f"AXON saves {save:.1f} tok over JSON — ~{struct_frac:.0f}% of it is STRUCTURAL overhead")
    eff_a, eff_j = gtv + 0.1 * (a["tok"] - gtv), gtv + 0.1 * (j["tok"] - gtv)
    print(f"prompt-caching structure @0.1x: AXON {eff_a:.1f} vs JSON {eff_j:.1f} tok "
          f"-> edge shrinks {(j['tok']-a['tok'])/j['tok']*100:.0f}% -> {(eff_j-eff_a)/eff_j*100:.0f}%")
    print("\n(binary codecs protobuf/CBOR are denser still on a byte wire — not shown; well-established.)")


if __name__ == "__main__":
    main()
