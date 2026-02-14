"""
Automated semantic element extractors for structured formats.

Extracts elements from AXON, JSON FC, and FIPA-ACL outputs without LLM involvement.
Used as primary scoring for structured formats per the scoring contract.

Each extractor takes a raw output string and a list of element definitions,
and returns a dict of {element_id: {"verdict": "PRESENT"|"ABSENT", "evidence": str}}.
"""

from __future__ import annotations

import json
import os
import re
import sys
from typing import Optional

# Add src/ to path for AXON parser
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src"))

# ── Fence stripping (shared with condition_adapter) ────────────────────

_FENCE_RE = re.compile(r"^```[\w]*\n(.*?)```\s*$", re.DOTALL)


def _strip_fences(output: str) -> str:
    m = _FENCE_RE.match(output.strip())
    return m.group(1).strip() if m else output.strip()


# ── Element check helpers ──────────────────────────────────────────────

def _present(evidence: str) -> dict:
    return {"verdict": "PRESENT", "evidence": evidence}


def _absent(reason: str) -> dict:
    return {"verdict": "ABSENT", "evidence": reason}


# ── AXON Extractor ─────────────────────────────────────────────────────

# Map AXON performatives to semantic intent categories
AXON_PERF_TO_INTENT = {
    "QRY": {"query_intent", "query"},
    "INF": {"inform_intent", "inform"},
    "RPL": {"reply_intent", "reply", "inform_intent"},
    "REQ": {"request_intent", "request", "command"},
    "CMD": {"request_intent", "command"},
    "PRO": {"propose_intent", "propose"},
    "CTR": {"counter_intent", "counter"},
    "ACC": {"accept"},
    "REJ": {"reject"},
    "PUB": {"alert_intent", "alert", "publish"},
    "CFM": {"confirm"},
    "DNY": {"deny"},
    "ERR": {"error_intent", "error"},
    "SUB": {"subscribe"},
    "CAN": {"cancel"},
}


