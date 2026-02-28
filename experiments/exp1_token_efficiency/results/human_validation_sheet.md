# Human Validation Scoring Sheet

Generated: 2026-02-16 11:28 UTC
Source: codex results, seed=42
Items: 30 (target: 5 per condition)

## Instructions

For each item below, read the task instruction and the model's output.
Then mark each element as:
- **P** = PRESENT (the element is expressed accurately)
- **A** = ABSENT (the element is not expressed)
- **I** = INCORRECT (the element is expressed but factually wrong)

Replace the `[ ]` with `[P]`, `[A]`, or `[I]`.

---

## Item 1: L1-02 / free_english / codex / run#1

**Task**: Agent B tells Agent A that the server is healthy with 99.7% uptime.

**Output**:
```
From Agent B to Agent A: The server is healthy with 99.7% uptime.
```

**Scoring method**: judge

**Elements** (mark P, A, or I):
- [P] a1 sender — A sending agent is identified *(current: PRESENT)*
- [P] a2 receiver — A receiving agent is identified *(current: PRESENT)*
- [P] a3 inform_intent — An inform or tell action is expressed *(current: PRESENT)*
- [P] a4 status — Server health status is communicated (healthy/ok/up) *(current: PRESENT)*
- [P] a5 uptime_value — A numeric uptime value close to 99.7% is present *(current: PRESENT)*

---

## Item 2: L2-01 / free_english / codex / run#1

**Task**: A CI agent requests a builder agent to build a specific repo branch and commit.

**Output**:
```
From: CI Agent
To: Builder Agent
Message: Please build the repository branch `feature/ci-improvements` at commit `7e3a9b4c1d2f6a8b5c0e4f9a1b2c3d4e5f6a7b8c`.
```

**Scoring method**: judge

**Elements** (mark P, A, or I):
- [P] a1 sender — A sending agent (CI agent) is identified *(current: PRESENT)*
- [P] a2 receiver — A receiving agent (builder) is identified *(current: PRESENT)*
- [P] a3 request_intent — A request or command action is expressed *(current: PRESENT)*
- [P] a4 repo — A repository identifier is present (any name/string) *(current: PRESENT)*
- [P] a5 branch — A branch identifier is present (any name/string) *(current: PRESENT)*
- [P] a6 commit — A commit reference is present (any hash/string) *(current: PRESENT)*

---

## Item 3: L3-02 / free_english / codex / run#2

**Task**: A monitor publishes a severity-2 incident alert about payments service with latency > 2s. Include priority level 4, the causal chain (high latency caused by database connection pool exhaustion caused by traffic spike), and a resolution recommendation.

**Output**:
```
From: Monitor Agent
To: Incident Response Agent
Message: Severity-2 incident alert for the Payments Service: latency is above 2s. Priority level: 4. Causal chain: high latency is caused by database connection pool exhaustion, which is caused by a traffic spike. Recommended resolution: immediately reduce load (rate limit or shed traffic), scale application and database capacity, safely tune/increase the connection pool, and monitor until latency drops below threshold.
```

**Scoring method**: judge

**Elements** (mark P, A, or I):
- [P] a1 sender — A monitor agent is identified *(current: PRESENT)*
- [P] a2 receiver — A receiving agent is identified (any agent or broadcast) *(current: PRESENT)*
- [P] a3 alert_intent — An alert/publish/incident action is expressed *(current: PRESENT)*
- [P] a4 severity — Severity level 2 is specified *(current: PRESENT)*
- [P] a5 priority — Priority level 4 is specified *(current: PRESENT)*
- [P] a6 causal_chain — A causal chain linking high latency, pool exhaustion, and traffic spike is expressed *(current: PRESENT)*
- [P] a7 recommendation — A resolution recommendation is present *(current: PRESENT)*

---

## Item 4: L1-01 / free_english / codex / run#2

**Task**: Agent A asks Agent B for the status of a web server.

**Output**:
```
From: Agent A
To: Agent B
Message: Can you provide the current status of the web server, including whether it is up and any active issues?
```

**Scoring method**: judge

**Elements** (mark P, A, or I):
- [P] a1 sender — A sending agent is identified *(current: PRESENT)*
- [P] a2 receiver — A receiving agent is identified *(current: PRESENT)*
- [P] a3 query_intent — A query or question is expressed *(current: PRESENT)*
- [P] a4 target_server — A web server is referenced as the query target *(current: PRESENT)*

