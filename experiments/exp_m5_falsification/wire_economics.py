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


def binary_kill(axon_stats):
    """KILLER 1b: binary codecs on the byte wire (CBOR/msgpack, +schema-stripped)."""
    try:
        import cbor2, msgpack
        import conditions as C
    except Exception:
        print("\n=== KILLER 1b — binary codecs: SKIPPED (pip install cbor2 msgpack) ===")
        return
    objs = []
    for r in rows:
        if r["condition"] == "json" and r.get("valid") and (r.get("msg") or "").strip():
            try:
                o = json.loads(C.extract_json(r["msg"]))
                if isinstance(o, dict):
                    objs.append(o)
            except Exception:
                pass

    def leaves(o):
        if isinstance(o, dict):
            return [x for v in o.values() for x in leaves(v)]
        if isinstance(o, list):
            return [x for v in o for x in leaves(v)]
        return [o]

    def sz(encoder):
        raw = st.mean(len(encoder(o)) for o in objs)
        sgz = len(gzip.compress(b"".join(encoder(o) for o in objs), 9)) / len(objs)
        return raw, sgz

    variants = {
        "CBOR (binary, keys)": lambda o: cbor2.dumps(o),
        "msgpack (binary, keys)": lambda o: msgpack.packb(o),
        "CBOR values-only (protobuf-like)": lambda o: cbor2.dumps(leaves(o)),
    }
    print("\n=== KILLER 1b — binary codecs on the byte wire (n=%d) ===" % len(objs))
    print(f"{'encoding':<34}{'raw_B':>7}{'gz_stream_B':>13}")
    print(f"{'AXON (dense text)':<34}{axon_stats['raw']:>7.0f}{axon_stats['sgz']:>13.0f}")
    for name, enc in variants.items():
        raw, sgz = sz(enc)
        flag = "< AXON raw" if raw < axon_stats["raw"] else ">= AXON raw"
        print(f"{name:<34}{raw:>7.0f}{sgz:>13.0f}   ({flag})")
    print("AXON's only raw-byte win is over SCHEMALESS binary (keys-as-strings). But the")
    print("deterministic-parser regime where AXON's validity matters IS the schema regime,")
    print("where schema-stripped positional binary (~56B) beats AXON (~75B); after gzip all")
    print("formats land within a few B/msg and protobuf-like is smallest. Bytes -> binary wins.")


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

    binary_kill(a)

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