def extract_axon(output: str, elements: list[dict], task_id: str) -> dict[str, dict]:
    """Extract semantic elements from an AXON output."""
    cleaned = _strip_fences(output)
    results = {}

    # Try to parse using the public parse() function
    try:
        from axon_parser import parse as axon_parse
        messages = axon_parse(cleaned)
    except Exception as e:
        # Parse failed — fall back to text-based extraction
        for elem in elements:
            found = _check_content_fact(elem["name"].lower(), elem.get("check", ""),
                                        cleaned.lower(), cleaned)
            results[elem["id"]] = _present(found) if found else _absent(f"Parse failed: {e}")
        return results

    if not messages:
        for elem in elements:
            results[elem["id"]] = _absent("No messages parsed")
        return results

    # Collect all info across messages
    # Message structure: msg.performative, msg.routing.sender, msg.routing.receiver,
    #                    msg.content, msg.meta (MetaBlock with .fields dict)
    all_senders = set()
    all_receivers = set()
    all_performatives = set()
    all_meta = {}
    msg_count = len(messages)
    msg_ids = []
    reply_tos = []
    has_sequence = "->" in cleaned
    has_causation = "<-" in cleaned
    has_parallel = "&" in cleaned

    for msg in messages:
        if hasattr(msg, "performative") and msg.performative:
            all_performatives.add(msg.performative)
        if hasattr(msg, "routing") and msg.routing:
            if msg.routing.sender:
                s = msg.routing.sender
                all_senders.add(s if isinstance(s, str) else str(s))
            if msg.routing.receiver:
                r = msg.routing.receiver
                if isinstance(r, list):
                    for recv in r:
                        all_receivers.add(str(recv))
                else:
                    all_receivers.add(r if isinstance(r, str) else str(r))
        if hasattr(msg, "meta") and msg.meta and hasattr(msg.meta, "fields"):
            for k, v in msg.meta.fields.items():
                val = v.value if hasattr(v, "value") else str(v)
                all_meta.setdefault(k, []).append(val)
                if k == "id":
                    msg_ids.append(str(val))
                if k == "re":
                    reply_tos.append(str(val))

    # Flatten the output text for value searches
    text_lower = cleaned.lower()

    for elem in elements:
        eid = elem["id"]
        name = elem["name"].lower()
        check = elem.get("check", "").lower()
        category = elem.get("category", "")

        # Identity elements
        if name in ("sender", "sender_planner", "sender_monitor",
                     "supplier_sender", "buyer_counter_sender") or "sender" in name:
            if name.startswith("msg"):
                # Per-message sender (L3-03)
                msg_num = int(re.search(r"msg(\d+)", name).group(1)) - 1
                if msg_num < msg_count and hasattr(messages[msg_num], "routing") and messages[msg_num].routing and messages[msg_num].routing.sender:
                    results[eid] = _present(f"Sender: {messages[msg_num].routing.sender}")
                else:
                    results[eid] = _absent("No sender in this message")
            elif all_senders:
                results[eid] = _present(f"Sender(s): {', '.join(all_senders)}")
            else:
                results[eid] = _absent("No sender found")
            continue

        if name in ("receiver", "buyer_receiver") or "receiver" in name:
            if "multiple" in name or "worker" in name:
                # Multi-receiver or specific worker
                if len(all_receivers) >= 1:
                    results[eid] = _present(f"Receiver(s): {', '.join(all_receivers)}")
                else:
                    results[eid] = _absent("No receivers found")
            elif name.startswith("msg"):
                msg_num = int(re.search(r"msg(\d+)", name).group(1)) - 1
                if msg_num < msg_count and hasattr(messages[msg_num], "routing") and messages[msg_num].routing and messages[msg_num].routing.receiver:
                    results[eid] = _present(f"Receiver: {messages[msg_num].routing.receiver}")
                else:
                    results[eid] = _absent("No receiver in this message")
            elif all_receivers:
                results[eid] = _present(f"Receiver(s): {', '.join(all_receivers)}")
            else:
                results[eid] = _absent("No receiver found")
            continue

        # Intent elements
        if "_intent" in name or category == "intent":
            matched_perf = None
            for perf in all_performatives:
                intents = AXON_PERF_TO_INTENT.get(perf, set())
                # Check if this element's name matches any intent
                for intent_name in intents:
                    if intent_name in name or name in intent_name:
                        matched_perf = perf
                        break
                if matched_perf:
                    break

            # Also check for generic intent match
            if not matched_perf and all_performatives:
                # For msg-level intents (L3-03), check specific message
                if name.startswith("msg"):
                    msg_num = int(re.search(r"msg(\d+)", name).group(1)) - 1
                    if msg_num < msg_count and hasattr(messages[msg_num], "performative"):
                        matched_perf = messages[msg_num].performative
                elif any(p in AXON_PERF_TO_INTENT for p in all_performatives):
                    # Any performative present counts for generic intent check
                    matched_perf = list(all_performatives)[0]

            if matched_perf:
                results[eid] = _present(f"Performative: {matched_perf}")
            else:
                results[eid] = _absent("No matching performative found")
            continue

        # Metadata elements
        if category == "metadata" or name in ("metadata_id", "metadata_version"):
            if name.startswith("msg"):
                # Per-message metadata (L3-03)
                msg_num = int(re.search(r"msg(\d+)", name).group(1)) - 1
                if "id" in name:
                    if msg_num < len(msg_ids):
                        results[eid] = _present(f"Message ID: {msg_ids[msg_num]}")
                    else:
                        results[eid] = _absent("No message ID for this message")
                elif "version" in name:
                    versions = all_meta.get("%%", [])
                    if msg_num < len(versions):
                        results[eid] = _present(f"Version: {versions[msg_num]}")
                    elif versions:
                        results[eid] = _present(f"Version found: {versions[0]}")
                    else:
                        results[eid] = _absent("No protocol version found")
                elif "timestamp" in name:
                    timestamps = all_meta.get("ts", [])
                    if msg_num < len(timestamps):
                        results[eid] = _present(f"Timestamp: {timestamps[msg_num]}")
                    elif timestamps:
                        results[eid] = _present(f"Timestamp found: {timestamps[0]}")
                    else:
                        results[eid] = _absent("No timestamp found")
                else:
                    results[eid] = _absent(f"Unknown metadata element: {name}")
            elif "id" in name and "metadata" in name:
                if "id" in all_meta:
                    results[eid] = _present(f"ID: {all_meta['id'][0]}")
                else:
                    results[eid] = _absent("No message ID in metadata")
            elif "version" in name:
                if "%%" in all_meta:
                    results[eid] = _present(f"Version: {all_meta['%%'][0]}")
                else:
                    results[eid] = _absent("No protocol version in metadata")
            elif name == "metadata_complete":
                has_id = "id" in all_meta
                has_ver = "%%" in all_meta
                has_ts = "ts" in all_meta
                if has_id and has_ver and has_ts:
                    results[eid] = _present("ID, version, and timestamps present")
                else:
                    missing = []
                    if not has_id: missing.append("id")
                    if not has_ver: missing.append("version")
                    if not has_ts: missing.append("timestamp")
                    results[eid] = _absent(f"Missing: {', '.join(missing)}")
            else:
                results[eid] = _absent(f"Unknown metadata: {name}")
            continue

        # Threading elements
        if category == "threading" or "reply" in name and "link" in name:
            if name.startswith("msg"):
                msg_num = int(re.search(r"msg(\d+)", name).group(1)) - 1
                # Check if this message has a re: field
                if msg_num < len(reply_tos):
                    results[eid] = _present(f"Reply-to: {reply_tos[msg_num]}")
                elif reply_tos:
                    results[eid] = _present(f"Reply-to refs found: {reply_tos}")
                else:
                    results[eid] = _absent("No reply-to references")
            elif name == "reply_threading":
                if reply_tos:
                    results[eid] = _present(f"Reply-to links: {reply_tos}")
                else:
                    results[eid] = _absent("No reply threading")
            else:
                results[eid] = _absent("No threading found")
            continue

        # Compound elements (L3-03 multiple_messages, reply_threading, metadata_complete, etc.)
        if name == "multiple_messages":
            if msg_count >= 3:
                results[eid] = _present(f"{msg_count} messages")
            else:
                results[eid] = _absent(f"Only {msg_count} messages (need 3)")
            continue

        if name == "reply_threading":
            if reply_tos:
                results[eid] = _present(f"Reply-to links: {reply_tos}")
            else:
                results[eid] = _absent("No reply threading")
            continue

        if name == "metadata_complete":
            has_id = "id" in all_meta
            has_ver = "%%" in all_meta
            has_ts = "ts" in all_meta
            if has_id and has_ver and has_ts:
                results[eid] = _present("ID, version, and timestamps present")
            else:
                missing = []
                if not has_id: missing.append("id")
                if not has_ver: missing.append("version")
                if not has_ts: missing.append("timestamp")
                results[eid] = _absent(f"Missing: {', '.join(missing)}")
            continue

        # Structural elements (sequences, causal chains)
        if category in ("structural", "causal"):
            if "sequence" in name or "action" in name:
                if has_sequence:
                    results[eid] = _present("Sequence operator -> found")
                elif _check_content_fact(name, check, text_lower, cleaned):
                    results[eid] = _present(f"Action found: {name}")
                else:
                    results[eid] = _absent("No sequence/action found")
            elif "caus" in name:
                if has_causation:
                    results[eid] = _present("Causation operator <- found")
                else:
                    results[eid] = _absent("No causal operator found")
            else:
                results[eid] = _absent(f"Unknown structural element: {name}")
            continue

        # Content-fact elements — search for specific values in text
        found = _check_content_fact(name, check, text_lower, cleaned)
        if found:
            results[eid] = _present(found)
        else:
            results[eid] = _absent(f"Value not found for: {name}")
        continue

    return results