---

## Item 5: L3-01 / free_english / codex / run#1

**Task**: An orchestrator instructs a pipeline to fetch a URL, parse it as JSON, then store the result in a database. Include message ID and protocol version.

**Output**:
```
Message-ID: msg-001
Protocol-Version: 1.0
From: Orchestrator Agent
To: Pipeline Agent
Message: Please fetch the provided URL, parse the response as JSON, and store the parsed result in the database.
```

**Scoring method**: judge

**Elements** (mark P, A, or I):
- [P] a1 sender — An orchestrator agent is identified *(current: PRESENT)*
- [P] a2 receiver — A pipeline/receiver agent is identified *(current: PRESENT)*
- [P] a3 request_intent — An instruction/request action is expressed *(current: PRESENT)*
- [P] a4 sequence_of_actions — A sequence of fetch→parse→store actions is expressed in order *(current: PRESENT)*
- [P] a5 metadata_id — A message ID is present *(current: PRESENT)*
- [P] a6 metadata_version — A protocol version is present *(current: PRESENT)*

---

## Item 6: L1-02 / structured_english / codex / run#1

**Task**: Agent B tells Agent A that the server is healthy with 99.7% uptime.

**Output**:
```
FROM: agent-b
TO: agent-a
TYPE: inform
CONTENT: The server is healthy with 99.7% uptime.
```

**Scoring method**: judge

**Elements** (mark P, A, or I):
- [P] a1 sender — A sending agent is identified *(current: PRESENT)*
- [P] a2 receiver — A receiving agent is identified *(current: PRESENT)*
- [P] a3 inform_intent — An inform or tell action is expressed *(current: PRESENT)*
- [P] a4 status — Server health status is communicated (healthy/ok/up) *(current: PRESENT)*
- [P] a5 uptime_value — A numeric uptime value close to 99.7% is present *(current: PRESENT)*

---

## Item 7: L2-03 / structured_english / codex / run#3

**Task**: A planner distributes a data processing task across 3 workers, splitting range 0-3000 into three equal segments.

**Output**:
```
FROM: planner
TO: workers
TYPE: inform
CONTENT: Data processing range 0-3000 has been split equally across 3 workers: worker-1 handles 0-1000, worker-2 handles 1000-2000, and worker-3 handles 2000-3000.
```

**Scoring method**: judge

**Elements** (mark P, A, or I):
- [P] a1 sender — A planner agent is identified *(current: PRESENT)*
- [P] a2 receivers_multiple — Multiple worker agents (3) are addressed *(current: PRESENT)*
- [P] a3 request_intent — A task distribution/request action is expressed *(current: PRESENT)*
- [P] a4 task_type — Data processing is mentioned as the task type *(current: PRESENT)*
- [P] a5 data_ranges — Data ranges covering 0-3000 in three segments are specified *(current: PRESENT)*

---

## Item 8: L3-02 / structured_english / codex / run#1

**Task**: A monitor publishes a severity-2 incident alert about payments service with latency > 2s. Include priority level 4, the causal chain (high latency caused by database connection pool exhaustion caused by traffic spike), and a resolution recommendation.

**Output**:
```
FROM: monitor-agent
TO: incident-commander
TYPE: inform
CONTENT: Severity-2 incident alert: Payments service latency is above 2s. Priority level: 4. Causal chain: traffic spike caused database connection pool exhaustion, which caused high latency. Resolution recommendation: immediately scale service and database capacity, tune/increase connection pool limits, apply rate limiting/backpressure, and monitor latency plus pool utilization until stable.
```

**Scoring method**: judge

**Elements** (mark P, A, or I):
- [P] a1 sender — A monitor agent is identified *(current: PRESENT)*
- [P] a2 receiver — A receiving agent is identified (any agent or broadcast) *(current: PRESENT)*
- [ ] a3 alert_intent — An alert/publish/incident action is expressed *(current: PRESENT)*
- [ ] a4 severity — Severity level 2 is specified *(current: PRESENT)*
- [ ] a5 priority — Priority level 4 is specified *(current: PRESENT)*
- [ ] a6 causal_chain — A causal chain linking high latency, pool exhaustion, and traffic spike is expressed *(current: PRESENT)*
- [ ] a7 recommendation — A resolution recommendation is present *(current: PRESENT)*

