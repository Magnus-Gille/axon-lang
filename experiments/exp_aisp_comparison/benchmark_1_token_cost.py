#!/usr/bin/env python3
"""
Benchmark 1: Hand-Written Token Cost Comparison

Same communication scenario written in both AXON and AISP.
Direct token count comparison using tiktoken.

Question answered: "How many tokens does it take to say the same thing?"
"""

import tiktoken

enc = tiktoken.get_encoding("cl100k_base")


def count(text: str) -> int:
    return len(enc.encode(text))


# ── Scenarios ────────────────────────────────────────────────────────
# Each scenario has the same semantic content in both formats.

SCENARIOS = [
    {
        "id": "S1",
        "name": "Simple status query",
        "description": "Agent A asks Agent B for the status of a web server.",
        "axon": '[id:"m1", %%:1]\nQRY(@agent-a>@agent-b): status(@web-server)',
        "aisp": '𝔸1.0.status-query@2026-02-27\nγ≔agent-comm\n\n⟦Ω:Meta⟧{\n  sender≜@agent-a\n  receiver≜@agent-b\n  intent≜query\n  id≜"m1"\n  protocol≜1\n}\n\n⟦Σ:Types⟧{\n  Server≜{name:String, health:Status}\n}\n\n⟦Γ:Rules⟧{\n  ∀s∈Server:health(s)∈{healthy,degraded,down}\n}\n\n⟦Λ:Funcs⟧{\n  getStatus≜λ(srv).health(srv)\n}\n\n⟦Ε⟧⟨δ≜0.75;φ≜100;τ≜◊⁺⁺⟩',
    },
    {
        "id": "S2",
        "name": "Status reply with data",
        "description": "Agent B replies with server health info: healthy, 99.7% uptime.",
        "axon": '[id:"m2", %%:1, re:"m1"]\nINF(@agent-b>@agent-a): #status{server:@web-server, health:#healthy, uptime:99.7%}',
        "aisp": '𝔸1.0.status-reply@2026-02-27\nγ≔agent-comm\n\n⟦Ω:Meta⟧{\n  sender≜@agent-b\n  receiver≜@agent-a\n  intent≜inform\n  id≜"m2"\n  reply_to≜"m1"\n  protocol≜1\n}\n\n⟦Σ:Types⟧{\n  StatusReport≜{server:String, health:Status, uptime:Float}\n  Status≜{healthy,degraded,down}\n}\n\n⟦Γ:Rules⟧{\n  server≜"web-server"\n  health≜healthy\n  uptime≜99.7\n}\n\n⟦Λ:Funcs⟧{\n  report≜λ().{server:"web-server", health:healthy, uptime:99.7}\n}\n\n⟦Ε⟧⟨δ≜0.75;φ≜100;τ≜◊⁺⁺⟩',
    },
    {
        "id": "S3",
        "name": "Task delegation with deadline",
        "description": "Agent A delegates a database backup task to Agent C, due in 2 hours.",
        "axon": '[id:"m3", %%:1, ^:3]\nREQ(@agent-a>@agent-c): backup(@primary-db) -> verify(#checksum) [deadline:2h]',
        "aisp": '𝔸1.0.backup-request@2026-02-27\nγ≔agent-comm\n\n⟦Ω:Meta⟧{\n  sender≜@agent-a\n  receiver≜@agent-c\n  intent≜request\n  id≜"m3"\n  priority≜3\n  protocol≜1\n}\n\n⟦Σ:Types⟧{\n  Task≜{action:String, target:String, deadline:Duration}\n  Duration≜{value:Int, unit:String}\n}\n\n⟦Γ:Rules⟧{\n  action≜"backup"\n  target≜"primary-db"\n  deadline≜{value:2, unit:"hours"}\n  ∀backup:verify(checksum(backup))\n}\n\n⟦Λ:Funcs⟧{\n  backup≜λ(db).dump(db)→verify(checksum)\n}\n\n⟦Ε⟧⟨δ≜0.75;φ≜100;τ≜◊⁺⁺⟩',
    },
    {
        "id": "S4",
        "name": "Error report with cause chain",
        "description": "Agent B reports a connection timeout caused by DNS failure caused by network partition.",
        "axon": '[id:"m4", %%:1, ^:5]\nERR(@agent-b>@agent-a): #error{type:#timeout, service:@api-gateway} <- #cause{type:#dns_failure, resolver:@dns-1} <- #cause{type:#network_partition, segment:"zone-b"}',
        "aisp": '𝔸1.0.error-report@2026-02-27\nγ≔agent-comm\n\n⟦Ω:Meta⟧{\n  sender≜@agent-b\n  receiver≜@agent-a\n  intent≜error\n  id≜"m4"\n  priority≜5\n  protocol≜1\n}\n\n⟦Σ:Types⟧{\n  Error≜{type:ErrorType, service:String, cause:Cause}\n  Cause≜{type:ErrorType, detail:String, cause:Cause?}\n  ErrorType≜{timeout,dns_failure,network_partition}\n}\n\n⟦Γ:Rules⟧{\n  error≜{type:timeout, service:"api-gateway"}\n  cause1≜{type:dns_failure, resolver:"dns-1"}\n  cause2≜{type:network_partition, segment:"zone-b"}\n  error.cause≜cause1\n  cause1.cause≜cause2\n}\n\n⟦Λ:Funcs⟧{\n  rootCause≜λ(e).e.cause=∅⇒e|rootCause(e.cause)\n}\n\n⟦Ε⟧⟨δ≜0.75;φ≜100;τ≜◊⁺⁺⟩',
    },
    {
        "id": "S5",
        "name": "Proposal with price",
        "description": "Agent A proposes to Agent B: run load test on staging for $2.50, takes 45 minutes.",
        "axon": '[id:"m5", %%:1]\nPRO(@agent-a>@agent-b): #proposal{task:"load-test", target:@staging, cost:2.50usd, duration:45min}',
        "aisp": '𝔸1.0.proposal@2026-02-27\nγ≔agent-comm\n\n⟦Ω:Meta⟧{\n  sender≜@agent-a\n  receiver≜@agent-b\n  intent≜propose\n  id≜"m5"\n  protocol≜1\n}\n\n⟦Σ:Types⟧{\n  Proposal≜{task:String, target:String, cost:Money, duration:Duration}\n  Money≜{amount:Float, currency:String}\n  Duration≜{value:Int, unit:String}\n}\n\n⟦Γ:Rules⟧{\n  task≜"load-test"\n  target≜"staging"\n  cost≜{amount:2.50, currency:"usd"}\n  duration≜{value:45, unit:"minutes"}\n}\n\n⟦Λ:Funcs⟧{\n  accept≜λ(p).schedule(p.task, p.target)\n}\n\n⟦Ε⟧⟨δ≜0.75;φ≜100;τ≜◊⁺⁺⟩',
    },
    {
        "id": "S6",
        "name": "Multi-step pipeline",
        "description": "Agent A tells Agent B to fetch a URL, parse as JSON, extract the 'data' field, store in the database.",
        "axon": '[id:"m6", %%:1]\nCMD(@agent-a>@agent-b): fetch("https://api.example.com/v1/data") -> parse("json") -> extract("data") -> store(@results-db)',
        "aisp": '𝔸1.0.pipeline@2026-02-27\nγ≔agent-comm\n\n⟦Ω:Meta⟧{\n  sender≜@agent-a\n  receiver≜@agent-b\n  intent≜command\n  id≜"m6"\n  protocol≜1\n}\n\n⟦Σ:Types⟧{\n  Pipeline≜Step[]\n  Step≜{action:String, params:Map}\n}\n\n⟦Γ:Rules⟧{\n  step1≜{action:"fetch", url:"https://api.example.com/v1/data"}\n  step2≜{action:"parse", format:"json"}\n  step3≜{action:"extract", field:"data"}\n  step4≜{action:"store", target:"results-db"}\n  ∀i∈[1..3]:step(i).output→step(i+1).input\n}\n\n⟦Λ:Funcs⟧{\n  run≜λ(steps).fold(steps, λ(acc,s).s.action(acc))\n}\n\n⟦Ε⟧⟨δ≜0.75;φ≜100;τ≜◊⁺⁺⟩',
    },
    {
        "id": "S7",
        "name": "Alert with severity and affected services",
        "description": "Monitoring agent broadcasts: disk usage at 94% on storage-1, affects backup-service and log-service, severity critical.",
        "axon": '[id:"m7", %%:1, ^:5]\nPUB(@monitor>@all): #alert{type:#disk_usage, node:@storage-1, value:94%, severity:#critical, affects:[@backup-service, @log-service]}',
        "aisp": '𝔸1.0.alert@2026-02-27\nγ≔agent-comm\n\n⟦Ω:Meta⟧{\n  sender≜@monitor\n  receiver≜@all\n  intent≜alert\n  id≜"m7"\n  priority≜5\n  protocol≜1\n}\n\n⟦Σ:Types⟧{\n  Alert≜{type:AlertType, node:String, value:Float, severity:Severity, affects:String[]}\n  AlertType≜{disk_usage,cpu,memory,network}\n  Severity≜{info,warning,critical}\n}\n\n⟦Γ:Rules⟧{\n  type≜disk_usage\n  node≜"storage-1"\n  value≜94.0\n  severity≜critical\n  affects≜["backup-service","log-service"]\n}\n\n⟦Λ:Funcs⟧{\n  escalate≜λ(a).a.severity=critical⇒notify(oncall)\n}\n\n⟦Ε⟧⟨δ≜0.75;φ≜100;τ≜◊⁺⁺⟩',
    },
    {
        "id": "S8",
        "name": "Negotiation counter-offer",
        "description": "Agent B counters Agent A's proposal: accepts the task but wants $3.75 instead of $2.50, and 60 minutes instead of 45.",
        "axon": '[id:"m8", %%:1, re:"m5"]\nCTR(@agent-b>@agent-a): #counter{original:"m5", accept:["task", "target"], modify:{cost:3.75usd, duration:60min}, reason:"resource contention"}',
        "aisp": '𝔸1.0.counter@2026-02-27\nγ≔agent-comm\n\n⟦Ω:Meta⟧{\n  sender≜@agent-b\n  receiver≜@agent-a\n  intent≜counter\n  id≜"m8"\n  reply_to≜"m5"\n  protocol≜1\n}\n\n⟦Σ:Types⟧{\n  Counter≜{original:String, accepted:String[], modified:Map, reason:String}\n  Money≜{amount:Float, currency:String}\n  Duration≜{value:Int, unit:String}\n}\n\n⟦Γ:Rules⟧{\n  original≜"m5"\n  accepted≜["task","target"]\n  modified_cost≜{amount:3.75, currency:"usd"}\n  modified_duration≜{value:60, unit:"minutes"}\n  reason≜"resource contention"\n}\n\n⟦Λ:Funcs⟧{\n  resolve≜λ(c).merge(original(c), c.modified)\n}\n\n⟦Ε⟧⟨δ≜0.75;φ≜100;τ≜◊⁺⁺⟩',
    },
]