def _check_content_fact(name: str, check: str, text_lower: str, text_raw: str) -> Optional[str]:
    """Check for specific content facts by searching for key values."""
    # Specific value checks based on element name patterns
    checks = {
        "target_server": [r"server", r"web.?server", r"srv"],
        "status": [r"health", r"#healthy", r"ok", r"up"],
        "uptime_value": [r"99\.7", r"99\.7%"],
        "error_code": [r"404"],
        "error_description": [r"not.?found"],
        "repo": [r"repo", r"repository", r"github"],
        "branch": [r"branch", r"main", r"master", r"feature"],
        "commit": [r"commit", r"[0-9a-f]{7,40}"],
        "item": [r"widget"],
        "item_widgets": [r"widget"],
        "quantity": [r"10.?000", r"10000"],
        "quantity_10000": [r"10.?000", r"10000"],
        "price": [r"2\.50", r"2\.5[^0-9]", r"2\.5usd", r"price", r"unit_price"],
        "price_2_50": [r"2\.50", r"2\.5[^0-9]", r"2\.5usd"],
        "counter_price_2_20": [r"2\.20", r"2\.2[^0-9]"],
        "market_average_2_15": [r"2\.15"],
        "justification": [r"market", r"average", r"reason", r"because"],
        "justification_present": [r"market", r"average", r"reason"],
        "task_type": [r"data.?process", r"process", r"#task", r"task", r"dp-"],
        "data_ranges": [r"0.*1000.*2000.*3000", r"range", r"segment"],
        "range_segment_1": [r"0.*1000"],
        "range_segment_2": [r"1000.*2000", r"1001"],
        "range_segment_3": [r"2000.*3000", r"2001"],
        "receivers_multiple": [r"worker.*worker", r"@\w+.*@\w+.*@\w+"],
        "sequence_of_actions": [r"->", r"fetch.*parse.*store"],
        "action_fetch": [r"fetch", r"get", r"retrieve"],
        "action_parse": [r"parse", r"json"],
        "action_store": [r"store", r"save", r"db", r"database"],
        "severity": [r"sev.*2", r"severity.*2", r"#sev2", r":2"],
        "severity_2": [r"sev.*2", r"severity.*2", r"#sev2"],
        "priority": [r"pri.*4", r"priority.*4", r"\^.*4", r"\^:4"],
        "priority_4": [r"pri.*4", r"priority.*4", r"\^.*4", r"\^:4"],
        "causal_chain": [r"<-", r"caused.?by", r"because"],
        "cause_pool_exhaustion": [r"pool", r"connection.*pool", r"exhaustion"],
        "cause_traffic_spike": [r"traffic.*spike", r"spike"],
        "service_payments": [r"payment"],
        "latency_threshold": [r"2\s*s", r"2000\s*ms", r"latency.*>.*2", r">.*2s"],
        "recommendation": [r"recommend", r"scale", r"restart", r"resolve", r"mitigat"],
        "diagnostics_data": [r"bottleneck", r"diagnostic", r"connection"],
        "scaling_request": [r"scal"],
        "msg2_bottleneck": [r"bottleneck"],
        "msg2_connection_stats": [r"connection", r"conn"],
        "msg3_scaling_request": [r"scal"],
    }

    # Try name-based lookup first
    patterns = checks.get(name, [])
    if not patterns:
        # Try partial match
        for key, pats in checks.items():
            if key in name or name in key:
                patterns = pats
                break

    for pattern in patterns:
        if re.search(pattern, text_lower):
            match = re.search(pattern, text_raw, re.IGNORECASE)
            return f"Found: {match.group(0)}" if match else f"Pattern matched: {pattern}"

    return None