---

## Item 9: L1-03 / structured_english / codex / run#3

**Task**: A service agent reports a 404 not-found error to the caller agent.

**Output**:
```
FROM: service-agent
TO: caller-agent
TYPE: error
CONTENT: Request failed with 404 Not Found. The requested resource could not be located.
```

**Scoring method**: judge

**Elements** (mark P, A, or I):
- [ ] a1 sender — A sending agent (service agent) is identified *(current: PRESENT)*
- [ ] a2 receiver — A receiving agent (caller) is identified *(current: PRESENT)*
- [ ] a3 error_intent — An error report action is expressed *(current: PRESENT)*
- [ ] a4 error_code — The numeric code 404 is present *(current: PRESENT)*
- [ ] a5 error_description — A 'not found' description is present *(current: PRESENT)*

---

## Item 10: L3-01 / structured_english / codex / run#2

**Task**: An orchestrator instructs a pipeline to fetch a URL, parse it as JSON, then store the result in a database. Include message ID and protocol version.

**Output**:
```
FROM: orchestrator
TO: pipeline
TYPE: request
CONTENT: Message-ID: msg-001; Protocol-Version: 1.0; Fetch the URL https://example.com/data.json, parse the response as JSON, then store the parsed result in the database.
```

**Scoring method**: judge

**Elements** (mark P, A, or I):
- [ ] a1 sender — An orchestrator agent is identified *(current: PRESENT)*
- [ ] a2 receiver — A pipeline/receiver agent is identified *(current: PRESENT)*
- [ ] a3 request_intent — An instruction/request action is expressed *(current: PRESENT)*
- [ ] a4 sequence_of_actions — A sequence of fetch→parse→store actions is expressed in order *(current: PRESENT)*
- [ ] a5 metadata_id — A message ID is present *(current: PRESENT)*
- [ ] a6 metadata_version — A protocol version is present *(current: PRESENT)*

---

## Item 11: L1-01 / instruction_matched_english / codex / run#1

**Task**: Agent A asks Agent B for the status of a web server.

**Output**:
```
[message-id: m1]
[timestamp: 1770940800]
[context: convo-1]
QUERY (agent-a -> agent-b):
  target: web-server
  property: status
```

**Scoring method**: judge

**Elements** (mark P, A, or I):
- [ ] a1 sender — A sending agent is identified *(current: PRESENT)*
- [ ] a2 receiver — A receiving agent is identified *(current: PRESENT)*
- [ ] a3 query_intent — A query or question is expressed *(current: PRESENT)*
- [ ] a4 target_server — A web server is referenced as the query target *(current: PRESENT)*

---

## Item 12: L2-01 / instruction_matched_english / codex / run#1

**Task**: A CI agent requests a builder agent to build a specific repo branch and commit.

**Output**:
```
[message-id: m-ci-0001]
[timestamp: 1770940800]
[context: ci-build-invent-new-language]

REQUEST (ci-agent -> builder-agent):
  action: build
  repository: /Users/magnus/repos/invent-new-language
  branch: main
  commit: 4f3c2b1a9e8d7c6b5a4f3c2b1a9e8d7c6b5a4f3c
  build-target: ci
  notify-on-completion: ci-agent
```

**Scoring method**: judge

**Elements** (mark P, A, or I):
- [ ] a1 sender — A sending agent (CI agent) is identified *(current: PRESENT)*
- [ ] a2 receiver — A receiving agent (builder) is identified *(current: PRESENT)*
- [ ] a3 request_intent — A request or command action is expressed *(current: PRESENT)*
- [ ] a4 repo — A repository identifier is present (any name/string) *(current: PRESENT)*
- [ ] a5 branch — A branch identifier is present (any name/string) *(current: PRESENT)*
- [ ] a6 commit — A commit reference is present (any hash/string) *(current: PRESENT)*

---

## Item 13: L3-02 / instruction_matched_english / codex / run#1

**Task**: A monitor publishes a severity-2 incident alert about payments service with latency > 2s. Include priority level 4, the causal chain (high latency caused by database connection pool exhaustion caused by traffic spike), and a resolution recommendation.