def main():
    print("=" * 80)
    print("BENCHMARK 1: Hand-Written Token Cost Comparison")
    print("=" * 80)
    print("\n  Same semantic content, both formats. Token counts via cl100k_base.\n")

    print(f"  {'ID':<4} {'Scenario':<35} {'AXON':>6} {'AISP':>6} {'Ratio':>7} {'AXON chars':>11} {'AISP chars':>11}")
    print("  " + "-" * 82)

    axon_total = 0
    aisp_total = 0
    axon_chars_total = 0
    aisp_chars_total = 0

    for s in SCENARIOS:
        axon_tok = count(s["axon"])
        aisp_tok = count(s["aisp"])
        ratio = aisp_tok / axon_tok if axon_tok > 0 else float("inf")
        axon_total += axon_tok
        aisp_total += aisp_tok
        axon_chars_total += len(s["axon"])
        aisp_chars_total += len(s["aisp"])
        print(f"  {s['id']:<4} {s['name']:<35} {axon_tok:>6} {aisp_tok:>6} {ratio:>6.1f}x {len(s['axon']):>11} {len(s['aisp']):>11}")

    ratio_total = aisp_total / axon_total if axon_total > 0 else 0
    print("  " + "-" * 82)
    print(f"  {'':>4} {'TOTAL':<35} {axon_total:>6} {aisp_total:>6} {ratio_total:>6.1f}x {axon_chars_total:>11} {aisp_chars_total:>11}")
    print(f"  {'':>4} {'MEAN per scenario':<35} {axon_total/len(SCENARIOS):>6.0f} {aisp_total/len(SCENARIOS):>6.0f}")

    print(f"\n  AISP uses {ratio_total:.1f}x more tokens than AXON for identical content.")
    print(f"  AXON average: {axon_total/len(SCENARIOS):.0f} tokens/message")
    print(f"  AISP average: {aisp_total/len(SCENARIOS):.0f} tokens/message")
    print(f"  Overhead per message: +{(aisp_total - axon_total)/len(SCENARIOS):.0f} tokens")

    # Show the smallest and largest scenarios
    print("\n  DETAILED EXAMPLES:")
    # Show S1 (simplest)
    s1 = SCENARIOS[0]
    print(f"\n  --- {s1['name']} ---")
    print(f"  AXON ({count(s1['axon'])} tokens):")
    for line in s1["axon"].split("\n"):
        print(f"    {line}")
    print(f"\n  AISP ({count(s1['aisp'])} tokens):")
    for line in s1["aisp"].split("\n"):
        print(f"    {line}")

    # Show S4 (most complex)
    s4 = SCENARIOS[3]
    print(f"\n  --- {s4['name']} ---")
    print(f"  AXON ({count(s4['axon'])} tokens):")
    for line in s4["axon"].split("\n"):
        print(f"    {line}")
    print(f"\n  AISP ({count(s4['aisp'])} tokens):")
    for line in s4["aisp"].split("\n"):
        print(f"    {line}")


if __name__ == "__main__":
    main()