# ── JSON FC Extractor ──────────────────────────────────────────────────

JSON_PERF_TO_INTENT = {
    "query": {"query_intent", "query"},
    "inform": {"inform_intent", "inform"},
    "reply": {"reply_intent", "inform_intent"},
    "request": {"request_intent", "request"},
    "command": {"request_intent", "command"},
    "propose": {"propose_intent", "propose"},
    "counter": {"counter_intent", "counter"},
    "counter-propose": {"counter_intent", "counter"},
    "counterpropose": {"counter_intent", "counter"},
    "alert": {"alert_intent", "alert"},
    "publish": {"alert_intent", "publish"},
    "error": {"error_intent", "error"},
    "report": {"inform_intent", "error_intent"},
}


def extract_json_fc(output: str, elements: list[dict], task_id: str) -> dict[str, dict]:
    """Extract semantic elements from a JSON FC output."""
    cleaned = _strip_fences(output)
    results = {}

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        for elem in elements:
            results[elem["id"]] = _absent(f"JSON parse failed: {e}")
        return results

    # Normalize: handle both single object and array of objects
    if isinstance(data, list):
        messages = data
    elif isinstance(data, dict):
        messages = [data]
    else:
        for elem in elements:
            results[elem["id"]] = _absent("Unexpected JSON type")
        return results

    # Collect info across all messages
    all_senders = set()
    all_receivers = set()
    all_performatives = set()
    all_content = {}
    msg_count = len(messages)
    msg_ids = []
    reply_tos = []

    for msg in messages:
        if not isinstance(msg, dict):
            continue
        sender = msg.get("from") or msg.get("sender") or msg.get("from_agent")
        receiver = msg.get("to") or msg.get("receiver") or msg.get("to_agent")
        perf = msg.get("performative") or msg.get("type") or msg.get("action")
        content = msg.get("content", {})
        mid = msg.get("id") or msg.get("message_id")
        reply_to = msg.get("reply_to") or msg.get("in_reply_to")

        if sender:
            all_senders.add(str(sender))
        if receiver:
            all_receivers.add(str(receiver))
        if perf:
            all_performatives.add(str(perf).lower())
        if isinstance(content, dict):
            all_content.update(content)
        if mid:
            msg_ids.append(str(mid))
        if reply_to:
            reply_tos.append(str(reply_to))

    text_lower = cleaned.lower()

    for elem in elements:
        eid = elem["id"]
        name = elem["name"].lower()
        check = elem.get("check", "").lower()
        category = elem.get("category", "")

        # Identity elements
        if "sender" in name:
            if name.startswith("msg"):
                msg_num = int(re.search(r"msg(\d+)", name).group(1)) - 1
                if msg_num < msg_count:
                    msg = messages[msg_num]
                    s = msg.get("from") or msg.get("sender")
                    if s:
                        results[eid] = _present(f"Sender: {s}")
                    else:
                        results[eid] = _absent("No sender in message")
                else:
                    results[eid] = _absent("Message not found")
            elif all_senders:
                results[eid] = _present(f"Sender(s): {', '.join(all_senders)}")
            else:
                results[eid] = _absent("No sender field")
            continue

        if "receiver" in name or name == "buyer_receiver":
            if "multiple" in name or "worker" in name:
                if isinstance(messages[0].get("to"), list):
                    results[eid] = _present(f"Multiple receivers: {messages[0]['to']}")
                elif len(all_receivers) >= 1:
                    results[eid] = _present(f"Receiver(s): {', '.join(all_receivers)}")
                else:
                    results[eid] = _absent("No receivers")
            elif name.startswith("msg"):
                msg_num = int(re.search(r"msg(\d+)", name).group(1)) - 1
                if msg_num < msg_count:
                    msg = messages[msg_num]
                    r = msg.get("to") or msg.get("receiver")
                    if r:
                        results[eid] = _present(f"Receiver: {r}")
                    else:
                        results[eid] = _absent("No receiver in message")
                else:
                    results[eid] = _absent("Message not found")
            elif all_receivers:
                results[eid] = _present(f"Receiver(s): {', '.join(all_receivers)}")
            else:
                results[eid] = _absent("No receiver field")
            continue

        # Intent elements
        if "_intent" in name or category == "intent":
            matched = False
            for perf in all_performatives:
                intents = JSON_PERF_TO_INTENT.get(perf, set())
                for intent_name in intents:
                    if intent_name in name or name.replace("_intent", "") in intent_name:
                        results[eid] = _present(f"Performative: {perf}")
                        matched = True
                        break
                if matched:
                    break
            if not matched:
                if name.startswith("msg"):
                    msg_num = int(re.search(r"msg(\d+)", name).group(1)) - 1
                    if msg_num < msg_count:
                        msg = messages[msg_num]
                        perf = msg.get("performative") or msg.get("type")
                        if perf:
                            results[eid] = _present(f"Performative: {perf}")
                            matched = True
                if not matched:
                    if all_performatives:
                        results[eid] = _present(f"Performative(s): {all_performatives}")
                    else:
                        results[eid] = _absent("No performative field")
            continue

        # Metadata elements
        if category == "metadata" or "metadata" in name:
            if name.startswith("msg"):
                msg_num = int(re.search(r"msg(\d+)", name).group(1)) - 1
                if msg_num < msg_count:
                    msg = messages[msg_num]
                    if "id" in name:
                        mid = msg.get("id") or msg.get("message_id")
                        results[eid] = _present(f"ID: {mid}") if mid else _absent("No ID")
                    elif "version" in name:
                        ver = msg.get("protocol_version") or msg.get("version")
                        results[eid] = _present(f"Version: {ver}") if ver else _absent("No version")
                    elif "timestamp" in name:
                        ts = msg.get("timestamp") or msg.get("ts")
                        results[eid] = _present(f"Timestamp: {ts}") if ts else _absent("No timestamp")
                    else:
                        results[eid] = _absent(f"Unknown metadata: {name}")
                else:
                    results[eid] = _absent("Message not found")
            elif name == "metadata_complete":
                has_ids = bool(msg_ids)
                has_ver = any(
                    m.get("protocol_version") or m.get("version") or
                    (isinstance(m.get("content"), dict) and (m["content"].get("protocol_version") or m["content"].get("version")))
                    for m in messages
                )
                has_ts = any(m.get("timestamp") or m.get("ts") for m in messages)
                if has_ids and has_ver and has_ts:
                    results[eid] = _present("ID, version, timestamps present")
                else:
                    missing = []
                    if not has_ids: missing.append("id")
                    if not has_ver: missing.append("version")
                    if not has_ts: missing.append("timestamp")
                    results[eid] = _absent(f"Missing: {', '.join(missing)}")
            elif "id" in name:
                results[eid] = _present(f"ID: {msg_ids[0]}") if msg_ids else _absent("No ID")
            elif "version" in name:
                # Check top-level and content for version
                ver = None
                for m in messages:
                    ver = m.get("protocol_version") or m.get("version")
                    if not ver and isinstance(m.get("content"), dict):
                        ver = m["content"].get("protocol_version") or m["content"].get("version")
                    if ver:
                        break
                results[eid] = _present(f"Version: {ver}") if ver else _absent("No version")
            else:
                results[eid] = _absent(f"Unknown metadata: {name}")
            continue

        # Threading elements
        if "reply" in name and ("link" in name or "threading" in name):
            if reply_tos:
                results[eid] = _present(f"Reply-to: {reply_tos}")
            else:
                results[eid] = _absent("No reply-to references")
            continue

        # Compound elements — check before content-fact fallback
        if name == "multiple_messages":
            results[eid] = _present(f"{msg_count} messages") if msg_count >= 3 else _absent(f"Only {msg_count}")
            continue
        if name == "reply_threading":
            results[eid] = _present(f"Reply-to: {reply_tos}") if reply_tos else _absent("No reply threading")
            continue
        if name == "metadata_complete":
            has_ids = bool(msg_ids)
            has_ver = any(
                m.get("protocol_version") or m.get("version") or
                (isinstance(m.get("content"), dict) and (m["content"].get("protocol_version") or m["content"].get("version")))
                for m in messages
            )
            has_ts = any(m.get("timestamp") or m.get("ts") for m in messages)
            if has_ids and has_ver and has_ts:
                results[eid] = _present("ID, version, timestamps present")
            else:
                missing = []
                if not has_ids: missing.append("id")
                if not has_ver: missing.append("version")
                if not has_ts: missing.append("timestamp")
                results[eid] = _absent(f"Missing: {', '.join(missing)}")
            continue
        if name == "sequence_of_actions":
            if "steps" in all_content or "actions" in all_content or "pipeline" in all_content:
                results[eid] = _present("Sequence structure found in content")
            elif re.search(r"fetch.*parse.*store", text_lower):
                results[eid] = _present("Sequence found in text")
            else:
                results[eid] = _absent("No sequence found")
            continue

        # Content-fact elements — search in content dict and raw text
        found = _check_json_content(name, all_content, text_lower, cleaned)
        if found:
            results[eid] = _present(found)
        else:
            # Fall back to text search
            text_found = _check_content_fact(name, check, text_lower, cleaned)
            if text_found:
                results[eid] = _present(text_found)
            else:
                results[eid] = _absent(f"Not found: {name}")

    return results