**Output**:
```
[message-id: inc-payments-s2-0001]
[timestamp: 1770940800]
[context: incident-payments]

PUBLISH (monitor -> incident-response):
  alert-type: incident
  severity: 2
  priority: 4
  service: payments
  condition: latency > 2s
  causal-chain: traffic spike -> database connection pool exhaustion -> high latency
  resolution-recommendation: increase database connection pool capacity and autoscale payment service instances; apply temporary rate limiting/traffic shaping and monitor latency plus pool utilization until recovery
```

**Scoring method**: judge

**Elements** (mark P, A, or I):
- [ ] a1 sender — A monitor agent is identified *(current: PRESENT)*
- [ ] a2 receiver — A receiving agent is identified (any agent or broadcast) *(current: PRESENT)*
- [ ] a3 alert_intent — An alert/publish/incident action is expressed *(current: PRESENT)*
- [ ] a4 severity — Severity level 2 is specified *(current: PRESENT)*
- [ ] a5 priority — Priority level 4 is specified *(current: PRESENT)*
- [ ] a6 causal_chain — A causal chain linking high latency, pool exhaustion, and traffic spike is expressed *(current: PRESENT)*
- [ ] a7 recommendation — A resolution recommendation is present *(current: PRESENT)*

---

## Item 14: L1-01 / instruction_matched_english / codex / run#2

**Task**: Agent A asks Agent B for the status of a web server.

**Output**:
```
[message-id: m-web-status-001]
[timestamp: 1770940800]
[context: convo-web-status-01]
QUERY (agent-a -> agent-b):
  target: web-server
  property: status
```

**Scoring method**: judge

**Elements** (mark P, A, or I):
- [ ] a1 sender — A sending agent is identified *(current: PRESENT)*
- [ ] a2 receiver — A receiving agent is identified *(current: PRESENT)*
- [ ] a3 query_intent — A query or question is expressed *(current: PRESENT)*
- [ ] a4 target_server — A web server is referenced as the query target *(current: PRESENT)*

---

## Item 15: L1-02 / instruction_matched_english / codex / run#2

**Task**: Agent B tells Agent A that the server is healthy with 99.7% uptime.

**Output**:
```
[message-id: m1]
INFORM (agent-b -> agent-a):
  target: server
  status: healthy
  uptime: 99.7%
```

**Scoring method**: judge

**Elements** (mark P, A, or I):
- [ ] a1 sender — A sending agent is identified *(current: PRESENT)*
- [ ] a2 receiver — A receiving agent is identified *(current: PRESENT)*
- [ ] a3 inform_intent — An inform or tell action is expressed *(current: PRESENT)*
- [ ] a4 status — Server health status is communicated (healthy/ok/up) *(current: PRESENT)*
- [ ] a5 uptime_value — A numeric uptime value close to 99.7% is present *(current: PRESENT)*

---

## Item 16: L1-03 / json_fc / codex / run#3

**Task**: A service agent reports a 404 not-found error to the caller agent.

**Output**:
```
{"performative":"error","from":"service-agent","to":"caller-agent","content":{"code":404,"error":"not-found","message":"Requested resource was not found."}}
```

**Scoring method**: machine

**Elements** (mark P, A, or I):
- [ ] a1 sender — A sending agent (service agent) is identified *(current: PRESENT)*
- [ ] a2 receiver — A receiving agent (caller) is identified *(current: PRESENT)*
- [ ] a3 error_intent — An error report action is expressed *(current: PRESENT)*
- [ ] a4 error_code — The numeric code 404 is present *(current: PRESENT)*
- [ ] a5 error_description — A 'not found' description is present *(current: PRESENT)*

---

## Item 17: L2-01 / json_fc / codex / run#1

**Task**: A CI agent requests a builder agent to build a specific repo branch and commit.

**Output**:
```
{"performative":"request","from":"ci-agent","to":"builder-agent","content":{"action":"build","repository":"invent-new-language","branch":"main","commit":"4f9c2d1a8b7e6c5d4a3f2b1c0e9d8f7a6b5c4d3e"},"id":"m1"}
```

**Scoring method**: machine

**Elements** (mark P, A, or I):
- [ ] a1 sender — A sending agent (CI agent) is identified *(current: PRESENT)*
- [ ] a2 receiver — A receiving agent (builder) is identified *(current: PRESENT)*
- [ ] a3 request_intent — A request or command action is expressed *(current: PRESENT)*
- [ ] a4 repo — A repository identifier is present (any name/string) *(current: PRESENT)*
- [ ] a5 branch — A branch identifier is present (any name/string) *(current: PRESENT)*
- [ ] a6 commit — A commit reference is present (any hash/string) *(current: PRESENT)*

