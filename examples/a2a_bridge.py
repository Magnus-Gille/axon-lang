"""
AXON ↔ A2A Bridge Example
==========================

Demonstrates how AXON messages fit inside Google's A2A protocol as a
token-efficient message format. A2A handles transport, discovery, and
task lifecycle; AXON optimizes the payload.

This is a conceptual example — it does not depend on an A2A SDK.
It shows the data structures and token savings.

See: https://github.com/google/A2A
"""

import json
import sys
import os

# Add parent src/ to path for the AXON parser
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

try:
    from axon_parser import Lexer, Parser
    HAS_PARSER = True
except ImportError:
    HAS_PARSER = False


# ---------------------------------------------------------------------------
# 1. AXON-formatted A2A Task
# ---------------------------------------------------------------------------

def create_a2a_task_with_axon():
    """
    An A2A task where the message payload uses AXON instead of plain JSON.

    A2A's Part.media_type field allows any MIME type, so agents can
    declare and use "application/axon" through standard content negotiation.
    """

    # --- AXON payload (compact, semantic) ---
    axon_payload = 'REQ(@orchestrator>@analyzer): analyze($dataset) -> summarize(#brief, max_tokens:500) & extract(#entities)'

    # --- Equivalent JSON function-calling payload (verbose) ---
    json_payload = json.dumps({
        "role": "orchestrator",
        "target": "analyzer",
        "intent": "request",
        "actions": {
            "sequence": [
                {
                    "function": "analyze",
                    "arguments": {"data": "$dataset"}
                },
                {
                    "parallel": [
                        {
                            "function": "summarize",
                            "arguments": {
                                "format": "brief",
                                "max_tokens": 500
                            }
                        },
                        {
                            "function": "extract",
                            "arguments": {
                                "type": "entities"
                            }
                        }
                    ]
                }
            ]
        }
    })

    # --- A2A task with AXON-formatted payload ---
    # Uses A2A spec field names: method "message/send", role "ROLE_USER",
    # Part.mediaType (camelCase per ProtoJSON/ADR-001), messageId required.
    a2a_task_axon = {
        "jsonrpc": "2.0",
        "id": "req-001",
        "method": "message/send",
        "params": {
            "message": {
                "messageId": "msg-001",
                "role": "ROLE_USER",
                "parts": [{
                    "text": axon_payload,
                    "mediaType": "application/axon"
                }]
            }
        }
    }

    # --- Same task with JSON payload ---
    a2a_task_json = {
        "jsonrpc": "2.0",
        "id": "req-001",
        "method": "message/send",
        "params": {
            "message": {
                "messageId": "msg-001",
                "role": "ROLE_USER",
                "parts": [{
                    "text": json_payload,
                    "mediaType": "application/json"
                }]
            }
        }
    }

    return a2a_task_axon, a2a_task_json, axon_payload, json_payload


# ---------------------------------------------------------------------------
# 2. A2A Agent Card advertising AXON support
# ---------------------------------------------------------------------------

def create_axon_agent_card():
    """
    An A2A Agent Card that declares AXON as a supported input/output format.

    A2A's content negotiation lets clients discover AXON support and
    request AXON-formatted responses via acceptedOutputModes.
    """
    # Agent Card per A2A spec: supportedInterfaces required,
    # skills have tags, roles use ROLE_ prefix.
    return {
        "name": "Data Analysis Agent",
        "description": "Analyzes datasets and returns structured insights",
        "version": "1.0.0",
        "supportedInterfaces": [{
            "url": "https://agents.example.com/analyzer",
            "protocolBinding": "JSONRPC",
            "protocolVersion": "1.0"
        }],
        "capabilities": {
            "streaming": True,
            "extensions": [{
                "uri": "https://axon-lang.dev/ext/axon/v1",
                "description": "Accepts and produces AXON-formatted payloads for token-efficient agent communication",
                "required": False,
                "params": {
                    "axonVersion": "0.1",
                    "tier": 2,
                    "performatives": ["REQ", "RPL", "INF", "QRY", "ERR", "ACK"]
                }
            }]
        },
        "defaultInputModes": ["text/plain", "application/json", "application/axon"],
        "defaultOutputModes": ["text/plain", "application/json", "application/axon"],
        "skills": [
            {
                "id": "analyze",
                "name": "Dataset Analysis",
                "description": "Analyze a dataset and return structured insights",
                "tags": ["analysis", "data", "insights"],
                "inputModes": ["application/axon", "application/json"],
                "outputModes": ["application/axon", "application/json"],
                "examples": [
                    "REQ(@client>@analyzer): analyze($data, format:#summary)",
                    "REQ(@client>@analyzer): analyze($data) -> extract(#trends) & extract(#anomalies)"
                ]
            }
        ]
    }