def _check_json_content(name: str, content: dict, text_lower: str, text_raw: str) -> Optional[str]:
    """Check for values in JSON content dict."""
    # Flatten nested content for searching
    flat = _flatten_dict(content)

    # Direct key matches
    key_maps = {
        "item": ["item", "product"],
        "item_widgets": ["item", "product"],
        "quantity": ["quantity", "qty", "amount"],
        "quantity_10000": ["quantity", "qty"],
        "price": ["price", "unit_price", "price_per_unit"],
        "price_2_50": ["price", "unit_price", "original_offer_unit_price"],
        "counter_price_2_20": ["unit_price", "counter_price", "price"],
        "market_average_2_15": ["market_average", "market_average_unit_price"],
        "justification": ["justification", "reason", "rationale"],
        "justification_present": ["justification", "reason", "rationale"],
        "repo": ["repo", "repository"],
        "branch": ["branch"],
        "commit": ["commit", "commit_hash", "sha"],
        "status": ["status"],
        "uptime_value": ["uptime"],
        "error_code": ["code", "error_code", "status_code"],
        "error_description": ["description", "message", "error_message"],
        "task_type": ["task", "task_type", "type"],
        "severity": ["severity"],
        "severity_2": ["severity"],
        "priority": ["priority"],
        "priority_4": ["priority"],
        "recommendation": ["recommendation", "resolution", "action"],
        "service_payments": ["service", "service_name"],
        "latency_threshold": ["latency", "threshold", "latency_threshold"],
    }

    keys_to_check = key_maps.get(name, [name])
    for key in keys_to_check:
        if key in flat:
            return f"Key '{key}': {flat[key]}"

    return None