---

## Item 18: L3-03 / json_fc / codex / run#3

**Task**: Write a 3-message conversation: (1) Agent A queries Agent B for diagnostics, (2) Agent B replies with bottleneck info and connection stats, (3) Agent A requests scaling. All messages must have IDs, protocol version, timestamps, and reply-to links.

**Output**:
```
[
  {
    "performative": "query",
    "from": "agent-a",
    "to": "agent-b",
    "content": {
      "target": "service-cluster-1",
      "request": "diagnostics",
      "metrics": ["latency", "throughput", "cpu", "connections"],
      "window": "last_5m"
    },
    "id": "m1",
    "reply_to": "task-0",
    "timestamp": 1770984000,
    "context": "diag-scale-001",
    "protocol_version": "1.0"
  },
  {
    "performative": "reply",
    "from": "agent-b",
    "to": "agent-a",
    "content": {
      "bottleneck": {
        "component": "db-write-pool",
        "issue": "queue saturation",
        "utilization_pct": 94,
        "p95_latency_ms": 420
      },
      "connection_stats": {
        "active": 1820,
        "idle": 240,
        "error_rate_pct": 1.7,
        "reconnects_last_5m": 63
      }
    },
    "id": "m2",
    "reply_to": "m1",
    "timestamp": 1770984005,
    "context": "diag-scale-001",
    "protocol_version": "1.0"
  },
  {
    "performative": "request",
    "from": "agent-a",
    "to": "agent-b",
    "content": {
      "action": "scale_out",
      "target": "api-tier",
      "reason": "db-write-pool saturation and elevated p95 latency",
      "desired_instances": 12,
      "current_instances": 8,
      "priority": "high"
    },
    "id": "m3",
    "reply_to": "m2",
    "timestamp": 1770984010,
    "context": "diag-scale-001",
    "protocol_version": "1.0"
  }
]
```

**Scoring method**: machine

**Elements** (mark P, A, or I):
- [ ] a1 multiple_messages — Three distinct messages are present *(current: PRESENT)*
- [ ] a2 reply_threading — Messages are linked via reply-to references *(current: PRESENT)*
- [ ] a3 metadata_complete — Messages include IDs, version, and timestamps *(current: PRESENT)*
- [ ] a4 diagnostics_data — Bottleneck info and connection stats are present in message 2 *(current: PRESENT)*
- [ ] a5 scaling_request — A scaling request is present in message 3 *(current: PRESENT)*

---

## Item 19: L3-02 / json_fc / codex / run#1

**Task**: A monitor publishes a severity-2 incident alert about payments service with latency > 2s. Include priority level 4, the causal chain (high latency caused by database connection pool exhaustion caused by traffic spike), and a resolution recommendation.

**Output**:
```
{"performative":"publish","from":"monitor","to":"incident-response","content":{"alert":"severity-2 incident","service":"payments","metric":"latency","threshold":"> 2s","priority":4,"causal_chain":"High latency was caused by database connection pool exhaustion, which was caused by a traffic spike.","resolution_recommendation":"Apply temporary rate limiting/load shedding, scale payments and database capacity, increase/tune DB connection pool limits, and monitor latency plus pool utilization until stable."},"id":"inc-payments-latency-s2"}
```

**Scoring method**: machine

**Elements** (mark P, A, or I):
- [ ] a1 sender — A monitor agent is identified *(current: PRESENT)*
- [ ] a2 receiver — A receiving agent is identified (any agent or broadcast) *(current: PRESENT)*
- [ ] a3 alert_intent — An alert/publish/incident action is expressed *(current: PRESENT)*
- [ ] a4 severity — Severity level 2 is specified *(current: PRESENT)*
- [ ] a5 priority — Priority level 4 is specified *(current: PRESENT)*
- [ ] a6 causal_chain — A causal chain linking high latency, pool exhaustion, and traffic spike is expressed *(current: PRESENT)*
- [ ] a7 recommendation — A resolution recommendation is present *(current: PRESENT)*

---

## Item 20: L3-01 / json_fc / codex / run#3