# ---------------------------------------------------------------------------
# 3. A2A response with AXON artifact
# ---------------------------------------------------------------------------

def create_axon_response_artifact():
    """
    An A2A task completion with AXON-formatted artifacts.
    """
    axon_result = 'RPL(@analyzer>@orchestrator): {sentiment:#positive, confidence:0.92, topics:[#tech, #ai, #infrastructure], summary:"Growth trend detected across all segments", entities:[{name:"Acme Corp", type:#org, mentions:12}, {name:"Q4 2026", type:#temporal, mentions:8}]}'

    json_result = json.dumps({
        "role": "analyzer",
        "target": "orchestrator",
        "intent": "reply",
        "result": {
            "sentiment": "positive",
            "confidence": 0.92,
            "topics": ["tech", "ai", "infrastructure"],
            "summary": "Growth trend detected across all segments",
            "entities": [
                {"name": "Acme Corp", "type": "org", "mentions": 12},
                {"name": "Q4 2026", "type": "temporal", "mentions": 8}
            ]
        }
    })

    a2a_response = {
        "jsonrpc": "2.0",
        "id": "req-001",
        "result": {
            "id": "task-123",
            "status": {
                "state": "TASK_STATE_COMPLETED",
                "timestamp": "2026-03-23T10:46:00Z"
            },
            "artifacts": [{
                "artifactId": "result-1",
                "name": "Analysis Results",
                "parts": [{
                    "text": axon_result,
                    "mediaType": "application/axon"
                }]
            }]
        }
    }

    return a2a_response, axon_result, json_result


# ---------------------------------------------------------------------------
# 4. Token comparison
# ---------------------------------------------------------------------------

def estimate_tokens(text):
    """
    Rough token estimate: ~4 characters per token (GPT/Claude average).
    Real tokenizers vary, but this gives a directional comparison.
    """
    return len(text) / 4.0


def compare_payloads():
    """Compare AXON vs JSON payload sizes in A2A context."""

    _, _, axon_req, json_req = create_a2a_task_with_axon()
    _, axon_resp, json_resp = create_axon_response_artifact()

    print("=" * 65)
    print("AXON vs JSON Payload Comparison (inside A2A)")
    print("=" * 65)

    # Request comparison
    print("\n--- Request Payload ---")
    print(f"AXON ({len(axon_req)} chars, ~{estimate_tokens(axon_req):.0f} tokens):")
    print(f"  {axon_req}")
    print(f"\nJSON ({len(json_req)} chars, ~{estimate_tokens(json_req):.0f} tokens):")
    print(f"  {json_req[:120]}...")

    req_savings = (1 - len(axon_req) / len(json_req)) * 100
    print(f"\n  Request savings: {req_savings:.0f}% fewer characters")

    # Response comparison
    print("\n--- Response Payload ---")
    print(f"AXON ({len(axon_resp)} chars, ~{estimate_tokens(axon_resp):.0f} tokens):")
    print(f"  {axon_resp[:120]}...")
    print(f"\nJSON ({len(json_resp)} chars, ~{estimate_tokens(json_resp):.0f} tokens):")
    print(f"  {json_resp[:120]}...")

    resp_savings = (1 - len(axon_resp) / len(json_resp)) * 100
    print(f"\n  Response savings: {resp_savings:.0f}% fewer characters")

    # Aggregate
    total_axon = len(axon_req) + len(axon_resp)
    total_json = len(json_req) + len(json_resp)
    total_savings = (1 - total_axon / total_json) * 100

    print(f"\n{'=' * 65}")
    print(f"Total payload: AXON {total_axon} chars vs JSON {total_json} chars")
    print(f"Overall savings: {total_savings:.0f}% fewer characters")
    print(f"{'=' * 65}")

    # Experimental context
    print("\nNote: Controlled experiments (Exp 1, N=486) measured AXON at")
    print("15.4 tok/unit vs JSON FC at 22.6 tok/unit — a 32% reduction")
    print("with statistical significance (p < 0.001).")

    # Validate AXON if parser available
    if HAS_PARSER:
        print("\n--- Parser Validation ---")
        for label, axon_text in [("Request", axon_req), ("Response", axon_resp)]:
            try:
                lexer = Lexer(axon_text)
                tokens = lexer.tokenize()
                parser = Parser(tokens)
                ast = parser.parse()  # returns list of Message dataclasses
                perf = ast[0].performative if ast else "N/A"
                print(f"  {label}: VALID (performative: {perf})")
            except Exception as e:
                print(f"  {label}: Parse note — {e}")

    return total_savings