def _flatten_dict(d: dict, prefix: str = "") -> dict:
    """Flatten nested dict into dot-separated keys."""
    result = {}
    for k, v in d.items():
        full_key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            result.update(_flatten_dict(v, full_key))
        else:
            result[k] = v  # Keep both short and full key
            result[full_key] = v
    return result


# ── FIPA-ACL Extractor ─────────────────────────────────────────────────

FIPA_PERF_TO_INTENT = {
    "query-if": {"query_intent", "query"},
    "query-ref": {"query_intent", "query"},
    "inform": {"inform_intent", "inform", "reply_intent"},
    "request": {"request_intent", "request"},
    "propose": {"propose_intent", "propose"},
    "accept-proposal": {"accept"},
    "reject-proposal": {"reject"},
    "cfp": {"propose_intent"},
    "agree": {"accept"},
    "refuse": {"reject"},
    "failure": {"error_intent"},
    "not-understood": {"error_intent"},
    "subscribe": {"subscribe"},
    "cancel": {"cancel"},
}


def parse_fipa_sexp(text: str) -> list[dict]:
    """Minimal S-expression parser for FIPA-ACL messages.

    Parses forms like:
        (inform :sender a :receiver b :content "..." :reply-with m1)

    Returns list of message dicts with keys:
        performative, sender, receiver, content, reply_with, in_reply_to,
        language, ontology, and any other :keyword attributes.
    """
    messages = []
    # Find all top-level ( ... ) forms
    depth = 0
    start = None
    for i, ch in enumerate(text):
        if ch == '(':
            if depth == 0:
                start = i
            depth += 1
        elif ch == ')':
            depth -= 1
            if depth == 0 and start is not None:
                form = text[start:i + 1]
                parsed = _parse_single_fipa(form)
                if parsed:
                    messages.append(parsed)
                start = None
    return messages