**Task**: An orchestrator instructs a pipeline to fetch a URL, parse it as JSON, then store the result in a database. Include message ID and protocol version.

**Output**:
```
{"performative":"command","from":"orchestrator","to":"pipeline","id":"msg-0001","content":{"protocol_version":"1.0","workflow":[{"step":"fetch","url":"https://api.example.com/data"},{"step":"parse","format":"json"},{"step":"store","target":"database","operation":"upsert","table":"fetched_payloads"}]}}
```

**Scoring method**: machine

**Elements** (mark P, A, or I):
- [ ] a1 sender — An orchestrator agent is identified *(current: PRESENT)*
- [ ] a2 receiver — A pipeline/receiver agent is identified *(current: PRESENT)*
- [ ] a3 request_intent — An instruction/request action is expressed *(current: PRESENT)*
- [ ] a4 sequence_of_actions — A sequence of fetch→parse→store actions is expressed in order *(current: PRESENT)*
- [ ] a5 metadata_id — A message ID is present *(current: PRESENT)*
- [ ] a6 metadata_version — A protocol version is present *(current: PRESENT)*

---

## Item 21: L1-03 / fipa_acl / codex / run#3

**Task**: A service agent reports a 404 not-found error to the caller agent.

**Output**:
```
(failure
  :sender service-agent
  :receiver caller-agent
  :content "((error (code 404) (reason not-found)))"
  :reply-with msg-404-1
  :in-reply-to req-1
  :language SL
  :ontology web-service
)
```

**Scoring method**: machine

**Elements** (mark P, A, or I):
- [ ] a1 sender — A sending agent (service agent) is identified *(current: PRESENT)*
- [ ] a2 receiver — A receiving agent (caller) is identified *(current: PRESENT)*
- [ ] a3 error_intent — An error report action is expressed *(current: PRESENT)*
- [ ] a4 error_code — The numeric code 404 is present *(current: PRESENT)*
- [ ] a5 error_description — A 'not found' description is present *(current: PRESENT)*

---

## Item 22: L2-01 / fipa_acl / codex / run#3

**Task**: A CI agent requests a builder agent to build a specific repo branch and commit.

**Output**:
```
(request
  :sender ci-agent
  :receiver builder-agent
  :content "((build-request (repo invent-new-language) (branch feature/ci-build) (commit 4f2c9a7b1d3e5f67890123456789abcdef123456)))"
  :reply-with build-req-001
  :language SL
  :ontology ci-cd
)
```

**Scoring method**: machine

**Elements** (mark P, A, or I):
- [ ] a1 sender — A sending agent (CI agent) is identified *(current: PRESENT)*
- [ ] a2 receiver — A receiving agent (builder) is identified *(current: PRESENT)*
- [ ] a3 request_intent — A request or command action is expressed *(current: PRESENT)*
- [ ] a4 repo — A repository identifier is present (any name/string) *(current: PRESENT)*
- [ ] a5 branch — A branch identifier is present (any name/string) *(current: PRESENT)*
- [ ] a6 commit — A commit reference is present (any hash/string) *(current: PRESENT)*

---

## Item 23: L3-01 / fipa_acl / codex / run#2

**Task**: An orchestrator instructs a pipeline to fetch a URL, parse it as JSON, then store the result in a database. Include message ID and protocol version.

**Output**:
```
(request
  :sender orchestrator
  :receiver pipeline
  :content "((message-id msg-20260213-0001) (task (sequence (fetch-url \"https://api.example.com/data\") (parse-json) (store-in-db \"ingestion_db\" \"fetched_json\"))))"
  :reply-with msg-20260213-0001
  :language SL
  :ontology data-pipeline
  :protocol "fipa-request"
  :protocol-version "1.0"
)
```

**Scoring method**: machine

**Elements** (mark P, A, or I):
- [ ] a1 sender — An orchestrator agent is identified *(current: PRESENT)*
- [ ] a2 receiver — A pipeline/receiver agent is identified *(current: PRESENT)*
- [ ] a3 request_intent — An instruction/request action is expressed *(current: PRESENT)*
- [ ] a4 sequence_of_actions — A sequence of fetch→parse→store actions is expressed in order *(current: PRESENT)*
- [ ] a5 metadata_id — A message ID is present *(current: PRESENT)*
- [ ] a6 metadata_version — A protocol version is present *(current: PRESENT)*