# ---------------------------------------------------------------------------
# 5. Multi-agent workflow comparison
# ---------------------------------------------------------------------------

def multi_agent_workflow_comparison():
    """
    Simulates a 5-agent A2A workflow to show cumulative token savings.

    Scenario: An orchestrator coordinates analysis, summarization,
    translation, validation, and storage across 5 specialist agents.
    """

    axon_messages = [
        'REQ(@orch>@fetcher): fetch("https://api.example.com/data", format:#json)',
        'RPL(@fetcher>@orch): {status:#ok, records:1847, size:2.4MB}',
        'REQ(@orch>@analyzer): analyze($data) -> classify(#sentiment) & detect(#anomalies)',
        'RPL(@analyzer>@orch): {sentiment:#mixed, anomalies:3, confidence:0.89}',
        'REQ(@orch>@summarizer): summarize($analysis, style:#executive, max_tokens:200)',
        'RPL(@summarizer>@orch): {summary:"Q4 shows mixed sentiment with 3 anomalies...", tokens:47}',
        'REQ(@orch>@translator): translate($summary, lang:#ja)',
        'RPL(@translator>@orch): {text:"Q4\u306f\u6df7\u5408\u611f\u60c5...", lang:#ja, confidence:0.95}',
        'REQ(@orch>@store): persist({report:$summary, translation:$ja_text, metadata:$analysis})',
        'ACK(@store>@orch): {id:"report-2026-q4", stored:T, replicas:3}',
    ]

    json_messages = [
        json.dumps({"intent": "request", "from": "orchestrator", "to": "fetcher", "action": "fetch", "args": {"url": "https://api.example.com/data", "format": "json"}}),
        json.dumps({"intent": "reply", "from": "fetcher", "to": "orchestrator", "result": {"status": "ok", "records": 1847, "size": "2.4mb"}}),
        json.dumps({"intent": "request", "from": "orchestrator", "to": "analyzer", "actions": [{"action": "analyze", "args": {"data": "$data"}}, {"parallel": [{"action": "classify", "args": {"type": "sentiment"}}, {"action": "detect", "args": {"type": "anomalies"}}]}]}),
        json.dumps({"intent": "reply", "from": "analyzer", "to": "orchestrator", "result": {"sentiment": "mixed", "anomalies": 3, "confidence": 0.89}}),
        json.dumps({"intent": "request", "from": "orchestrator", "to": "summarizer", "action": "summarize", "args": {"input": "$analysis", "style": "executive", "max_tokens": 200}}),
        json.dumps({"intent": "reply", "from": "summarizer", "to": "orchestrator", "result": {"summary": "Q4 shows mixed sentiment with 3 anomalies...", "tokens": 47}}),
        json.dumps({"intent": "request", "from": "orchestrator", "to": "translator", "action": "translate", "args": {"input": "$summary", "language": "ja"}}),
        json.dumps({"intent": "reply", "from": "translator", "to": "orchestrator", "result": {"text": "Q4\u306f\u6df7\u5408\u611f\u60c5...", "language": "ja", "confidence": 0.95}}),
        json.dumps({"intent": "request", "from": "orchestrator", "to": "store", "action": "persist", "args": {"report": "$summary", "translation": "$ja_text", "metadata": "$analysis"}}),
        json.dumps({"intent": "reply", "from": "store", "to": "orchestrator", "result": {"id": "report-2026-q4", "stored": True, "replicas": 3}}),
    ]

    axon_total = sum(len(m) for m in axon_messages)
    json_total = sum(len(m) for m in json_messages)
    savings = (1 - axon_total / json_total) * 100

    print(f"\n{'=' * 65}")
    print("Multi-Agent Workflow: 5 agents, 10 messages")
    print(f"{'=' * 65}")
    print(f"AXON total: {axon_total} chars (~{axon_total/4:.0f} tokens)")
    print(f"JSON total: {json_total} chars (~{json_total/4:.0f} tokens)")
    print(f"Savings:    {savings:.0f}% fewer characters")
    print(f"\nAt 1000 workflows/day: ~{(json_total - axon_total) * 1000 / 4:.0f} tokens saved/day")
    print(f"{'=' * 65}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("AXON ↔ A2A Bridge Example")
    print("A2A handles transport & discovery. AXON optimizes the payload.\n")

    # Show agent card
    card = create_axon_agent_card()
    print("Agent Card (declares AXON support):")
    print(f"  Input modes:  {card['defaultInputModes']}")
    print(f"  Output modes: {card['defaultOutputModes']}")
    print(f"  Extension:    {card['capabilities']['extensions'][0]['uri']}")

    # Compare payloads
    compare_payloads()

    # Multi-agent workflow
    multi_agent_workflow_comparison()