def _parse_single_fipa(form: str) -> Optional[dict]:
    """Parse a single FIPA-ACL S-expression."""
    # Strip outer parens
    inner = form.strip()
    if inner.startswith('('):
        inner = inner[1:]
    if inner.endswith(')'):
        inner = inner[:-1]
    inner = inner.strip()

    if not inner:
        return None

    # Extract performative (first token)
    tokens = inner.split(None, 1)
    if not tokens:
        return None

    perf = tokens[0].lower()
    rest = tokens[1] if len(tokens) > 1 else ""

    result = {"performative": perf}

    # Extract :keyword value pairs
    # Handle quoted strings and nested parens
    pattern = r':(\S+)\s+'
    parts = re.split(pattern, rest)
    # parts[0] is anything before first :keyword (usually empty)
    # then alternating: keyword, value, keyword, value, ...
    i = 1
    while i < len(parts) - 1:
        keyword = parts[i].lower().replace("-", "_")
        value = parts[i + 1].strip()

        # Clean up value: remove trailing :keyword indicators
        # Find where the next :keyword starts
        value = value.strip()
        if value.startswith('"') and '"' in value[1:]:
            # Quoted string — extract just the quoted part
            end_quote = value.index('"', 1)
            value = value[1:end_quote]
        elif value.startswith('('):
            # Nested S-expression — find matching close paren
            depth = 0
            for j, ch in enumerate(value):
                if ch == '(':
                    depth += 1
                elif ch == ')':
                    depth -= 1
                    if depth == 0:
                        value = value[:j + 1]
                        break

        result[keyword] = value
        i += 2

    return result