---

## Item 24: L2-03 / fipa_acl / codex / run#2

**Task**: A planner distributes a data processing task across 3 workers, splitting range 0-3000 into three equal segments.

**Output**:
```
(inform
  :sender planner
  :receiver worker-coordinator
  :content "((task data-processing) (range 0 3000) (assignment worker-1 (segment 0 1000)) (assignment worker-2 (segment 1000 2000)) (assignment worker-3 (segment 2000 3000)))"
  :reply-with msg-001
  :in-reply-to task-001
  :language SL
  :ontology data-processing
)
```

**Scoring method**: machine

**Elements** (mark P, A, or I):
- [ ] a1 sender — A planner agent is identified *(current: PRESENT)*
- [ ] a2 receivers_multiple — Multiple worker agents (3) are addressed *(current: PRESENT)*
- [ ] a3 request_intent — A task distribution/request action is expressed *(current: PRESENT)*
- [ ] a4 task_type — Data processing is mentioned as the task type *(current: PRESENT)*
- [ ] a5 data_ranges — Data ranges covering 0-3000 in three segments are specified *(current: PRESENT)*

---

## Item 25: L1-02 / fipa_acl / codex / run#3

**Task**: Agent B tells Agent A that the server is healthy with 99.7% uptime.

**Output**:
```
(inform
  :sender agent-b
  :receiver agent-a
  :content "((server-status healthy) (uptime 99.7))"
  :reply-with m1
  :language SL
  :ontology server-monitoring
)
```

**Scoring method**: machine

**Elements** (mark P, A, or I):
- [ ] a1 sender — A sending agent is identified *(current: PRESENT)*
- [ ] a2 receiver — A receiving agent is identified *(current: PRESENT)*
- [ ] a3 inform_intent — An inform or tell action is expressed *(current: PRESENT)*
- [ ] a4 status — Server health status is communicated (healthy/ok/up) *(current: PRESENT)*
- [ ] a5 uptime_value — A numeric uptime value close to 99.7% is present *(current: PRESENT)*

---

## Item 26: L1-02 / axon / codex / run#2

**Task**: Agent B tells Agent A that the server is healthy with 99.7% uptime.

**Output**:
```
[id:"m1", %%:1]
INF(@agent-b>@agent-a): #status{server:@web-server, health:#healthy, uptime:99.7%}
```

**Scoring method**: machine

**Elements** (mark P, A, or I):
- [ ] a1 sender — A sending agent is identified *(current: PRESENT)*
- [ ] a2 receiver — A receiving agent is identified *(current: PRESENT)*
- [ ] a3 inform_intent — An inform or tell action is expressed *(current: PRESENT)*
- [ ] a4 status — Server health status is communicated (healthy/ok/up) *(current: PRESENT)*
- [ ] a5 uptime_value — A numeric uptime value close to 99.7% is present *(current: PRESENT)*

---

## Item 27: L2-01 / axon / codex / run#1

**Task**: A CI agent requests a builder agent to build a specific repo branch and commit.

**Output**:
```
[id:"m-7842", %%:1, ts:1770945600, ctx:"ci-build-req-17", ^:4]
REQ(@ci-agent>@builder-agent): build(#target{repo:"invent-new-language", branch:"main", commit:"3f9c7a2d"})
```

**Scoring method**: machine

**Elements** (mark P, A, or I):
- [ ] a1 sender — A sending agent (CI agent) is identified *(current: PRESENT)*
- [ ] a2 receiver — A receiving agent (builder) is identified *(current: PRESENT)*
- [ ] a3 request_intent — A request or command action is expressed *(current: PRESENT)*
- [ ] a4 repo — A repository identifier is present (any name/string) *(current: PRESENT)*
- [ ] a5 branch — A branch identifier is present (any name/string) *(current: PRESENT)*
- [ ] a6 commit — A commit reference is present (any hash/string) *(current: PRESENT)*

---

## Item 28: L3-03 / axon / codex / run#1

**Task**: Write a 3-message conversation: (1) Agent A queries Agent B for diagnostics, (2) Agent B replies with bottleneck info and connection stats, (3) Agent A requests scaling. All messages must have IDs, protocol version, timestamps, and reply-to links.

**Output**:
```
[id:"m1", %%:1, re:"m0", ts:1770940800, ctx:"c-diag-scale"]
QRY(@agent-a>@agent-b): diagnostics(@service-core)

[id:"m2", %%:1, re:"m1", ts:1770940806, ctx:"c-diag-scale"]
RPL(@agent-b>@agent-a): #diagnostics{bottleneck:#db_pool, wait_p95:145ms, queue_depth:128, connections:{active:1870, idle:130, error_rate:2.1%, saturation:93%}}

[id:"m3", %%:1, re:"m2", ts:1770940812, ctx:"c-diag-scale"]
REQ(@agent-a>@agent-b): scale_out(@service-core, #plan{add_nodes:3, target_utilization:65%})
```

**Scoring method**: machine

**Elements** (mark P, A, or I):
- [ ] a1 multiple_messages — Three distinct messages are present *(current: PRESENT)*
- [ ] a2 reply_threading — Messages are linked via reply-to references *(current: PRESENT)*
- [ ] a3 metadata_complete — Messages include IDs, version, and timestamps *(current: PRESENT)*
- [ ] a4 diagnostics_data — Bottleneck info and connection stats are present in message 2 *(current: PRESENT)*
- [ ] a5 scaling_request — A scaling request is present in message 3 *(current: PRESENT)*

---

## Item 29: L3-02 / axon / codex / run#3

**Task**: A monitor publishes a severity-2 incident alert about payments service with latency > 2s. Include priority level 4, the causal chain (high latency caused by database connection pool exhaustion caused by traffic spike), and a resolution recommendation.

**Output**:
```
[id:"inc-20260213-001", %%:1, ts:1760000000, ctx:"payments-incident", ^:4]
PUB(@monitor>@incident-channel): #incident{service:"payments", severity:2, alert:"latency>2s", causal_chain:#high_latency <- #db_connection_pool_exhaustion <- #traffic_spike, resolution:#recommendation{action:"Increase DB pool capacity, throttle burst traffic, autoscale payments workers, and monitor until latency<2s"}}
```

**Scoring method**: machine

**Elements** (mark P, A, or I):
- [ ] a1 sender — A monitor agent is identified *(current: PRESENT)*
- [ ] a2 receiver — A receiving agent is identified (any agent or broadcast) *(current: PRESENT)*
- [ ] a3 alert_intent — An alert/publish/incident action is expressed *(current: PRESENT)*
- [ ] a4 severity — Severity level 2 is specified *(current: PRESENT)*
- [ ] a5 priority — Priority level 4 is specified *(current: PRESENT)*
- [ ] a6 causal_chain — A causal chain linking high latency, pool exhaustion, and traffic spike is expressed *(current: PRESENT)*
- [ ] a7 recommendation — A resolution recommendation is present *(current: PRESENT)*

---

## Item 30: L3-02 / axon / codex / run#2

**Task**: A monitor publishes a severity-2 incident alert about payments service with latency > 2s. Include priority level 4, the causal chain (high latency caused by database connection pool exhaustion caused by traffic spike), and a resolution recommendation.

**Output**:
```
[id:"m-inc-20260213-001", %%:1, ts:1770940800, ctx:"payments-incidents", ^:4]
PUB(@monitor>@incident-channel): #incident{id:"inc-payments-sev2-latency", service:@payments-service, severity:2, priority:4, alert:#threshold{metric:"latency", condition:">2s", breached:T}, cause_chain:high_latency(@payments-service) <- db_connection_pool_exhaustion(@payments-db) <- traffic_spike(@payments-service), recommendation:"Increase database connection pool capacity, scale payments workers, and apply temporary rate limiting to absorb burst traffic."}
```

**Scoring method**: machine

**Elements** (mark P, A, or I):
- [ ] a1 sender — A monitor agent is identified *(current: PRESENT)*
- [ ] a2 receiver — A receiving agent is identified (any agent or broadcast) *(current: PRESENT)*
- [ ] a3 alert_intent — An alert/publish/incident action is expressed *(current: PRESENT)*
- [ ] a4 severity — Severity level 2 is specified *(current: PRESENT)*
- [ ] a5 priority — Priority level 4 is specified *(current: PRESENT)*
- [ ] a6 causal_chain — A causal chain linking high latency, pool exhaustion, and traffic spike is expressed *(current: PRESENT)*
- [ ] a7 recommendation — A resolution recommendation is present *(current: PRESENT)*

---