def extract_fipa_acl(output: str, elements: list[dict], task_id: str) -> dict[str, dict]:
    """Extract semantic elements from a FIPA-ACL output."""
    cleaned = _strip_fences(output)
    results = {}

    messages = parse_fipa_sexp(cleaned)

    if not messages:
        # Try to extract basic info from text even without proper parsing
        for elem in elements:
            found = _check_content_fact(elem["name"].lower(), elem.get("check", ""),
                                        cleaned.lower(), cleaned)
            results[elem["id"]] = _present(found) if found else _absent("No FIPA messages parsed")
        return results

    # Collect info across messages
    all_senders = set()
    all_receivers = set()
    all_performatives = set()
    msg_count = len(messages)
    msg_ids = []
    reply_tos = []

    for msg in messages:
        perf = msg.get("performative", "")
        sender = msg.get("sender", "")
        receiver = msg.get("receiver", "")
        reply_with = msg.get("reply_with", "")
        in_reply_to = msg.get("in_reply_to", "")

        if perf:
            all_performatives.add(perf)
        if sender:
            all_senders.add(sender)
        if receiver:
            all_receivers.add(receiver)
        if reply_with:
            msg_ids.append(reply_with)
        if in_reply_to:
            reply_tos.append(in_reply_to)

    text_lower = cleaned.lower()

    for elem in elements:
        eid = elem["id"]
        name = elem["name"].lower()
        check = elem.get("check", "").lower()
        category = elem.get("category", "")

        # Identity
        if "sender" in name:
            if name.startswith("msg"):
                msg_num = int(re.search(r"msg(\d+)", name).group(1)) - 1
                if msg_num < msg_count:
                    s = messages[msg_num].get("sender", "")
                    results[eid] = _present(f"Sender: {s}") if s else _absent("No sender")
                else:
                    results[eid] = _absent("Message not found")
            elif all_senders:
                results[eid] = _present(f"Sender(s): {', '.join(all_senders)}")
            else:
                results[eid] = _absent("No :sender attribute")
            continue

        if "receiver" in name or name == "buyer_receiver":
            if "multiple" in name or "worker" in name:
                results[eid] = _present(f"Receiver(s): {', '.join(all_receivers)}") if all_receivers else _absent("No receivers")
            elif name.startswith("msg"):
                msg_num = int(re.search(r"msg(\d+)", name).group(1)) - 1
                if msg_num < msg_count:
                    r = messages[msg_num].get("receiver", "")
                    results[eid] = _present(f"Receiver: {r}") if r else _absent("No receiver")
                else:
                    results[eid] = _absent("Message not found")
            elif all_receivers:
                results[eid] = _present(f"Receiver(s): {', '.join(all_receivers)}")
            else:
                results[eid] = _absent("No :receiver attribute")
            continue

        # Intent
        if "_intent" in name or category == "intent":
            matched = False
            for perf in all_performatives:
                intents = FIPA_PERF_TO_INTENT.get(perf, set())
                for intent_name in intents:
                    if intent_name in name or name.replace("_intent", "") in intent_name:
                        results[eid] = _present(f"Performative: {perf}")
                        matched = True
                        break
                if matched:
                    break
            if not matched:
                if name.startswith("msg"):
                    msg_num = int(re.search(r"msg(\d+)", name).group(1)) - 1
                    if msg_num < msg_count:
                        perf = messages[msg_num].get("performative", "")
                        if perf:
                            results[eid] = _present(f"Performative: {perf}")
                            matched = True
                if not matched:
                    results[eid] = _present(f"Performatives: {all_performatives}") if all_performatives else _absent("No performative")
            continue

        # Metadata
        if category == "metadata" or "metadata" in name:
            if "id" in name:
                results[eid] = _present(f"ID: {msg_ids[0]}") if msg_ids else _absent("No :reply-with")
            elif "version" in name:
                # FIPA doesn't have native version — check :language or :protocol
                ver = any(m.get("language") or m.get("protocol") for m in messages)
                results[eid] = _present("Language/protocol present") if ver else _absent("No version equivalent")
            elif "timestamp" in name:
                # FIPA doesn't have native timestamp — check text
                results[eid] = _present("Timestamp in text") if re.search(r"\d{10}", cleaned) else _absent("No timestamp")
            elif name == "metadata_complete":
                has_ids = bool(msg_ids)
                has_lang = any(m.get("language") for m in messages)
                if has_ids and has_lang:
                    results[eid] = _present("IDs and language present")
                else:
                    results[eid] = _absent("Incomplete metadata")
            else:
                results[eid] = _absent(f"Unknown metadata: {name}")
            continue

        # Threading
        if "reply" in name and ("link" in name or "threading" in name):
            results[eid] = _present(f"In-reply-to: {reply_tos}") if reply_tos else _absent("No :in-reply-to")
            continue

        # Content facts — search in :content and raw text
        found = _check_content_fact(name, check, text_lower, cleaned)
        if found:
            results[eid] = _present(found)
            continue

        # Compound
        if name == "multiple_messages":
            results[eid] = _present(f"{msg_count} messages") if msg_count >= 3 else _absent(f"Only {msg_count}")
            continue

        if eid not in results:
            results[eid] = _absent(f"Not found: {name}")

    return results


# ── Dispatcher ─────────────────────────────────────────────────────────

EXTRACTORS = {
    "axon": extract_axon,
    "json_fc": extract_json_fc,
    "fipa_acl": extract_fipa_acl,
}

# Conditions that use automated extraction as primary scoring
MACHINE_SCORED_CONDITIONS = {"axon", "json_fc", "fipa_acl"}

# Conditions that require LLM judge scoring
JUDGE_SCORED_CONDITIONS = {"free_english", "structured_english", "instruction_matched_english"}


def extract_elements(condition: str, output: str, elements: list[dict],
                     task_id: str) -> Optional[dict[str, dict]]:
    """Extract semantic elements from an output.

    Returns dict of {element_id: {"verdict": str, "evidence": str}} or None
    if the condition requires judge scoring (English conditions).
    """
    extractor = EXTRACTORS.get(condition)
    if extractor is None:
        return None  # Signals: use judge scoring
    return extractor(output, elements, task_id)
